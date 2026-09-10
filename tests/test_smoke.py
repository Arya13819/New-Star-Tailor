"""Phase 1 smoke tests: the app boots and the shell renders."""
from __future__ import annotations


def test_app_factory(app):
    assert app.config["TESTING"] is True
    assert app.config["SHOP_NAME"] == "New Star Tailor"


def test_healthz_liveness(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_api_health_reports_integrations(client):
    resp = client.get("/api/health")
    body = resp.get_json()
    assert body["service"] == "new-star-tailor"
    # Integrations are NOT configured in tests — must be reported as False.
    assert body["integrations"]["payments_configured"] is False
    assert body["integrations"]["messaging_configured"] is False


def test_homepage_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"New Star Tailor" in resp.data
    assert b"9352672795" in resp.data


def test_unknown_page_shows_friendly_404(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert b"Page not found" in resp.data
    assert b"Traceback" not in resp.data


def test_language_switch_to_hindi(client):
    client.get("/set-language/hi")
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'lang="hi"' in resp.data


def test_csrf_protection_enabled_for_forms(app):
    # CSRF is disabled in the testing config for convenience, but the
    # extension must still be registered on the app.
    assert "csrf" in app.extensions
