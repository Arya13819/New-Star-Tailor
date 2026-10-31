"""Security response headers + a per-request CSP nonce (master prompt §17
hardening pass). The nonce lets the handful of inline <script> blocks the
UI needs (service-worker registration, the order-form item rows, the JSON-LD
business listing) run under a strict script-src without 'unsafe-inline'.
"""
from __future__ import annotations

import secrets

from flask import Flask, g, request


def register_security_headers(app: Flask) -> None:
    @app.before_request
    def _make_csp_nonce() -> None:
        g.csp_nonce = secrets.token_urlsafe(16)

    @app.context_processor
    def _inject_csp_nonce() -> dict:
        return {"csp_nonce": g.get("csp_nonce", "")}

    @app.after_request
    def _set_security_headers(response):
        nonce = g.get("csp_nonce", "")
        csp = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            # Inline style="" attributes are used throughout the templates for
            # small one-off layout tweaks; nonces don't cover style attributes,
            # so this is the pragmatic middle ground rather than a full CSS rewrite.
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers.setdefault("Content-Security-Policy", csp)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )
        if request.is_secure:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response
