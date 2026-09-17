"""Placeholder dashboard — real content arrives in Phase 9."""
from __future__ import annotations

from flask import render_template
from flask_login import current_user

from ...utils.security import admin_required
from . import bp


@bp.get("/dashboard")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", user=current_user)
