"""Phase 7: order creation and lifecycle."""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.models.customer import Customer
from app.models.enums import (
    FabricSource,
    OrderPriority,
    OrderStatus,
    ServiceCategory,
    UserRole,
)
from app.models.measurement import Measurement, MeasurementVersion
from app.models.order import Order
from app.models.service import Service
from app.models.user import User
from app.services.order_service import OrderError, create_order, update_status


def _login_admin(client, db):
    u = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    u.set_password("supersecret1")
    db.session.add(u)
    db.session.commit()
    client.post(
        "/admin/login",
        data={"identifier": "owner@example.com", "password": "supersecret1"},
    )
    return u


def _customer(db, name="Ramesh"):
    c = Customer(name=name, mobile="9000000010")
    db.session.add(c)
    db.session.commit()
    return c


def _service(db, code="COMBO", price="550.00", category=ServiceCategory.SHIRT):
    s = Service(code=code, name_en="Shirt + Pant Combo", category=category,
                default_stitching_price=Decimal(price))
    db.session.add(s)
    db.session.commit()
    return s


# --- numbering ------------------------------------------------------------


def test_order_numbers_are_sequential_and_4_digit_padded(app, db):
    c = _customer(db)
    s = _service(db)
    for _i in range(2):
        create_order(
            customer=c,
            items=[
                {
                    "service_id": s.id,
                    "service_name": s.name_en,
                    "category": s.category,
                    "quantity": 1,
                    "stitching_price": Decimal("550.00"),
                }
            ],
            fabric_source=FabricSource.CUSTOMER,
            priority=OrderPriority.NORMAL,
            notes=None,
            actor_id=None,
        )
    numbers = [o.order_number for o in Order.query.order_by(Order.id).all()]
    assert numbers == ["NST-0001", "NST-0002"]


# --- money / business rules ------------------------------------------------


def test_customer_cloth_advance_is_50_percent_of_stitching(app, db):
    c = _customer(db)
    s = _service(db, price="700.00")
    order = create_order(
        customer=c,
        items=[
            {
                "service_id": s.id,
                "service_name": s.name_en,
                "category": s.category,
                "quantity": 1,
                "stitching_price": Decimal("700.00"),
                "material_price": Decimal("9999"),  # must be ignored: customer cloth
            }
        ],
        fabric_source=FabricSource.CUSTOMER,
        priority=OrderPriority.NORMAL,
        notes=None,
        actor_id=None,
    )
    assert order.subtotal_material == Decimal("0.00")  # material forced to zero
    assert order.subtotal_stitching == Decimal("700.00")
    assert order.grand_total == Decimal("700.00")
    assert order.required_advance == Decimal("350.00")
    assert order.advance_satisfied is False


def test_shop_cloth_advance_is_100_percent_of_grand_total(app, db):
    c = _customer(db)
    s = _service(db, code="CHEETAH_US", price="850.00", category=ServiceCategory.ARMY)
    order = create_order(
        customer=c,
        items=[
            {
                "service_id": s.id,
                "service_name": s.name_en,
                "category": s.category,
                "quantity": 1,
                "stitching_price": Decimal("850.00"),
                "material_price": Decimal("1200.00"),
            }
        ],
        fabric_source=FabricSource.SHOP,
        priority=OrderPriority.URGENT,
        notes=None,
        actor_id=None,
    )
    assert order.subtotal_stitching == Decimal("850.00")
    assert order.subtotal_material == Decimal("1200.00")
    assert order.grand_total == Decimal("2050.00")
    assert order.required_advance == Decimal("2050.00")  # 100%, not just stitching


