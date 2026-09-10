"""Customer profiles (people we take measurements for).

Mobile is deliberately **not unique** — family members often share one number
but each is a distinct profile with their own measurements.
"""
from __future__ import annotations

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa


class Customer(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "customers"
    __table_args__ = TABLE_ARGS

    name: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    mobile: Mapped[str] = mapped_column(sa.String(20), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(sa.String(400))
    notes: Mapped[str | None] = mapped_column(sa.Text)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    # Optional link to a login account. NULL for walk-ins created by the admin.
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    user = db.relationship("User", back_populates="customers")

    measurement = db.relationship(
        "Measurement",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan",
    )
    orders = db.relationship("Order", back_populates="customer", lazy="selectin")
    payments = db.relationship("Payment", back_populates="customer", lazy="selectin")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Customer {self.id} {self.name!r} {self.mobile}>"
