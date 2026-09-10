"""Phase 2: the data model behaves as the business rules require."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.models import (
    Customer,
    Measurement,
    MeasurementVersion,
    Order,
    OrderItem,
    Payment,
    PaymentEvent,
    Service,
    Setting,
    User,
)
from app.models.enums import (
    FabricSource,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    ServiceCategory,
    UserRole,
)

EXPECTED_TABLES = {
    "users",
    "customers",
    "measurements",
    "measurement_versions",
    "services",
    "orders",
    "order_items",
    "order_sequences",
    "payments",
    "payment_events",
    "reference_images",
    "notifications",
    "settings",
    "audit_logs",
}


def test_all_tables_present(db):
    names = set(inspect(db.engine).get_table_names())
    assert EXPECTED_TABLES.issubset(names)


def test_password_hashing_roundtrip(db):
    u = User(name="Operator", mobile="9352672795", role=UserRole.ADMIN)
    u.set_password("correct horse")
    db.session.add(u)
    db.session.commit()

    assert u.password_hash != "correct horse"
    assert u.check_password("correct horse") is True
    assert u.check_password("wrong") is False
    assert u.is_admin is True


def test_two_customers_may_share_a_mobile(db):
    a = Customer(name="Person A", mobile="9352672795")
    b = Customer(name="Person B", mobile="9352672795")
    db.session.add_all([a, b])
    db.session.commit()

    same = Customer.query.filter_by(mobile="9352672795").all()
    assert {c.name for c in same} == {"Person A", "Person B"}
    assert a.id != b.id


def test_setting_json_roundtrip(db):
    s = Setting(key="shop")
    s.value = {"name": "New Star Tailor", "phone": "9352672795"}
    db.session.add(s)
    db.session.commit()

    fetched = Setting.query.filter_by(key="shop").one()
    assert fetched.value["phone"] == "9352672795"


def test_service_price_may_be_unset(db):
    shirt = Service(code="SHIRT", name_en="Shirt", category=ServiceCategory.SHIRT)
    combo = Service(
        code="SHIRT_PANT_COMBO",
        name_en="Shirt + Pant Combo",
        category=ServiceCategory.SHIRT,
        default_stitching_price=Decimal("550.00"),
    )
    db.session.add_all([shirt, combo])
    db.session.commit()

    assert shirt.price_is_set is False
    assert combo.price_is_set is True


def test_measurement_versioning_keeps_history(db):
    c = Customer(name="Ramesh", mobile="9000000001")
    m = Measurement(customer=c)
    db.session.add_all([c, m])
    db.session.flush()

    v1 = MeasurementVersion(measurement_id=m.id, version_number=1, shirt_chest=Decimal("40.00"))
    db.session.add(v1)
    db.session.flush()
    m.current_version_id = v1.id
    db.session.commit()

    v2 = MeasurementVersion(measurement_id=m.id, version_number=2, shirt_chest=Decimal("42.00"))
    db.session.add(v2)
    db.session.flush()
    m.current_version_id = v2.id
    db.session.commit()

    db.session.refresh(m)
    assert {v.version_number for v in m.versions} == {1, 2}
    assert m.current_version.shirt_chest == Decimal("42.00")
    # v1 is untouched.
    assert db.session.get(MeasurementVersion, v1.id).shirt_chest == Decimal("40.00")


def test_measurement_version_number_unique_per_measurement(db):
    c = Customer(name="Sunil", mobile="9000000002")
    m = Measurement(customer=c)
    db.session.add_all([c, m])
    db.session.flush()
    db.session.add(MeasurementVersion(measurement_id=m.id, version_number=1))
    db.session.commit()
    db.session.add(MeasurementVersion(measurement_id=m.id, version_number=1))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_order_items_cascade_delete(db):
    c = Customer(name="Imran", mobile="9000000003")
    db.session.add(c)
    db.session.flush()
    o = Order(customer_id=c.id, fabric_source=FabricSource.CUSTOMER, status=OrderStatus.NEW)
    db.session.add(o)
    db.session.flush()
    o.items.append(
        OrderItem(
            service_name_snapshot="Police Khaaki",
            category_snapshot=ServiceCategory.POLICE,
            stitching_price=Decimal("700.00"),
            material_price=Decimal("0.00"),
            quantity=1,
            line_total=Decimal("700.00"),
        )
    )
    db.session.commit()
    item_id = o.items[0].id

    db.session.delete(o)
    db.session.commit()
    assert db.session.get(OrderItem, item_id) is None


def test_payment_event_rejects_duplicate_webhook(db):
    db.session.add(PaymentEvent(provider="demo", event_id="evt_1", event_type="paid"))
    db.session.commit()
    db.session.add(PaymentEvent(provider="demo", event_id="evt_1", event_type="paid"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_payment_defaults_to_pending(db):
    c = Customer(name="Deepak", mobile="9000000004")
    db.session.add(c)
    db.session.flush()
    o = Order(customer_id=c.id, fabric_source=FabricSource.SHOP)
    db.session.add(o)
    db.session.flush()
    p = Payment(
        order_id=o.id,
        customer_id=c.id,
        amount=Decimal("500.00"),
        method=PaymentMethod.ONLINE,
    )
    db.session.add(p)
    db.session.commit()
    assert p.status == PaymentStatus.PENDING
    assert p.is_verified is False


def test_order_confirmed_date_helpers(db):
    c = Customer(name="Farhan", mobile="9000000005")
    db.session.add(c)
    db.session.flush()
    o = Order(
        customer_id=c.id,
        fabric_source=FabricSource.CUSTOMER,
        requested_delivery_date=date(2026, 1, 1),
    )
    db.session.add(o)
    db.session.commit()
    assert o.is_confirmed is False
    o.order_number = "NST-000001"
    db.session.commit()
    assert o.is_confirmed is True
