"""JSON API blueprint.

Admin and customer endpoints are added and individually authorised in later
phases.
"""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint("api", __name__)

from . import health, payments  # noqa: E402,F401  (register routes on import)
