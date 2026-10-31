"""Public (no-login) pages — one module per area, growing since Phase 11."""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint("public", __name__)

from . import enquiry, home, pages, seo, services, track_order  # noqa: E402,F401
