"""Admin dashboard (Phase 9): the morning-overview page (master prompt §40)."""
from __future__ import annotations

from datetime import date

from flask import render_template, request
from flask_login import current_user

from ...models.enums import OrderPriority, OrderStatus
from ...models.order import Order
from ...repositories import customer_repo, order_repo
from ...services import payment_service
from ...utils.security import admin_required
from . import bp


@bp.get("/dashboard")
@admin_required
def dashboard():
    counts = order_repo.counts_by_status()
    today = date.today()

    open_orders = (
        Order.query.filter(Order.status != OrderStatus.DELIVERED)
        .order_by(Order.confirmed_delivery_date.is_(None), Order.confirmed_delivery_date)
        .all()
    )

    todays_deliveries = [
        o for o in open_orders if o.confirmed_delivery_date == today
    ]
    overdue = [
        o
        for o in open_orders
        if (o.confirmed_delivery_date or o.requested_delivery_date)
        and (o.confirmed_delivery_date or o.requested_delivery_date) < today
    ]
    urgent_open = [o for o in open_orders if o.priority == OrderPriority.URGENT]

    all_orders = Order.query.all()
    with_balance = [
        (o, payment_service.balance_for_order(o))
        for o in all_orders
        if payment_service.balance_for_order(o) > 0
    ]
    with_balance.sort(key=lambda pair: pair[1], reverse=True)
    outstanding_total = sum((bal for _o, bal in with_balance), start=0)

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    return render_template(
        "admin/dashboard.html",
        user=current_user,
        counts=counts,
        todays_deliveries=todays_deliveries,
        overdue=overdue,
        urgent_open=urgent_open,
        pending_payments=with_balance[:8],
        pending_payments_count=len(with_balance),
        outstanding_total=outstanding_total,
        recent_orders=recent_orders,
    )


@bp.get("/search")
@admin_required
def global_search():
    term = request.args.get("q", "").strip()
    customers = customer_repo.search(term).items if term else []
    orders = order_repo.search(None, term).items if term else []
    return render_template(
        "admin/search.html", term=term, customers=customers, orders=orders
    )
