"""Phase 9: admin dashboard and global search."""
from __future__ import annotations

from datetime import date, timedelta
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


def _service(db):
    s = Service(code="SVC", name_en="Service", category=ServiceCategory.SHIRT,
                default_stitching_price=Decimal("550.00"))
    db.session.add(s)
    db.session.commit()
    return s


def test_dashboard_requires_admin(client):
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 302


def test_dashboard_empty_state(client, db):
    _login_admin(client, db)
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert b"No orders yet" in resp.data
    assert b"Nothing outstanding" in resp.data


def test_dashboard_shows_status_counts(client, db):
    from app.models.enums import OrderStatus

    _login_admin(client, db)
    c = Customer(name="Ramesh", mobile="9000000001")
    db.session.add(c)
    db.session.commit()
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    assert order.status == OrderStatus.NEW

    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    # NEW count card should read 1.
    assert b'<p class="h3 mb-0">1</p>' in resp.data


def test_dashboard_urgent_and_overdue_and_todays_deliveries(client, db):
    _login_admin(client, db)
    c = Customer(name="Ramesh", mobile="9000000001")
    db.session.add(c)
    db.session.commit()
    s = _service(db)

    urgent_order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.URGENT,
        confirmed_delivery_date=date.today(),
        notes=None, actor_id=None,
    )
    overdue_order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        confirmed_delivery_date=date.today() - timedelta(days=2),
        notes=None, actor_id=None,
    )

    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert urgent_order.order_number.encode() in resp.data
    assert overdue_order.order_number.encode() in resp.data


def test_dashboard_pending_payments_widget(client, db):
    _login_admin(client, db)
    c = Customer(name="Ramesh", mobile="9000000001")
    db.session.add(c)
    db.session.commit()
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("1000.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    record_payment(order=order, amount=Decimal("300"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)

    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert b"700.00" in resp.data  # outstanding balance shown


def test_dashboard_urgent_card_links_to_a_working_filtered_view(client, db):
    _login_admin(client, db)
    c = Customer(name="Ramesh", mobile="9000000001")
    db.session.add(c)
    db.session.commit()
    s = _service(db)

    urgent_order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.URGENT,
        notes=None, actor_id=None,
    )
    normal_order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )

    dash = client.get("/admin/dashboard")
    assert b'href="/admin/orders?view=urgent"' in dash.data

    resp = client.get("/admin/orders?view=urgent")
    assert resp.status_code == 200
    assert urgent_order.order_number.encode() in resp.data
    assert normal_order.order_number.encode() not in resp.data


def test_dashboard_today_and_overdue_cards_filter_correctly(client, db):
    _login_admin(client, db)
    c = Customer(name="Ramesh", mobile="9000000001")
    db.session.add(c)
    db.session.commit()
    s = _service(db)

    today_order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        confirmed_delivery_date=date.today(),
        notes=None, actor_id=None,
    )
    overdue_order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        confirmed_delivery_date=date.today() - timedelta(days=2),
        notes=None, actor_id=None,
    )

    resp = client.get("/admin/orders?view=today")
    assert today_order.order_number.encode() in resp.data
    assert overdue_order.order_number.encode() not in resp.data

    resp = client.get("/admin/orders?view=overdue")
    assert overdue_order.order_number.encode() in resp.data
    assert today_order.order_number.encode() not in resp.data


def test_order_list_ignores_unknown_view(client, db):
    _login_admin(client, db)
    resp = client.get("/admin/orders?view=made-up")
    assert resp.status_code == 200


def test_global_search_finds_customer_and_order(client, db):
    _login_admin(client, db)
    c = Customer(name="Sunil Verma", mobile="9827011002")
    db.session.add(c)
    db.session.commit()
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )

    resp = client.get("/admin/search?q=Sunil")
    assert resp.status_code == 200
    assert b"Sunil Verma" in resp.data
    assert order.order_number.encode() in resp.data

    resp = client.get(f"/admin/search?q={order.order_number}")
    assert order.order_number.encode() in resp.data


def test_global_search_requires_admin(client):
    resp = client.get("/admin/search?q=x")
    assert resp.status_code == 302
