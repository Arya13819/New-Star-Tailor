"""Phase 16 (PWA) + Phase 17 (SEO + hardening) tests."""
from __future__ import annotations

import json


def test_manifest_is_served_and_valid_json(client):
    resp = client.get("/static/manifest.webmanifest")
    assert resp.status_code == 200
    manifest = json.loads(resp.data)
    assert manifest["name"] == "New Star Tailor"
    assert manifest["display"] == "standalone"
    assert any(icon["sizes"] == "512x512" for icon in manifest["icons"])


def test_manifest_linked_from_homepage(client):
    resp = client.get("/")
    assert b'rel="manifest"' in resp.data


def test_service_worker_served_at_root_scope(client):
    resp = client.get("/sw.js")
    assert resp.status_code == 200
    assert resp.headers["Service-Worker-Allowed"] == "/"
    assert "javascript" in resp.headers["Content-Type"]


def test_service_worker_never_caches_admin_or_customer_or_api(client):
    resp = client.get("/sw.js")
    body = resp.data.decode()
    assert "/admin" in body
    assert "/customer" in body
    assert "/api" in body
    # The fetch handler must bail out (return, not respondWith) for those paths.
    assert "startsWith(\"/admin\")" in body


def test_robots_txt_disallows_private_areas(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "Disallow: /admin" in body
    assert "Disallow: /customer" in body
    assert "Disallow: /auth" in body
    assert "Disallow: /api" in body
    assert "Sitemap:" in body


def test_sitemap_lists_only_public_pages(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/xml")
    body = resp.data.decode()
    assert "<loc>http://localhost/</loc>" in body
    assert "<loc>http://localhost/services</loc>" in body
    assert "/admin" not in body
    assert "/customer" not in body


def test_security_headers_present_on_every_response(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in resp.headers["Permissions-Policy"]
    csp = resp.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_csp_nonce_matches_inline_script_tag(client):
    resp = client.get("/")
    csp = resp.headers["Content-Security-Policy"]
    nonce = csp.split("nonce-")[1].split("'")[0]
    assert f'nonce="{nonce}"'.encode() in resp.data


def test_csp_nonce_is_fresh_per_request(client):
    nonce_a = client.get("/").headers["Content-Security-Policy"]
    nonce_b = client.get("/").headers["Content-Security-Policy"]
    assert nonce_a != nonce_b


def test_json_ld_local_business_present_on_homepage(client):
    resp = client.get("/")
    body = resp.data.decode()
    assert "application/ld+json" in body
    assert '"@type": "ClothingStore"' in body
    assert "9352672795" in body


def test_open_graph_tags_present(client):
    resp = client.get("/")
    body = resp.data.decode()
    assert 'property="og:title"' in body
    assert 'property="og:image"' in body
    assert 'property="og:url"' in body


def test_apple_touch_icon_served(client):
    resp = client.get("/static/img/icons/apple-touch-icon.png")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "image/png"
