"""Public service catalogue (stitching prices only — cloth billed separately)."""
from __future__ import annotations

from flask import render_template
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
    by_category = {
        cat: [s for s in rows if s.category == cat] for cat in ServiceCategory
    }
    return render_template(
        "public/services.html",
        by_category=by_category,
        category_labels=CATEGORY_LABELS,
        service_images=SERVICE_IMAGES,
    )
