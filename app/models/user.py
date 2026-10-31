"""Application user accounts (admin operators and customer logins)."""
from __future__ import annotations

from datetime import datetime

import bcrypt
from flask_login import UserMixin

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa
from .enums import UserRole


class User(PkMixin, TimestampMixin, UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        sa.UniqueConstraint("mobile", name="uq_users_mobile"),
        TABLE_ARGS,
    )

    name: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    # Customers log in with mobile; admins may use either. Unique when present
    # so a mobile number unambiguously identifies one login account (distinct
    # from customers.mobile, which is deliberately NOT unique).
    mobile: Mapped[str | None] = mapped_column(sa.String(20))
    email: Mapped[str | None] = mapped_column(sa.String(190), unique=True)

    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, native_enum=False, length=20),
        nullable=False,
        default=UserRole.CUSTOMER,
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime)
    # Persisted (not just session) so a customer's SMS notifications are
    # sent in their chosen language even when queued outside their own
    # request — an admin marking an order READY, or the reminders CLI cron.
    # NULL/"en" both mean "no Hindi preference recorded" (see notification_service).
    preferred_locale: Mapped[str | None] = mapped_column(sa.String(5))

    customers = db.relationship("Customer", back_populates="user", lazy="selectin")

    # --- password helpers ---
    def set_password(self, raw: str) -> None:
        self.password_hash = bcrypt.hashpw(
            raw.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, raw: str) -> bool:
        if not self.password_hash:
            return False
        try:
            return bcrypt.checkpw(
                raw.encode("utf-8"), self.password_hash.encode("utf-8")
            )
        except ValueError:
            return False

    # --- Flask-Login ---
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def get_id(self) -> str:  # noqa: D401
        return str(self.id)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.id} {self.role} {self.name!r}>"
