"""Customer data access."""
from __future__ import annotations

import re

from flask import abort
from sqlalchemy import or_

from ..extensions import db
from ..models.customer import Customer


def search(term: str | None, page: int = 1, per_page: int = 20):
    query = Customer.query.filter(Customer.is_active.is_(True))
    term = (term or "").strip()
    if term:
        digits = re.sub(r"\D", "", term)
        if digits:
            query = query.filter(
                or_(Customer.mobile.contains(digits), Customer.name.ilike(f"%{term}%"))
            )
        else:
            query = query.filter(Customer.name.ilike(f"%{term}%"))
    query = query.order_by(Customer.created_at.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def find_by_mobile(mobile: str) -> list[Customer]:
    return (
        Customer.query.filter(Customer.mobile == mobile, Customer.is_active.is_(True))
        .order_by(Customer.name)
        .all()
    )


def get_or_404(customer_id: int) -> Customer:
    customer = db.session.get(Customer, customer_id)
    if customer is None or not customer.is_active:
        abort(404)
    return customer
