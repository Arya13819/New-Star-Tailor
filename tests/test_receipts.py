"""Phase 12: printable order and payment receipts."""
from __future__ import annotations

from decimal import Decimal

from app.models.customer import Customer
from app.models.enums import FabricSource, OrderPriority, PaymentMethod, ServiceCategory, UserRole
from app.models.service import Service
from app.models.user import User
from app.services.order_service import create_order
from app.services.payment_service import record_payment


def _login_admin(client, db):
    u = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    u.set_password("supersecret1")
    db.session.add(u)
    db.session.commit()
    client.post("/admin/login", data={"identifier": "owner@example.com", "password": "supersecret1"})
    return u


def _order(db, price="1900.00", material="1200.00", fabric=FabricSource.SHOP):
    c = Customer(name="Ramesh Prajapat", mobile="9000000010")
    db.session.add(c)
    db.session.commit()
    s = Service(code="CHEETAH_US", name_en="Cheetah US Pattern", category=ServiceCategory.ARMY,
                default_stitching_price=Decimal("850.00"))
    db.session.add(s)
    db.session.commit()
    return create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("850.00"), "material_price": Decimal(material)}],
        fabric_source=fabric, priority=OrderPriority.NORMAL, notes=None, actor_id=None,
    )


def test_order_receipt_requires_admin(client, db):
    order = _order(db)
    resp = client.get(f"/admin/orders/{order.id}/receipt")
    assert resp.status_code == 302


def test_order_receipt_shows_shop_header_and_totals(client, db):
    _login_admin(client, db)
    order = _order(db)
    resp = client.get(f"/admin/orders/{order.id}/receipt")
    assert resp.status_code == 200
    assert b"New Star Tailor" in resp.data
    assert order.order_number.encode() in resp.data
    assert b"Ramesh Prajapat" in resp.data
    assert b"2,050.00" in resp.data or b"2050.00" in resp.data


def test_order_receipt_reflects_partial_payment(client, db):
    _login_admin(client, db)
    order = _order(db)
    record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    resp = client.get(f"/admin/orders/{order.id}/receipt")
    assert b"500.00" in resp.data
    assert b"1,550.00" in resp.data or b"1550.00" in resp.data  # remaining balance


def test_customer_can_print_own_receipt_but_not_anothers(client, db):
    order = _order(db)
    other = Customer(name="Someone Else", mobile="9333333331")
    db.session.add(other)
    db.session.commit()

    # Register the "other" customer's portal login.
    client.post(
        "/customer/register",
        data={"name": "Someone Else", "mobile": "9333333331",
              "password": "supersecret1", "confirm_password": "supersecret1"},
    )
    resp = client.get(f"/customer/orders/{order.id}/receipt")
    assert resp.status_code == 404


def test_payment_receipt_requires_admin(client, db):
    order = _order(db)
    payment = record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.CASH,
                              transaction_reference=None, note=None, actor_id=None)
    resp = client.get(f"/admin/payments/{payment.id}/receipt")
    assert resp.status_code == 302


def test_payment_receipt_shows_amount_and_balance(client, db):
    _login_admin(client, db)
    order = _order(db)
    payment = record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.CASH,
                              transaction_reference="TXN123", note=None, actor_id=None)
    resp = client.get(f"/admin/payments/{payment.id}/receipt")
    assert resp.status_code == 200
    assert b"500.00" in resp.data
    assert b"TXN123" in resp.data
    assert order.order_number.encode() in resp.data
