"""Order data access."""
from __future__ import annotations

import re
from datetime import date

from flask import abort
from sqlalchemy import or_

from ..extensions import db
from ..models.customer import Customer
from ..models.enums import OrderPriority, OrderStatus
from ..models.order import Order

# Dashboard "still open" shortcut cards (urgent/today/overdue) — matches the
# same open-order definition used to build those counts on the dashboard.
VIEWS = {"urgent", "today", "overdue"}


def search(
    status: str | None,
    term: str | None,
    *,
    view: str | None = None,
    page: int = 1,
    per_page: int = 20,
):
    query = Order.query.join(Customer, Order.customer_id == Customer.id)

    if view in VIEWS:
        query = query.filter(Order.status != OrderStatus.DELIVERED)
        if view == "urgent":
            query = query.filter(Order.priority == OrderPriority.URGENT)
        elif view == "today":
            query = query.filter(Order.confirmed_delivery_date == date.today())
        elif view == "overdue":
            query = query.filter(Order.confirmed_delivery_date < date.today())
    elif status and status in OrderStatus.__members__:
        query = query.filter(Order.status == OrderStatus[status])

    term = (term or "").strip()
    if term:
        digits = re.sub(r"\D", "", term)
        clauses = [Order.order_number.ilike(f"%{term}%"), Customer.name.ilike(f"%{term}%")]
        if digits:
            clauses.append(Customer.mobile.contains(digits))
        query = query.filter(or_(*clauses))

    query = query.order_by(Order.created_at.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def counts_by_status() -> dict[str, int]:
    rows = db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
    counts = {s.value: 0 for s in OrderStatus}
    for status, count in rows:
        counts[status.value] = count
    counts["TOTAL"] = sum(counts.values())
    return counts


def get_or_404(order_id: int) -> Order:
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)
    return order
