"""Shop reports (master prompt §39). Revenue is always verified payments
only — a pending or failed payment never counts as collected money."""
from __future__ import annotations

from decimal import Decimal

from ..models.enums import OrderStatus, PaymentStatus, ServiceCategory
from ..models.order import Order, OrderItem
from ..models.payment import Payment
from ..utils.money import money_sum


def summary(start, end) -> dict:
    orders_in_range = Order.query.filter(
        Order.created_at >= start, Order.created_at < end
    ).all()
    total_orders = len(orders_in_range)

    by_status = {s.value: 0 for s in OrderStatus}
    for o in orders_in_range:
        by_status[o.status.value] += 1

    order_ids = [o.id for o in orders_in_range]
    items = (
        OrderItem.query.filter(OrderItem.order_id.in_(order_ids)).all()
        if order_ids
        else []
    )
    category_order_ids: dict[str, set[int]] = {c.value: set() for c in ServiceCategory}
    category_amount: dict[str, Decimal] = {c.value: Decimal("0.00") for c in ServiceCategory}
    for it in items:
        cat = it.category_snapshot.value
        category_order_ids[cat].add(it.order_id)
        category_amount[cat] += it.line_total

    category_breakdown = [
        {
            "category": cat,
            "order_count": len(category_order_ids[cat]),
            "amount": money_sum([category_amount[cat]]),
        }
        for cat in category_order_ids
    ]

    verified_payments = Payment.query.filter(
        Payment.status == PaymentStatus.VERIFIED,
        Payment.verified_at >= start,
        Payment.verified_at < end,
    ).all()
    total_revenue = money_sum(p.amount for p in verified_payments)

    return {
        "window": {"start": start, "end": end},
        "total_orders": total_orders,
        "by_status": by_status,
        "delivered_orders": by_status[OrderStatus.DELIVERED.value],
        "pending_orders": total_orders - by_status[OrderStatus.DELIVERED.value],
        "category_breakdown": category_breakdown,
        "total_revenue": total_revenue,
    }


def pending_payments(limit: int = 20) -> dict:
    """Current outstanding balances — not date-ranged, this is a snapshot
    of "who owes what right now"."""
    from . import payment_service

    all_orders = Order.query.all()
    with_balance = [
        (o, payment_service.balance_for_order(o))
        for o in all_orders
    ]
    with_balance = [(o, bal) for o, bal in with_balance if bal > 0]
    with_balance.sort(key=lambda pair: pair[1], reverse=True)
    total_outstanding = money_sum(bal for _o, bal in with_balance)
    return {
        "rows": with_balance[:limit],
        "count": len(with_balance),
        "total": total_outstanding,
    }
