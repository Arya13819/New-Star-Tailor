"""Order creation and lifecycle business logic.

Stitching and material are always kept separate (master prompt §5). Material
only applies when the shop supplies the cloth — customer-cloth items are
force-zeroed here regardless of what a form submitted, so a stray value can
never sneak a material charge onto a customer-cloth order.
"""
from __future__ import annotations

from decimal import Decimal

from flask_babel import gettext as _

from ..extensions import db
from ..models.audit_log import AuditLog
from ..models.base import utcnow
from ..models.enums import FabricSource, OrderSource, OrderStatus
from ..models.order import Order, OrderItem
from ..utils.money import percent_of, to_money
from . import notification_service, numbering_service


class OrderError(ValueError):
    """Raised for a business-rule violation the UI should show as a message."""


def create_order(
    *,
    customer,
    items: list[dict],
    fabric_source: FabricSource,
    priority,
    requested_delivery_date=None,
    confirmed_delivery_date=None,
    notes: str | None,
    actor_id: int | None,
    source: OrderSource = OrderSource.SHOP,
    self_measurement_acknowledged: bool = False,
) -> Order:
    if not items:
        raise OrderError(_("Add at least one service to the order."))

    shop_cloth = fabric_source == FabricSource.SHOP
    current_version_id = (
        customer.measurement.current_version_id if customer.measurement else None
    )

    order_items: list[OrderItem] = []
    stitching_total = Decimal("0.00")
    material_total = Decimal("0.00")

    for raw in items:
        quantity = max(1, int(raw["quantity"]))
        stitching_price = to_money(raw["stitching_price"])
        if stitching_price <= 0:
            raise OrderError(_("Each item's stitching price must be greater than zero."))
        # Material is only ever charged when the shop provides the cloth.
        material_price = to_money(raw.get("material_price", 0)) if shop_cloth else Decimal("0.00")
        line_total = to_money((stitching_price + material_price) * quantity)

        stitching_total += stitching_price * quantity
        material_total += material_price * quantity

        order_items.append(
            OrderItem(
                service_id=raw.get("service_id"),
                service_name_snapshot=raw["service_name"],
                category_snapshot=raw["category"],
                stitching_price=stitching_price,
                material_price=material_price,
                quantity=quantity,
                line_total=line_total,
                measurement_version_id=current_version_id,
                notes=raw.get("notes") or None,
            )
        )

    stitching_total = to_money(stitching_total)
    material_total = to_money(material_total)
    grand_total = to_money(stitching_total + material_total)

    required_advance = (
        to_money(grand_total) if shop_cloth else percent_of(stitching_total, 50)
    )

    order_number, _seq = numbering_service.next_order_number()

    order = Order(
        order_number=order_number,
        customer_id=customer.id,
        status=OrderStatus.NEW,
        priority=priority,
        fabric_source=fabric_source,
        requested_delivery_date=requested_delivery_date,
        confirmed_delivery_date=confirmed_delivery_date,
        subtotal_stitching=stitching_total,
        subtotal_material=material_total,
        grand_total=grand_total,
        required_advance=required_advance,
        advance_satisfied=required_advance <= 0,
        notes=(notes or "").strip() or None,
        created_by_id=actor_id,
        confirmed_at=utcnow(),
        source=source,
        self_measurement_acknowledged=self_measurement_acknowledged,
        self_measurement_acknowledged_at=(utcnow() if self_measurement_acknowledged else None),
    )
    order.items = order_items
    db.session.add(order)
    db.session.flush()

    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="order",
            entity_id=order.id,
            action="create",
            to_value=order.order_number,
        )
    )
    notification_service.queue_notification(
        customer=customer,
        order=order,
        type_="ORDER_CONFIRMATION",
        body=f"Namaste {customer.name}, your order {order.order_number} has been "
        f"received at New Star Tailor. Total: Rs. {grand_total}.",
    )
    db.session.commit()
    return order


def update_status(order: Order, new_status: OrderStatus, *, actor_id: int | None) -> Order:
    before = order.status
    order.status = new_status
    if new_status == OrderStatus.DELIVERED:
        order.delivered_at = utcnow()
    elif order.delivered_at is not None:
        order.delivered_at = None  # moved back out of DELIVERED

    if new_status == OrderStatus.READY and before != OrderStatus.READY:
        notification_service.queue_notification(
            customer=order.customer,
            order=order,
            type_="ORDER_READY",
            body=f"Namaste {order.customer.name}, your order {order.order_number} "
            f"is ready for pickup at New Star Tailor.",
        )

    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="order",
            entity_id=order.id,
            action="status_change",
            from_value=before.value,
            to_value=new_status.value,
        )
    )
    db.session.commit()
    return order


def update_details(
    order: Order,
    *,
    priority=None,
    confirmed_delivery_date=None,
    notes=None,
    actor_id: int | None,
) -> Order:
    if priority is not None:
        order.priority = priority
    if confirmed_delivery_date is not None:
        order.confirmed_delivery_date = confirmed_delivery_date
    if notes is not None:
        order.notes = notes.strip() or None
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="order",
            entity_id=order.id,
            action="update_details",
        )
    )
    db.session.commit()
    return order
