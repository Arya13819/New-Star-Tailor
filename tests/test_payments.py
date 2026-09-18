"""Phase 8: payments — partial, advance, verification, idempotency."""
from __future__ import annotations

from decimal import Decimal

from app.models.customer import Customer
from app.models.enums import (
    FabricSource,
    OrderPriority,
    PaymentMethod,
    PaymentStatus,
    ServiceCategory,
    UserRole,
)
from app.models.payment import Payment, PaymentEvent
from app.models.service import Service
from app.models.user import User
from app.services.order_service import create_order
from app.services.payment_service import (
    PaymentError,
    balance_for_order,
    paid_for_order,
    record_payment,
    verify_payment,
)


def _login_admin(client, db):
    u = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    u.set_password("supersecret1")
    db.session.add(u)
    db.session.commit()
    client.post("/admin/login", data={"identifier": "owner@example.com", "password": "supersecret1"})
    return u


def _order(db, *, fabric=FabricSource.CUSTOMER, price="1500.00", material="0"):
    c = Customer(name="Ramesh", mobile="9000000010")
    db.session.add(c)
    db.session.commit()
    s = Service(code="SVC", name_en="Service", category=ServiceCategory.SHIRT,
                default_stitching_price=Decimal(price))
    db.session.add(s)
    db.session.commit()
    return create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal(price), "material_price": Decimal(material)}],
        fabric_source=fabric, priority=OrderPriority.NORMAL, notes=None, actor_id=None,
    )


# --- business logic ---------------------------------------------------------


def test_partial_payments_accumulate_without_overwriting(app, db):
    order = _order(db)  # grand_total 1500, required_advance 750
    record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)

    assert Payment.query.filter_by(order_id=order.id).count() == 3
    assert paid_for_order(order.id) == Decimal("1500.00")
    assert balance_for_order(order) == Decimal("0.00")


def test_cash_and_upi_verified_immediately_online_pending(app, db):
    order = _order(db)
    cash = record_payment(order=order, amount=Decimal("100"), method=PaymentMethod.CASH,
                           transaction_reference=None, note=None, actor_id=None)
    upi = record_payment(order=order, amount=Decimal("100"), method=PaymentMethod.UPI,
                          transaction_reference="upi123", note=None, actor_id=None)
    online = record_payment(order=order, amount=Decimal("100"), method=PaymentMethod.ONLINE,
                             transaction_reference="pay_1", note=None, actor_id=None)

    assert cash.status == PaymentStatus.VERIFIED
    assert upi.status == PaymentStatus.VERIFIED
    assert online.status == PaymentStatus.PENDING
    # Pending online money doesn't count toward the paid/balance figures.
    assert paid_for_order(order.id) == Decimal("200.00")


def test_overpayment_is_rejected(app, db):
    order = _order(db, price="500.00")
    record_payment(order=order, amount=Decimal("400"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    try:
        record_payment(order=order, amount=Decimal("200"), method=PaymentMethod.CASH,
                        transaction_reference=None, note=None, actor_id=None)
        raised = False
    except PaymentError:
        raised = True
    assert raised
    assert paid_for_order(order.id) == Decimal("400.00")  # unchanged


def test_verifying_a_pending_payment_updates_advance_flag(app, db):
    order = _order(db, price="1000.00")  # required_advance 500
    online = record_payment(order=order, amount=Decimal("500"), method=PaymentMethod.ONLINE,
                             transaction_reference="pay_2", note=None, actor_id=None)
    assert order.advance_satisfied is False

    verify_payment(online, actor_id=None)
    assert online.status == PaymentStatus.VERIFIED
    assert order.advance_satisfied is True


def test_zero_or_negative_amount_rejected(app, db):
    order = _order(db)
    for bad in (Decimal("0"), Decimal("-10")):
        try:
            record_payment(order=order, amount=bad, method=PaymentMethod.CASH,
                            transaction_reference=None, note=None, actor_id=None)
            raised = False
        except PaymentError:
            raised = True
        assert raised


def test_shop_cloth_full_payment_satisfies_advance(app, db):
    order = _order(db, fabric=FabricSource.SHOP, price="850.00", material="1200.00")
    assert order.required_advance == Decimal("2050.00")
    record_payment(order=order, amount=Decimal("2050.00"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    assert order.advance_satisfied is True
    assert balance_for_order(order) == Decimal("0.00")


def test_payment_event_idempotency_constraint_still_holds(app, db):
    """Sanity check the Phase 2 guarantee this phase's webhook depends on."""
    from sqlalchemy.exc import IntegrityError

    db.session.add(PaymentEvent(provider="demo", event_id="evt_x"))
    db.session.commit()
    db.session.add(PaymentEvent(provider="demo", event_id="evt_x"))
    raised = False
    try:
        db.session.commit()
    except IntegrityError:
        raised = True
    db.session.rollback()
    assert raised


# --- HTTP --------------------------------------------------------------


def test_record_payment_via_http(client, db):
    _login_admin(client, db)
    order = _order(db, price="1000.00")
    resp = client.post(
        f"/admin/orders/{order.id}/payments",
        data={"amount": "500", "method": "CASH", "note": "advance"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Payment.query.filter_by(order_id=order.id).count() == 1


def test_verify_payment_via_http(client, db):
    _login_admin(client, db)
    order = _order(db, price="1000.00")
    client.post(f"/admin/orders/{order.id}/payments", data={"amount": "500", "method": "ONLINE"})
    payment = Payment.query.filter_by(order_id=order.id).one()
    assert payment.status == PaymentStatus.PENDING

    resp = client.post(f"/admin/payments/{payment.id}/verify", follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(payment)
    assert payment.status == PaymentStatus.VERIFIED


def test_payment_list_page_and_totals(client, db):
    _login_admin(client, db)
    order = _order(db, price="1000.00")
    client.post(f"/admin/orders/{order.id}/payments", data={"amount": "400", "method": "CASH"})
    client.post(f"/admin/orders/{order.id}/payments", data={"amount": "300", "method": "ONLINE"})

    resp = client.get("/admin/payments")
    assert resp.status_code == 200
    assert b"400.00" in resp.data


def test_webhook_is_honest_about_not_being_configured(client):
    resp = client.post("/api/payments/webhook")
    assert resp.status_code == 501
    assert b"not" in resp.data.lower() or b"No online payment provider" in resp.data


def test_non_admin_cannot_record_or_verify_payments(client, db):
    order = _order(db)
    cust = User(name="Ramesh", mobile="9352672795", role=UserRole.CUSTOMER)
    cust.set_password("supersecret1")
    db.session.add(cust)
    db.session.commit()
    client.post("/customer/login", data={"mobile": "9352672795", "password": "supersecret1"})

    resp = client.post(f"/admin/orders/{order.id}/payments", data={"amount": "100", "method": "CASH"})
    assert resp.status_code == 403
    assert client.get("/admin/payments").status_code == 403
