"""Service catalogue. Prices are configurable and snapshotted onto orders."""
from __future__ import annotations

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa
from .enums import ServiceCategory


class Service(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "services"
    __table_args__ = TABLE_ARGS

    code: Mapped[str] = mapped_column(sa.String(40), nullable=False, unique=True)
    name_en: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    name_hi: Mapped[str | None] = mapped_column(sa.String(120))
    category: Mapped[ServiceCategory] = mapped_column(
        sa.Enum(ServiceCategory, native_enum=False, length=12), nullable=False
    )

    # NULL means "price not set yet" — the owner must enter it before the
    # service can be used on an order.
    default_stitching_price: Mapped[float | None] = mapped_column(
        sa.Numeric(10, 2, asdecimal=True)
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=100)
    description: Mapped[str | None] = mapped_column(sa.String(300))

    @property
    def price_is_set(self) -> bool:
        return self.default_stitching_price is not None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Service {self.code} {self.category}>"
