"""Static-ish pages. About has no real story copy yet — shown honestly as
"coming soon" rather than inventing content (master prompt §59)."""
from __future__ import annotations

from flask import render_template
from flask_babel import lazy_gettext as _l

from . import bp

# Real shop/product photos, see app/static/img/services/ and img/shop-storefront.jpg.
GALLERY_PHOTOS = [
    ("shirt_pant_combo.jpg", _l("Shirt + Pant Combo")),
    ("shirt.jpg", _l("Shirt")),
    ("pant.jpg", _l("Pant")),
    ("police_khaaki.jpg", _l("Police Khaaki")),
    ("crpf_khaaki.jpg", _l("CRPF Khaaki")),
    ("crpf_khaaki_dangri.jpg", _l("CRPF Khaaki Dangri")),
    ("crpf_cheetah.jpg", _l("CRPF Cheetah")),
    ("cheetah_us_pattern.jpg", _l("Cheetah US Pattern")),
    ("army_pattern.jpg", _l("Army Pattern")),
]


@bp.get("/about")
def about():
    return render_template("public/about.html")


@bp.get("/gallery")
def gallery():
    return render_template("public/gallery.html", photos=GALLERY_PHOTOS)


@bp.get("/contact")
def contact():
    return render_template("public/contact.html")
