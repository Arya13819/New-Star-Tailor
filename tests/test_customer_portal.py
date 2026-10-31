"""Phase 10: customer portal, with strict data isolation between customers."""
from __future__ import annotations

from decimal import Decimal

from app.models.customer import Customer
from app.models.enums import FabricSource, OrderPriority, ServiceCategory, UserRole
from app.models.service import Service
from app.models.user import User
from app.services.order_service import create_order


def _register(client, name, mobile):
    client.post("/customer/logout")  # registering while signed in just redirects home
    client.post(
        "/customer/register",
        data={
            "name": name,
            "mobile": mobile,
            "password": "supersecret1",
            "confirm_password": "supersecret1",
        },
    )


def _service(db):
    s = Service(code="SVC", name_en="Service", category=ServiceCategory.SHIRT,
                default_stitching_price=Decimal("550.00"))
    db.session.add(s)
    db.session.commit()
    return s


def test_dashboard_requires_customer_login(client):
    resp = client.get("/customer/dashboard")
    assert resp.status_code == 302
    assert "/customer/login" in resp.headers["Location"]


def test_admin_cannot_use_customer_portal(client, db):
    admin = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    admin.set_password("supersecret1")
    db.session.add(admin)
    db.session.commit()
    client.post("/admin/login", data={"identifier": "owner@example.com", "password": "supersecret1"})
    assert client.get("/customer/dashboard").status_code == 403


def test_customer_sees_own_order(client, db):
    _register(client, "Customer A", "9333333331")
    profile = Customer.query.filter_by(mobile="9333333331").one()
    s = _service(db)
    order = create_order(
        customer=profile,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )

    resp = client.get("/customer/dashboard")
    assert order.order_number.encode() in resp.data

    resp = client.get(f"/customer/orders/{order.id}")
    assert resp.status_code == 200
    assert order.order_number.encode() in resp.data


def test_dashboard_cards_link_to_working_filtered_views(client, db):
    _register(client, "Customer A", "9333333331")
    profile = Customer.query.filter_by(mobile="9333333331").one()
    s = _service(db)
    open_order = create_order(
        customer=profile,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )

    dash = client.get("/customer/dashboard")
    assert b'href="/customer/orders?view=open"' in dash.data
    assert b'href="/customer/payments"' in dash.data

    resp = client.get("/customer/orders?view=open")
    assert resp.status_code == 200
    assert open_order.order_number.encode() in resp.data

    resp = client.get("/customer/payments")
    assert resp.status_code == 200


def test_customer_cannot_see_another_customers_order(client, db):
    # Customer A has an order.
    profile_a = Customer(name="Customer A", mobile="9333333331")
    db.session.add(profile_a)
    db.session.commit()
    s = _service(db)
    order = create_order(
        customer=profile_a,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )

    # Customer B logs in and tries to guess A's order id.
    _register(client, "Customer B", "9333333332")
    resp = client.get(f"/customer/orders/{order.id}")
    assert resp.status_code == 404  # not 403 - never confirms it exists

    resp = client.get("/customer/dashboard")
    assert order.order_number.encode() not in resp.data
    assert b"No orders yet" in resp.data


def test_customer_orders_list_only_shows_own_orders(client, db):
    _register(client, "Customer A", "9333333331")
    _register(client, "Customer B", "9333333332")  # replaces A's session
    profile_a = Customer.query.filter_by(mobile="9333333331").one()
    profile_b = Customer.query.filter_by(mobile="9333333332").one()
    s = _service(db)
    order_a = create_order(
        customer=profile_a,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    order_b = create_order(
        customer=profile_b,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )

    client.post("/customer/logout")
    client.post("/customer/login", data={"mobile": "9333333331", "password": "supersecret1"})
    resp = client.get("/customer/orders")
    assert order_a.order_number.encode() in resp.data
    assert order_b.order_number.encode() not in resp.data


def test_customer_payments_scoped_to_own_orders(client, db):
    from app.models.enums import PaymentMethod
    from app.services.payment_service import record_payment

    _register(client, "Customer A", "9333333331")
    _register(client, "Customer B", "9333333332")  # replaces A's session
    profile_a = Customer.query.filter_by(mobile="9333333331").one()
    profile_b = Customer.query.filter_by(mobile="9333333332").one()
    s = _service(db)
    order_a = create_order(
        customer=profile_a,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    order_b = create_order(
        customer=profile_b,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    record_payment(order=order_a, amount=Decimal("100"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    record_payment(order=order_b, amount=Decimal("200"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)

    client.post("/customer/logout")
    client.post("/customer/login", data={"mobile": "9333333331", "password": "supersecret1"})
    resp = client.get("/customer/payments")
    assert b"100.00" in resp.data
    assert b"200.00" not in resp.data


def test_measurements_page_shows_own_profile_only(client, db):
    _register(client, "Customer A", "9333333331")
    other = Customer(name="Unrelated Person", mobile="9000000099")
    db.session.add(other)
    db.session.commit()

    resp = client.get("/customer/measurements")
    assert resp.status_code == 200
    assert b"Customer A" in resp.data
    assert b"Unrelated Person" not in resp.data
