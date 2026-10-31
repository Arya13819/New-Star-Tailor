"""Phase 5: measurement versioning through the admin UI."""
from __future__ import annotations

from decimal import Decimal

from app.models.customer import Customer
from app.models.enums import UserRole
from app.models.measurement import MeasurementVersion
from app.models.user import User


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


def test_no_measurements_yet_message(client, db):
    _login_admin(client, db)
    c = _customer(db)
    resp = client.get(f"/admin/customers/{c.id}")
    assert b"No measurements recorded yet" in resp.data


def test_add_first_measurement_version(client, db):
    _login_admin(client, db)
    c = _customer(db)

    resp = client.post(
        f"/admin/customers/{c.id}/measurements/new",
        data={
            "shirt_length": "28.5",
            "shirt_chest": "40",
            "shirt_shoulder": "18",
            "shirt_sleeves": "24",
            "shirt_neck": "15.5",
            "pant_length": "40",
            "pant_waist": "34",
            "pant_hips": "40",
            "pant_mori": "15",
            "fitting_preference": "NORMAL",
            "allowance": "1 inch extra waist",
            "source": "SHOP",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Version 1" in resp.data

    db.session.refresh(c)
    version = c.measurement.current_version
    assert version.version_number == 1
    assert version.shirt_chest == Decimal("40.00")
    assert version.unit == "in"
    assert version.allowance == "1 inch extra waist"


def test_second_version_preserves_first(client, db):
    _login_admin(client, db)
    c = _customer(db)

    client.post(
        f"/admin/customers/{c.id}/measurements/new",
        data={"shirt_chest": "40", "fitting_preference": "NORMAL", "source": "SHOP"},
    )
    client.post(
        f"/admin/customers/{c.id}/measurements/new",
        data={"shirt_chest": "41", "fitting_preference": "NORMAL", "source": "SHOP"},
    )

    db.session.refresh(c)
    versions = sorted(c.measurement.versions, key=lambda v: v.version_number)
    assert [v.version_number for v in versions] == [1, 2]
    assert versions[0].shirt_chest == Decimal("40.00")  # untouched
    assert versions[1].shirt_chest == Decimal("41.00")
    assert c.measurement.current_version_id == versions[1].id


def test_measurement_form_prefills_from_current_version(client, db):
    _login_admin(client, db)
    c = _customer(db)
    client.post(
        f"/admin/customers/{c.id}/measurements/new",
        data={"shirt_chest": "40", "allowance": "keep loose", "source": "SHOP"},
    )

    resp = client.get(f"/admin/customers/{c.id}/measurements/new")
    assert b'value="40.00"' in resp.data
    assert b"keep loose" in resp.data


def test_measurement_history_shown_on_detail_page(client, db):
    _login_admin(client, db)
    c = _customer(db)
    for chest in ("40", "41", "42"):
        client.post(
            f"/admin/customers/{c.id}/measurements/new",
            data={"shirt_chest": chest, "source": "SHOP"},
        )
    resp = client.get(f"/admin/customers/{c.id}")
    assert b"Version 3" in resp.data  # current
    assert b"Version 2" in resp.data  # history
    assert b"Version 1" in resp.data  # history

    assert MeasurementVersion.query.count() == 3


def test_customer_cannot_add_measurements(client, db):
    c = _customer(db)
    cust_user = User(name="Ramesh", mobile="9352672795", role=UserRole.CUSTOMER)
    cust_user.set_password("supersecret1")
    db.session.add(cust_user)
    db.session.commit()
    client.post(
        "/customer/login", data={"mobile": "9352672795", "password": "supersecret1"}
    )
    resp = client.get(f"/admin/customers/{c.id}/measurements/new")
    assert resp.status_code == 403
