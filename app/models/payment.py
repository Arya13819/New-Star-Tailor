"""Payments and payment-provider webhook events."""
from __future__ import annotations

from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa, utcnow
from .enums import PaymentMethod, PaymentStatus

_MONEY = sa.Numeric(10, 2, asdecimal=True)


class Payment(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "payments"
    __table_args__ = TABLE_ARGS

    order_id: Mapped[int] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(_MONEY, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        sa.Enum(PaymentMethod, native_enum=False, length=10), nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        sa.Enum(PaymentStatus, native_enum=False, length=10),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(sa.String(40))
    transaction_reference: Mapped[str | None] = mapped_column(sa.String(190))
    note: Mapped[str | None] = mapped_column(sa.String(300))

    recorded_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    verified_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    verified_at: Mapped[datetime | None] = mapped_column(sa.DateTime)

    order = db.relationship("Order", back_populates="payments")
    customer = db.relationship("Customer", back_populates="payments")
    recorded_by = db.relationship("User", foreign_keys=[recorded_by_id])
    verified_by = db.relationship("User", foreign_keys=[verified_by_id])

    @property
    def is_verified(self) -> bool:
        return self.status == PaymentStatus.VERIFIED

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Payment order={self.order_id} {self.amount} {self.method} {self.status}>"


class PaymentEvent(PkMixin, db.Model):
    """Webhook idempotency ledger. ``UNIQUE(provider, event_id)`` guarantees a
    duplicate webhook can never create a duplicate payment."""

    __tablename__ = "payment_events"
    __table_args__ = (
        sa.UniqueConstraint("provider", "event_id", name="uq_payment_event"),
        TABLE_ARGS,
    )

    provider: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    event_id: Mapped[str] = mapped_column(sa.String(190), nullable=False)
    event_type: Mapped[str | None] = mapped_column(sa.String(80))
    payload_hash: Mapped[str | None] = mapped_column(sa.String(64))
    raw_payload: Mapped[str | None] = mapped_column(sa.Text)

    payment_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("payments.id", ondelete="SET NULL")
    )
    order_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="SET NULL")
    )
    processed_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PaymentEvent {self.provider}:{self.event_id}>"
