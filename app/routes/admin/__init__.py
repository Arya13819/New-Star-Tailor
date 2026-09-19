"""Admin (shop staff) area.

Split into one module per resource as it grows. Every route in this
blueprint is gated by ``@admin_required``.
"""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import (  # noqa: E402,F401
    customers,
    dashboard,
    enquiries,
    measurements,
    notifications,
    orders,
    payments,
    services,
)
