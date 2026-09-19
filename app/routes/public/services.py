"""Public service catalogue (stitching prices only — cloth billed separately)."""
from __future__ import annotations

from flask import render_template

from ...models.enums import ServiceCategory
from ...models.service import Service
from . import bp


@bp.get("/services")
def services():
    rows = (
        Service.query.filter_by(is_active=True)
        .order_by(Service.category, Service.sort_order)
        .all()
    )
    by_category = {
        cat: [s for s in rows if s.category == cat] for cat in ServiceCategory
    }
    return render_template("public/services.html", by_category=by_category)
