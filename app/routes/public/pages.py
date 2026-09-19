"""Static-ish pages. About/gallery have no real copy or photos yet — shown
honestly as "coming soon" rather than inventing content (master prompt §59)."""
from __future__ import annotations

from flask import render_template

from . import bp


@bp.get("/about")
def about():
    return render_template("public/about.html")


@bp.get("/gallery")
def gallery():
    return render_template("public/gallery.html")


@bp.get("/contact")
def contact():
    return render_template("public/contact.html")
