"""Admin (shop staff) area.

Phase 3 ships only the access-gated shell. The real dashboard (status
counts, quick actions, recent orders) arrives in Phase 9.
"""
from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user

from ..utils.security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/dashboard")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", user=current_user)
