"""Outbound customer notifications (plain SMS — never WhatsApp; email possible).

Phase 2 only defines the record. Scheduling and dispatch arrive in Phase 13.
Nothing is ever marked SENT unless a provider confirmed delivery.
"""
from __future__ import annotations

from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, db, mapped_column, sa, utcnow
from .enums import NotificationChannel, NotificationStatus, NotificationType


class Notification(PkMixin, db.Model):
    __tablename__ = "notifications"
    __table_args__ = TABLE_ARGS

    customer_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )
    order_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )

    channel: Mapped[NotificationChannel] = mapped_column(
        sa.Enum(NotificationChannel, native_enum=False, length=10),
        nullable=False,
        default=NotificationChannel.SMS,
    )
    type: Mapped[NotificationType] = mapped_column(
        sa.Enum(NotificationType, native_enum=False, length=24), nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        sa.Enum(NotificationStatus, native_enum=False, length=12),
        nullable=False,
        default=NotificationStatus.SCHEDULED,
        index=True,
    )

    # Prevents duplicate reminders, e.g. "PAYMENT_REMINDER:order=12:round=1".
    dedupe_key: Mapped[str | None] = mapped_column(sa.String(190), unique=True)

    to_address: Mapped[str | None] = mapped_column(sa.String(190))
    body: Mapped[str | None] = mapped_column(sa.Text)
    payload_json: Mapped[str | None] = mapped_column(sa.Text)

    scheduled_at: Mapped[datetime | None] = mapped_column(sa.DateTime, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(sa.DateTime)
    provider_message_id: Mapped[str | None] = mapped_column(sa.String(190))
    error_message: Mapped[str | None] = mapped_column(sa.String(500))

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow
    )

    customer = db.relationship("Customer")
    order = db.relationship("Order")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Notification {self.type} {self.status} order={self.order_id}>"
