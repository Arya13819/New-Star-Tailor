"""JSON API blueprint.

Admin and customer endpoints are added and individually authorised in later
phases. Phase 1 exposes only the health endpoint.
"""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint("api", __name__)

from . import health  # noqa: E402,F401  (register routes on import)
