"""Customer portal.

Phase 3 ships only the access-gated shell. Orders, measurements and payment
history arrive in Phase 10.
"""
from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user

from ..utils.security import customer_required

bp = Blueprint("customer", __name__, url_prefix="/customer")


@bp.get("/dashboard")
@customer_required
def dashboard():
    return render_template("customer/dashboard.html", user=current_user)
