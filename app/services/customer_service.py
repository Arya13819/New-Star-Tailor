"""Customer create/update business logic + audit trail."""
from __future__ import annotations

from ..extensions import db
from ..models.audit_log import AuditLog
from ..models.customer import Customer
from ..utils.security import normalise_mobile


def create_customer(*, name: str, mobile: str, address: str | None, notes: str | None, actor_id: int | None) -> Customer:
    customer = Customer(
        name=name.strip(),
        mobile=normalise_mobile(mobile),
        address=(address or "").strip() or None,
        notes=(notes or "").strip() or None,
    )
    db.session.add(customer)
    db.session.flush()
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="customer",
            entity_id=customer.id,
            action="create",
            to_value=customer.name,
        )
    )
    db.session.commit()
    return customer


def update_customer(customer: Customer, *, name: str, mobile: str, address: str | None, notes: str | None, actor_id: int | None) -> Customer:
    before = f"{customer.name} / {customer.mobile}"
    customer.name = name.strip()
    customer.mobile = normalise_mobile(mobile)
    customer.address = (address or "").strip() or None
    customer.notes = (notes or "").strip() or None
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="customer",
            entity_id=customer.id,
            action="update",
            from_value=before,
            to_value=f"{customer.name} / {customer.mobile}",
        )
    )
    db.session.commit()
    return customer