def test_multiple_items_and_quantities_sum_correctly(app, db):
    c = _customer(db)
    s1 = _service(db, code="COMBO", price="550.00")
    s2 = _service(db, code="KHAAKI", price="700.00", category=ServiceCategory.POLICE)
    order = create_order(
        customer=c,
        items=[
            {"service_id": s1.id, "service_name": s1.name_en, "category": s1.category,
             "quantity": 2, "stitching_price": Decimal("550.00")},
            {"service_id": s2.id, "service_name": s2.name_en, "category": s2.category,
             "quantity": 1, "stitching_price": Decimal("700.00")},
        ],
        fabric_source=FabricSource.CUSTOMER,
        priority=OrderPriority.NORMAL,
        notes=None,
        actor_id=None,
    )
    assert order.subtotal_stitching == Decimal("1800.00")
    assert {it.line_total for it in order.items} == {Decimal("1100.00"), Decimal("700.00")}


def test_urgent_priority_allows_a_manual_price_override(app, db):
    """No formula for urgent pricing — whatever the admin types is used verbatim."""
    c = _customer(db)
    s = _service(db, price="700.00")
    order = create_order(
        customer=c,
        items=[
            {"service_id": s.id, "service_name": s.name_en, "category": s.category,
             "quantity": 1, "stitching_price": Decimal("1500.00")},  # manual urgent price
        ],
        fabric_source=FabricSource.CUSTOMER,
        priority=OrderPriority.URGENT,
        notes=None,
        actor_id=None,
    )
    assert order.subtotal_stitching == Decimal("1500.00")
    assert order.priority == OrderPriority.URGENT


def test_no_items_is_rejected(app, db):
    c = _customer(db)
    with pytest.raises(OrderError):
        create_order(
            customer=c, items=[], fabric_source=FabricSource.CUSTOMER,
            priority=OrderPriority.NORMAL, notes=None, actor_id=None,
        )


def test_changing_service_price_never_touches_existing_orders(app, db):
    c = _customer(db)
    s = _service(db, price="550.00")
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    s.default_stitching_price = Decimal("999.00")
    db.session.commit()

    db.session.refresh(order)
    assert order.items[0].stitching_price == Decimal("550.00")  # untouched


def test_order_snapshots_current_measurement_version(app, db):
    c = _customer(db)
    m = Measurement(customer=c)
    db.session.add(m)
    db.session.flush()
    v = MeasurementVersion(measurement_id=m.id, version_number=1, shirt_chest=Decimal("40.00"))
    db.session.add(v)
    db.session.flush()
    m.current_version_id = v.id
    db.session.commit()

    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    assert order.items[0].measurement_version_id == v.id

    # A later measurement edit must not retroactively change this order's item.
    v2 = MeasurementVersion(measurement_id=m.id, version_number=2, shirt_chest=Decimal("42.00"))
    db.session.add(v2)
    db.session.flush()
    m.current_version_id = v2.id
    db.session.commit()

    db.session.refresh(order)
    assert order.items[0].measurement_version_id == v.id
    assert order.items[0].measurement_version.shirt_chest == Decimal("40.00")


def test_status_transition_sets_delivered_at(app, db):
    c = _customer(db)
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    assert order.delivered_at is None
    update_status(order, OrderStatus.DELIVERED, actor_id=None)
    assert order.delivered_at is not None
    assert order.status == OrderStatus.DELIVERED


# --- HTTP / admin routes ----------------------------------------------------


def test_order_list_requires_admin(client):
    resp = client.get("/admin/orders")
    assert resp.status_code == 302


