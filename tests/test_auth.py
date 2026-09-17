"""Phase 3: authentication — admin login, customer register/login, gating."""
from __future__ import annotations

from app.models.enums import UserRole
from app.models.user import User


def _make_admin(db, email="owner@example.com", password="supersecret1"):
    u = User(name="Owner", email=email, role=UserRole.ADMIN)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u


def _make_customer(db, mobile="9352672795", password="supersecret1"):
    u = User(name="Ramesh", mobile=mobile, role=UserRole.CUSTOMER)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u


# --- CLI ---------------------------------------------------------------


def test_create_admin_cli(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(
        args=[
            "nst",
            "create-admin",
            "--name",
            "Owner",
            "--email",
            "owner@example.com",
            "--mobile",
            "9352672795",
            "--password",
            "supersecret1",
        ]
    )
    assert result.exit_code == 0, result.output
    user = User.query.filter_by(email="owner@example.com").one()
    assert user.role == UserRole.ADMIN
    assert user.check_password("supersecret1")


def test_create_admin_cli_rejects_short_password(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(
        args=[
            "nst",
            "create-admin",
            "--name",
            "Owner",
            "--email",
            "owner@example.com",
            "--mobile",
            "",
            "--password",
            "short",
        ]
    )
    assert result.exit_code != 0
    assert User.query.count() == 0


# --- Admin login ---------------------------------------------------------


def test_admin_login_page_renders(client):
    resp = client.get("/admin/login")
    assert resp.status_code == 200
    assert b"Sign in" in resp.data


def test_admin_login_success_redirects_to_dashboard(client, db):
    _make_admin(db)
    resp = client.post(
        "/admin/login",
        data={"identifier": "owner@example.com", "password": "supersecret1"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Welcome, Owner" in resp.data


def test_admin_login_with_mobile_also_works(client, db):
    _make_admin(db, email="owner2@example.com")
    User.query.filter_by(email="owner2@example.com").update({"mobile": "9352672795"})
    db.session.commit()
    resp = client.post(
        "/admin/login",
        data={"identifier": "9352672795", "password": "supersecret1"},
        follow_redirects=True,
    )
    assert b"Welcome, Owner" in resp.data


def test_admin_login_wrong_password_shows_friendly_error(client, db):
    _make_admin(db)
    resp = client.post(
        "/admin/login",
        data={"identifier": "owner@example.com", "password": "wrong"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"is not correct" in resp.data


def test_unauthenticated_admin_dashboard_redirects_to_login(client):
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_customer_cannot_access_admin_dashboard(client, db):
    _make_customer(db)
    client.post(
        "/customer/login",
        data={"mobile": "9352672795", "password": "supersecret1"},
    )
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 403


# --- Customer register / login -------------------------------------------


def test_customer_can_register_and_lands_on_dashboard(client, db):
    resp = client.post(
        "/customer/register",
        data={
            "name": "Sunil Verma",
            "mobile": "9827011002",
            "address": "Station Road, Neemuch",
            "password": "supersecret1",
            "confirm_password": "supersecret1",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Welcome, Sunil Verma" in resp.data

    user = User.query.filter_by(mobile="9827011002").one()
    assert user.role == UserRole.CUSTOMER
    assert len(user.customers) == 1
    assert user.customers[0].mobile == "9827011002"


def test_customer_registration_password_mismatch_is_rejected(client, db):
    resp = client.post(
        "/customer/register",
        data={
            "name": "Sunil Verma",
            "mobile": "9827011002",
            "password": "supersecret1",
            "confirm_password": "different1",
        },
    )
    assert resp.status_code == 200  # re-rendered form, not a redirect
    assert User.query.count() == 0


def test_duplicate_mobile_registration_is_rejected_with_friendly_message(client, db):
    _make_customer(db, mobile="9827011002")
    resp = client.post(
        "/customer/register",
        data={
            "name": "Another Person",
            "mobile": "9827011002",
            "password": "supersecret1",
            "confirm_password": "supersecret1",
        },
        follow_redirects=True,
    )
    assert b"already exists" in resp.data
    assert User.query.filter_by(mobile="9827011002").count() == 1


def test_customer_login_success(client, db):
    _make_customer(db)
    resp = client.post(
        "/customer/login",
        data={"mobile": "9352672795", "password": "supersecret1"},
        follow_redirects=True,
    )
    assert b"Welcome, Ramesh" in resp.data


def test_customer_login_wrong_password(client, db):
    _make_customer(db)
    resp = client.post(
        "/customer/login",
        data={"mobile": "9352672795", "password": "wrong"},
        follow_redirects=True,
    )
    assert b"is not correct" in resp.data


def test_unauthenticated_customer_dashboard_redirects_to_customer_login(client):
    resp = client.get("/customer/dashboard")
    assert resp.status_code == 302
    assert "/customer/login" in resp.headers["Location"]


def test_admin_cannot_access_customer_dashboard(client, db):
    _make_admin(db)
    client.post(
        "/admin/login",
        data={"identifier": "owner@example.com", "password": "supersecret1"},
    )
    resp = client.get("/customer/dashboard")
    assert resp.status_code == 403


def test_logout_clears_session(client, db):
    _make_customer(db)
    client.post(
        "/customer/login",
        data={"mobile": "9352672795", "password": "supersecret1"},
    )
    client.post("/customer/logout")
    resp = client.get("/customer/dashboard")
    assert resp.status_code == 302
