"""Phase 4: admin customer management."""
from __future__ import annotations

from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.models.enums import UserRole
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


def test_customer_list_requires_admin(client):
    resp = client.get("/admin/customers")
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_customer_list_empty_state(client, db):
    _login_admin(client, db)
    resp = client.get("/admin/customers")
    assert resp.status_code == 200
    assert b"No customers yet" in resp.data


def test_create_customer(client, db):
    admin = _login_admin(client, db)
    resp = client.post(
        "/admin/customers/new",
        data={"name": "Ramesh Prajapat", "mobile": "9827011001", "address": "Bagana Road"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Ramesh Prajapat" in resp.data

    customer = Customer.query.filter_by(mobile="9827011001").one()
    assert customer.address == "Bagana Road"

    log = AuditLog.query.filter_by(entity_type="customer", entity_id=customer.id).one()
    assert log.action == "create"
    assert log.actor_user_id == admin.id


def test_create_customer_rejects_bad_mobile(client, db):
    _login_admin(client, db)
    resp = client.post(
        "/admin/customers/new",
        data={"name": "Bad Mobile", "mobile": "123"},
    )
    assert resp.status_code == 200  # re-rendered with an error, no redirect
    assert Customer.query.count() == 0


def test_duplicate_mobile_is_allowed_but_flagged(client, db):
    _login_admin(client, db)
    db.session.add(Customer(name="Person A", mobile="9352672795"))
    db.session.commit()

    # The "new customer" form warns about the existing profile...
    resp = client.get("/admin/customers/new?mobile=9352672795")
    assert b"existing customer" in resp.data
    assert b"Person A" in resp.data

    # ...but creating a second profile with the same number still succeeds.
    resp = client.post(
        "/admin/customers/new",
        data={"name": "Person B", "mobile": "9352672795"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    same_mobile = Customer.query.filter_by(mobile="9352672795").all()
    assert {c.name for c in same_mobile} == {"Person A", "Person B"}


def test_customer_search_by_name(client, db):
    _login_admin(client, db)
    db.session.add_all(
        [
            Customer(name="Sunil Verma", mobile="9000000001"),
            Customer(name="Imran Sheikh", mobile="9000000002"),
        ]
    )
    db.session.commit()

    resp = client.get("/admin/customers?q=sunil")
    assert b"Sunil Verma" in resp.data
    assert b"Imran Sheikh" not in resp.data


def test_customer_search_by_mobile(client, db):
    _login_admin(client, db)
    db.session.add_all(
        [
            Customer(name="Sunil Verma", mobile="9000000001"),
            Customer(name="Imran Sheikh", mobile="9000000002"),
        ]
    )
    db.session.commit()

    resp = client.get("/admin/customers?q=0000002")
    assert b"Imran Sheikh" in resp.data
    assert b"Sunil Verma" not in resp.data


def test_customer_detail_and_edit(client, db):
    _login_admin(client, db)
    c = Customer(name="Deepak Nagda", mobile="9000000003")
    db.session.add(c)
    db.session.commit()

    resp = client.get(f"/admin/customers/{c.id}")
    assert resp.status_code == 200
    assert b"Deepak Nagda" in resp.data

    resp = client.post(
        f"/admin/customers/{c.id}/edit",
        data={"name": "Deepak N. Nagda", "mobile": "9000000003", "address": "Mahavir Nagar"},
        follow_redirects=True,
    )
    assert b"Deepak N. Nagda" in resp.data
    db.session.refresh(c)
    assert c.address == "Mahavir Nagar"


def test_customer_detail_404_for_unknown_id(client, db):
    _login_admin(client, db)
    resp = client.get("/admin/customers/999")
    assert resp.status_code == 404


def test_customer_customer_cannot_access_admin_customers(client, db):
    cust = User(name="Ramesh", mobile="9352672795", role=UserRole.CUSTOMER)
    cust.set_password("supersecret1")
    db.session.add(cust)
    db.session.commit()
    client.post(
        "/customer/login", data={"mobile": "9352672795", "password": "supersecret1"}
    )
    resp = client.get("/admin/customers")
    assert resp.status_code == 403