def test_walk_in_order_creation_via_http(client, db):
    _login_admin(client, db)
    c = _customer(db)
    s = _service(db)

    resp = client.post(
        f"/admin/orders/new?customer_id={c.id}",
        data={
            "items-0-service_id": str(s.id),
            "items-0-quantity": "2",
            "items-0-stitching_price": "550",
            "items-0-material_price": "0",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
            "notes": "Test order",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"NST-0001" in resp.data

    order = Order.query.filter_by(order_number="NST-0001").one()
    assert order.grand_total == Decimal("1100.00")
    assert order.customer_id == c.id


def test_order_creation_needs_a_priced_service(client, db):
    _login_admin(client, db)
    c = _customer(db)
    # No priced services exist yet.
    resp = client.post(
        f"/admin/orders/new?customer_id={c.id}",
        data={
            "items-0-service_id": "",
            "items-0-quantity": "1",
            "items-0-stitching_price": "",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
        },
        follow_redirects=True,
    )
    assert Order.query.count() == 0
    assert resp.status_code == 200


def test_invalid_item_submission_shows_field_errors_not_silence(client, db):
    _login_admin(client, db)
    c = _customer(db)
    _service(db)

    resp = client.post(
        f"/admin/orders/new?customer_id={c.id}",
        data={
            "items-0-service_id": "",
            "items-0-quantity": "-3",
            "items-0-stitching_price": "",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
        },
    )
    assert resp.status_code == 200
    assert Order.query.count() == 0
    # The field itself must show something wrong, and a top-level flash too —
    # not a silent re-render with no explanation.
    assert b"is-invalid" in resp.data
    assert b"Please check the highlighted fields" in resp.data


def test_past_delivery_date_is_rejected(client, db):
    _login_admin(client, db)
    c = _customer(db)
    s = _service(db)

    resp = client.post(
        f"/admin/orders/new?customer_id={c.id}",
        data={
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "items-0-stitching_price": "550",
            "items-0-material_price": "0",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
            "confirmed_delivery_date": "2020-01-01",
        },
    )
    assert resp.status_code == 200
    assert Order.query.count() == 0
    assert b"is in the past" in resp.data


def test_order_detail_shows_advance_warning_when_unpaid(client, db):
    _login_admin(client, db)
    c = _customer(db)
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    resp = client.get(f"/admin/orders/{order.id}")
    assert resp.status_code == 200
    assert b"Advance not fully received" in resp.data


def test_status_change_via_http(client, db):
    _login_admin(client, db)
    c = _customer(db)
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    resp = client.post(
        f"/admin/orders/{order.id}/status", data={"status": "READY"}, follow_redirects=True
    )
    assert resp.status_code == 200
    db.session.refresh(order)
    assert order.status == OrderStatus.READY


def test_delivered_button_warns_about_outstanding_balance(client, db):
    _login_admin(client, db)
    c = _customer(db)
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    resp = client.get(f"/admin/orders/{order.id}")
    assert b'data-confirm-balance="' in resp.data


def test_delivered_button_has_no_warning_once_fully_paid(client, db):
    from app.models.enums import PaymentMethod
    from app.services.payment_service import record_payment

    _login_admin(client, db)
    c = _customer(db)
    s = _service(db)
    order = create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    record_payment(order=order, amount=Decimal("550.00"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    resp = client.get(f"/admin/orders/{order.id}")
    assert b'data-confirm-balance="' not in resp.data


def test_order_search_by_number_and_customer(client, db):
    _login_admin(client, db)
    c1 = Customer(name="Sunil Verma", mobile="9000000001")
    c2 = Customer(name="Imran Sheikh", mobile="9000000002")
    db.session.add_all([c1, c2])
    db.session.commit()
    s = _service(db)
    create_order(customer=c1, items=[{"service_id": s.id, "service_name": s.name_en,
                 "category": s.category, "quantity": 1, "stitching_price": Decimal("550.00")}],
                 fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
                 notes=None, actor_id=None)
    create_order(customer=c2, items=[{"service_id": s.id, "service_name": s.name_en,
                 "category": s.category, "quantity": 1, "stitching_price": Decimal("550.00")}],
                 fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
                 notes=None, actor_id=None)

    resp = client.get("/admin/orders?q=Sunil")
    assert b"NST-0001" in resp.data
    assert b"NST-0002" not in resp.data

    resp = client.get("/admin/orders?q=NST-0002")
    assert b"NST-0002" in resp.data
    assert b"NST-0001" not in resp.data


def test_non_admin_cannot_manage_orders(client, db):
    cust = User(name="Ramesh", mobile="9352672795", role=UserRole.CUSTOMER)
    cust.set_password("supersecret1")
    db.session.add(cust)
    db.session.commit()
    client.post("/customer/login", data={"mobile": "9352672795", "password": "supersecret1"})
    assert client.get("/admin/orders").status_code == 403
    assert client.get("/admin/orders/new").status_code == 403
