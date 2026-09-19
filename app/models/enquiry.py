"""Quick public enquiries (master prompt §14 Option A) — no order, no login,
just a message for staff to follow up on."""
from __future__ import annotations

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

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Enquiry {self.id} {self.name!r} {self.status}>"
