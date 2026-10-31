"""Public service catalogue (stitching prices only — cloth billed separately)."""
from __future__ import annotations

from flask import render_template, request
from flask_babel import lazy_gettext as _l

from ...models.enums import ServiceCategory
from ...models.service import Service
from . import bp

CATEGORY_LABELS = {
    ServiceCategory.SHIRT: _l("Shirt"),
    ServiceCategory.PANT: _l("Pant"),
    ServiceCategory.POLICE: _l("Police"),
    ServiceCategory.CRPF: _l("CRPF"),
    ServiceCategory.ARMY: _l("Army"),
}

# Static product photos, matched by Service.code (see app/static/img/services/).
SERVICE_IMAGES = {
    "SHIRT": "shirt.jpg",
    "PANT": "pant.jpg",
    "SHIRT_PANT_COMBO": "shirt_pant_combo.jpg",
    "POLICE_KHAAKI": "police_khaaki.jpg",
    "CRPF_KHAAKI": "crpf_khaaki.jpg",
    "CRPF_CHEETAH": "crpf_cheetah.jpg",
    "CRPF_KHAAKI_DANGRI": "crpf_khaaki_dangri.jpg",
    "ARMY_PATTERN": "army_pattern.jpg",
    "CHEETAH_US_PATTERN": "cheetah_us_pattern.jpg",
}


@bp.get("/services")
def services():
    rows = (
        Service.query.filter_by(is_active=True)
        .order_by(Service.category, Service.sort_order)
        .all()
    )
    selected_category = request.args.get("category", "ALL").upper()
    if selected_category not in {"ALL", *(cat.value for cat in ServiceCategory)}:
        selected_category = "ALL"
    search = request.args.get("q", "").strip()[:80]
    matching = [
        s for s in rows
        if (selected_category == "ALL" or s.category.value == selected_category)
        and (not search or search.casefold() in " ".join(
            str(value or "") for value in (s.name_en, s.name_hi, s.code, s.description)
        ).casefold())
    ]
    counts = {cat: sum(s.category == cat for s in rows) for cat in ServiceCategory}
    return render_template(
        "public/services.html",
        services=matching,
        categories=CATEGORY_LABELS,
        category_counts=counts,
        total_services=len(rows),
        selected_category=selected_category,
        search=search,
        service_images=SERVICE_IMAGES,
    )
