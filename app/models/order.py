"""Orders and order items.

Money columns are ``DECIMAL(10,2)``. Item prices are *snapshots*: changing a
service price later never rewrites an existing order.
"""
from __future__ import annotations

from datetime import date, datetime

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa
from .enums import (
    FabricSource,
    OrderPriority,
    OrderSource,
    OrderStatus,
    ServiceCategory,
)

_MONEY = sa.Numeric(10, 2, asdecimal=True)


class Order(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "orders"
    __table_args__ = TABLE_ARGS

    # Assigned server-side when the order is confirmed. NULL for drafts.
    order_number: Mapped[str | None] = mapped_column(sa.String(20), unique=True)

    customer_id: Mapped[int] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    source: Mapped[OrderSource] = mapped_column(
        sa.Enum(OrderSource, native_enum=False, length=10),
        nullable=False,
        default=OrderSource.SHOP,
    )
    status: Mapped[OrderStatus] = mapped_column(
        sa.Enum(OrderStatus, native_enum=False, length=12),
        nullable=False,
        default=OrderStatus.NEW,
        index=True,
    )
    priority: Mapped[OrderPriority] = mapped_column(
        sa.Enum(OrderPriority, native_enum=False, length=10),
        nullable=False,
        default=OrderPriority.NORMAL,
    )
    fabric_source: Mapped[FabricSource] = mapped_column(
        sa.Enum(FabricSource, native_enum=False, length=10), nullable=False
    )

    requested_delivery_date: Mapped[date | None] = mapped_column(sa.Date)
    confirmed_delivery_date: Mapped[date | None] = mapped_column(sa.Date)

    # Roll-up snapshots (kept in sync by the order service).
    subtotal_stitching: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)
    subtotal_material: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)
    grand_total: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)
    required_advance: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)

    # Cached flag (source of truth is the sum of verified payments). Recomputed
    # whenever a payment is verified/removed.
    advance_satisfied: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )

    self_measurement_acknowledged: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )
    self_measurement_acknowledged_at: Mapped[datetime | None] = mapped_column(sa.DateTime)

    notes: Mapped[str | None] = mapped_column(sa.Text)
    created_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(sa.DateTime)
    delivered_at: Mapped[datetime | None] = mapped_column(sa.DateTime)

    customer = db.relationship("Customer", back_populates="orders")
    created_by = db.relationship("User")
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderItem.id",
        lazy="selectin",
    )
    payments = db.relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="Payment.created_at",
        lazy="selectin",
    )
    reference_images = db.relationship(
        "ReferenceImage", back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def is_confirmed(self) -> bool:
        return self.order_number is not None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order {self.order_number or 'draft'} {self.status}>"


class OrderItem(PkMixin, db.Model):
    __tablename__ = "order_items"
    __table_args__ = TABLE_ARGS

    order_id: Mapped[int] = mapped_column(
        sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("services.id", ondelete="SET NULL")
    )

    # Snapshots — never follow the live Service row.
    service_name_snapshot: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    category_snapshot: Mapped[ServiceCategory] = mapped_column(
        sa.Enum(ServiceCategory, native_enum=False, length=12), nullable=False
    )
    stitching_price: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)
    material_price: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    line_total: Mapped[float] = mapped_column(_MONEY, nullable=False, default=0)

    measurement_version_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("measurement_versions.id", ondelete="SET NULL")
    )
    notes: Mapped[str | None] = mapped_column(sa.Text)

    order = db.relationship("Order", back_populates="items")
    service = db.relationship("Service")
    measurement_version = db.relationship("MeasurementVersion")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OrderItem {self.service_name_snapshot} x{self.quantity}>"


class OrderSequence(db.Model):
    """Single-row counter for atomic ``NST-000001`` generation.

    The numbering service takes a ``SELECT ... FOR UPDATE`` on this row inside
    the order-creation transaction.
    """

    __tablename__ = "order_sequences"
    __table_args__ = TABLE_ARGS

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    last_seq: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
