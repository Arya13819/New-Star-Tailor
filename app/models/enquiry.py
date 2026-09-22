"""Quick public enquiries (master prompt §14 Option A) — no order, no login,
just a message for staff to follow up on."""
from __future__ import annotations

from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa
from .enums import EnquiryStatus


class Enquiry(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "enquiries"
    __table_args__ = TABLE_ARGS

    name: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    mobile: Mapped[str] = mapped_column(sa.String(20), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(sa.String(400))
    message: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[EnquiryStatus] = mapped_column(
        sa.Enum(EnquiryStatus, native_enum=False, length=12),
        nullable=False,
        default=EnquiryStatus.NEW,
        index=True,
    )

    # Set only once an admin actually turns this enquiry into a real order
    # (never manually chosen from the status dropdown — see enquiry_service
    # .convert_to_order). Until then the enquiry has no order at all, so it
    # can never show up mixed into the confirmed-orders list.
    converted_order_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    converted_at: Mapped[datetime | None] = mapped_column(sa.DateTime)

    order = db.relationship("Order")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Enquiry {self.id} {self.name!r} {self.status}>"
