"""Phase 6: service catalogue & pricing."""
from __future__ import annotations

from decimal import Decimal

from app.models.enums import ServiceCategory, UserRole
from app.models.service import Service
from app.models.user import User
from app.services.catalog_service import DEFAULT_SERVICES, seed_defaults


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


def test_seed_defaults_matches_business_rules(app, db):
    created = seed_defaults()
    assert created == len(DEFAULT_SERVICES)

    combo = Service.query.filter_by(code="SHIRT_PANT_COMBO").one()
    assert combo.default_stitching_price == Decimal("550.00")

    khaaki = Service.query.filter_by(code="POLICE_KHAAKI").one()
    assert khaaki.default_stitching_price == Decimal("700.00")

    cheetah_us = Service.query.filter_by(code="CHEETAH_US_PATTERN").one()
    assert cheetah_us.default_stitching_price == Decimal("850.00")
    assert cheetah_us.category == ServiceCategory.ARMY  # owner's explicit call

    # Prices the owner said would come "later" are seeded unset, not guessed.
    for code in ("SHIRT", "PANT", "CRPF_KHAAKI_DANGRI", "ARMY_PATTERN"):
        svc = Service.query.filter_by(code=code).one()
        assert svc.default_stitching_price is None
        assert svc.price_is_set is False


def test_seed_defaults_is_idempotent(app, db):
    first = seed_defaults()
    second = seed_defaults()
    assert first == len(DEFAULT_SERVICES)
    assert second == 0
    assert Service.query.count() == len(DEFAULT_SERVICES)


def test_seeding_never_overwrites_a_manually_set_price(app, db):
    seed_defaults()
    shirt = Service.query.filter_by(code="SHIRT").one()
    shirt.default_stitching_price = Decimal("450.00")
    db.session.commit()

    seed_defaults()  # re-run, e.g. via the "Load default services" button

    db.session.refresh(shirt)
    assert shirt.default_stitching_price == Decimal("450.00")


def test_service_list_requires_admin(client):
    resp = client.get("/admin/services")
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_service_list_seed_button(client, db):
    _login_admin(client, db)
    resp = client.get("/admin/services")
    assert b"No services yet" in resp.data

    resp = client.post("/admin/services/seed-defaults", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Shirt" in resp.data
    assert b"Not set" in resp.data  # unset prices flagged, not hidden or guessed


def test_create_custom_service(client, db):
    _login_admin(client, db)
    resp = client.post(
        "/admin/services/new",
        data={
            "code": "KURTA_PYJAMA",
            "name_en": "Kurta Pyjama",
            "name_hi": "",
            "category": "SHIRT",
            "default_stitching_price": "600",
            "sort_order": "95",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    svc = Service.query.filter_by(code="KURTA_PYJAMA").one()
    assert svc.default_stitching_price == Decimal("600.00")


def test_duplicate_code_rejected(client, db):
    _login_admin(client, db)
    client.post(
        "/admin/services/new",
        data={"code": "DUPE", "name_en": "First", "category": "SHIRT", "sort_order": "1"},
    )
    resp = client.post(
        "/admin/services/new",
        data={"code": "DUPE", "name_en": "Second", "category": "PANT", "sort_order": "2"},
        follow_redirects=True,
    )
    assert b"already exists" in resp.data
    assert Service.query.filter_by(code="DUPE").count() == 1


def test_edit_price_does_not_touch_code(client, db):
    _login_admin(client, db)
    svc = Service(code="TEST_SVC", name_en="Test", category=ServiceCategory.SHIRT)
    db.session.add(svc)
    db.session.commit()

    resp = client.post(
        f"/admin/services/{svc.id}/edit",
        data={
            "code": "SHOULD_BE_IGNORED",
            "name_en": "Test Renamed",
            "category": "SHIRT",
            "default_stitching_price": "500",
            "sort_order": "1",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    db.session.refresh(svc)
    assert svc.code == "TEST_SVC"  # unchanged
    assert svc.name_en == "Test Renamed"
    assert svc.default_stitching_price == Decimal("500.00")


def test_toggle_active(client, db):
    _login_admin(client, db)
    svc = Service(code="TOGGLE_ME", name_en="Toggle Me", category=ServiceCategory.SHIRT)
    db.session.add(svc)
    db.session.commit()
    assert svc.is_active is True

    client.post(f"/admin/services/{svc.id}/toggle")
    db.session.refresh(svc)
    assert svc.is_active is False

    client.post(f"/admin/services/{svc.id}/toggle")
    db.session.refresh(svc)
    assert svc.is_active is True


def test_non_admin_cannot_manage_services(client, db):
    cust = User(name="Ramesh", mobile="9352672795", role=UserRole.CUSTOMER)
    cust.set_password("supersecret1")
    db.session.add(cust)
    db.session.commit()
    client.post(
        "/customer/login", data={"mobile": "9352672795", "password": "supersecret1"}
    )
    assert client.get("/admin/services").status_code == 403
    assert client.get("/admin/services/new").status_code == 403


def test_public_catalogue_filters_category_and_search_and_excludes_inactive(client, db):
    seed_defaults()
    hidden = Service(code="HIDDEN", name_en="Hidden police service", category=ServiceCategory.POLICE,
                     default_stitching_price=Decimal("100.00"), is_active=False)
    db.session.add(hidden)
    db.session.commit()
    page = client.get("/services?category=CRPF&q=cheetah")
    assert page.status_code == 200
    assert 'data-service="CRPF_CHEETAH"' in page.text
    assert 'data-service="POLICE_KHAAKI"' not in page.text
    assert 'data-service="CRPF_KHAAKI"' not in page.text
    assert 'data-service="HIDDEN"' not in client.get("/services").text
    empty = client.get("/services?q=does-not-exist")
    assert "No matching services" in empty.text
    assert "Clear filters" in empty.text
    assert 'data-service="' not in empty.text
    assert client.get("/services?category=NOT_REAL").status_code == 200


def test_catalogue_search_treats_metacharacters_as_literal_text(client, db):
    seed_defaults()
    for search in ("%", "<script>"):
        page = client.get("/services", query_string={"q": search})
        assert "No matching services" in page.text
        assert '<script>' not in page.text
    underscore = client.get("/services?q=_")
    assert 'data-service="SHIRT_PANT_COMBO"' in underscore.text
    assert 'data-service="SHIRT"' not in underscore.text
    assert 'data-service="PANT"' not in underscore.text


def test_order_link_selects_only_an_active_priced_service_and_does_not_override_post(client, db):
    from app.models.order import Order
    seed_defaults()
    combo = Service.query.filter_by(code="SHIRT_PANT_COMBO").one()
    unset = Service.query.filter_by(code="SHIRT").one()
    hidden = Service.query.filter_by(code="POLICE_KHAAKI").one()
    hidden.is_active = False
    db.session.commit()
    valid = client.get(f"/order?service={combo.id}")
    assert f'value="{combo.id}" selected' in valid.text
    for value in (unset.id, hidden.id, "bad", 999999):
        page = client.get(f"/order?service={value}")
        assert f'value="{value}" selected' not in page.text
    # A URL parameter must never choose the service on behalf of a POST.
    response = client.post(f"/order?service={combo.id}", data={
        "name": "Test customer", "mobile": "9555555511", "fabric_source": "CUSTOMER",
        "items-0-service_id": "", "items-0-quantity": "1",
    })
    assert response.status_code == 200
    assert Order.query.count() == 0
