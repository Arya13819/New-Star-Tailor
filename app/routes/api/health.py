"""Health / readiness endpoint."""
from __future__ import annotations

from flask import current_app, jsonify
from sqlalchemy import text

from ... import __version__
from ...config import Config
from ...extensions import db
from . import bp


@bp.get("/health")
def health():
    """Readiness probe.

    Reports app version, whether the database is reachable, and whether the
    optional payment / messaging integrations are configured. Never fabricates
    an "ok" for something that is not actually wired up.
    """
    db_ok = False
    db_error = None
    try:
        db.session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # noqa: BLE001 - report, don't crash the probe
        db_error = type(exc).__name__
        current_app.logger.warning("Health check: database unreachable (%s)", db_error)

    payload = {
        "service": "new-star-tailor",
        "version": __version__,
        "status": "ok" if db_ok else "degraded",
        "database": {"connected": db_ok, "error": db_error},
        "integrations": {
            "payments_configured": Config.payments_configured(),
            "messaging_configured": Config.messaging_configured(),
        },
    }
    return jsonify(payload), 200 if db_ok else 503
