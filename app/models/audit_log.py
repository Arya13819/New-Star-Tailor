"""Lightweight audit trail for status and payment changes (master prompt §69)."""
from __future__ import annotations

from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, db, mapped_column, sa, utcnow


class AuditLog(PkMixin, db.Model):
    __tablename__ = "audit_logs"
    __table_args__ = TABLE_ARGS

    actor_user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    entity_type: Mapped[str] = mapped_column(sa.String(40), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, index=True)
    action: Mapped[str] = mapped_column(sa.String(60), nullable=False)
    from_value: Mapped[str | None] = mapped_column(sa.String(255))
    to_value: Mapped[str | None] = mapped_column(sa.String(255))
    detail: Mapped[str | None] = mapped_column(sa.Text)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow, index=True
    )

    actor = db.relationship("User")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuditLog {self.entity_type}#{self.entity_id} {self.action}>"
