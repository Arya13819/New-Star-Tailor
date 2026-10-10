"""Phase 14: reports — real data only, revenue = verified payments."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from app.models.customer import Customer
from app.models.enums import FabricSource, OrderPriority, PaymentMethod, ServiceCategory, UserRole
from app.models.service import Service
from app.models.user import User
from app.services.order_service import create_order
from app.services.payment_service import record_payment
from app.services.report_service import pending_payments, summary


def _login_admin(client, db):
    u = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    u.set_password("supersecret1")
    db.session.add(u)
    db.session.commit()
    client.post("/admin/login", data={"identifier": "owner@example.com", "password": "supersecret1"})
    return u


_counter = iter(range(1, 10_000))


def _order(db, category=ServiceCategory.POLICE, price="700.00"):
    c = Customer(name="Ramesh", mobile="9000000010")
    db.session.add(c)
    db.session.commit()
    s = Service(code=f"SVC_{category.value}_{next(_counter)}", name_en="Service", category=category,
                default_stitching_price=Decimal(price))
    db.session.add(s)
    db.session.commit()
    return create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal(price)}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )


def test_summary_counts_orders_and_category(app, db):
    from app.models.base import utcnow

    order = _order(db, category=ServiceCategory.POLICE, price="700.00")
    now = utcnow()
    data = summary(now - timedelta(hours=1), now + timedelta(hours=1))
    assert data["total_orders"] == 1
    police = next(c for c in data["category_breakdown"] if c["category"] == "POLICE")
    assert police["order_count"] == 1
    assert police["amount"] == Decimal("700.00")
    assert order.status.value in data["by_status"]


def test_summary_revenue_only_counts_verified_payments(app, db):
    from app.models.base import utcnow

    order = _order(db, price="1000.00")
    record_payment(order=order, amount=Decimal("400"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    record_payment(order=order, amount=Decimal("300"), method=PaymentMethod.ONLINE,
                    transaction_reference=None, note=None, actor_id=None)  # PENDING

    now = utcnow()
    data = summary(now - timedelta(hours=1), now + timedelta(hours=1))
    assert data["total_revenue"] == Decimal("400.00")  # not 700


def test_summary_excludes_orders_outside_the_window(app, db):
    from app.extensions import db as _db
    from app.models.base import utcnow
    from app.models.order import Order

    order = _order(db)
    order.created_at = utcnow() - timedelta(days=40)
    _db.session.commit()

    now = utcnow()
    data = summary(now - timedelta(days=1), now)
    assert data["total_orders"] == 0
    assert Order.query.count() == 1  # still exists, just outside the window


def test_pending_payments_lists_outstanding_orders_only(app, db):
    paid = _order(db, price="500.00")
    record_payment(order=paid, amount=Decimal("500"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    unpaid = _order(db, price="700.00")

    result = pending_payments()
    order_ids = {o.id for o, _bal in result["rows"]}
    assert unpaid.id in order_ids
    assert paid.id not in order_ids
    assert result["total"] == Decimal("700.00")


def test_reports_page_requires_admin(client):
    resp = client.get("/admin/reports")
    assert resp.status_code == 302


def test_reports_page_renders_with_data(client, db):
    _login_admin(client, db)
    order = _order(db, price="700.00")
    record_payment(order=order, amount=Decimal("350"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)

    resp = client.get("/admin/reports?range=today")
    assert resp.status_code == 200
    assert b"350.00" in resp.data


def test_reports_page_shows_crpf_not_title_cased(client, db):
    _login_admin(client, db)
    _order(db, category=ServiceCategory.CRPF, price="700.00")

    resp = client.get("/admin/reports?range=today")
    assert resp.status_code == 200
    assert b"CRPF" in resp.data
    assert b"Crpf" not in resp.data


def test_reports_custom_range(client, db):
    _login_admin(client, db)
    from datetime import date

    today = date.today().isoformat()
    resp = client.get(f"/admin/reports?range=custom&from={today}&to={today}")
    assert resp.status_code == 200
