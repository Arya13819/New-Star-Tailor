"""Customer-uploaded reference images for an order."""
from __future__ import annotations

from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, db, mapped_column, sa, utcnow


class ReferenceImage(PkMixin, db.Model):
    __tablename__ = "reference_images"
    __table_args__ = TABLE_ARGS

    order_id: Mapped[int] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(sa.String(60), nullable=False)
    file_size: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    uploaded_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow
    )

    order = db.relationship("Order", back_populates="reference_images")
    uploaded_by = db.relationship("User")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ReferenceImage order={self.order_id} {self.file_name!r}>"
