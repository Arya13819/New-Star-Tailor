"""Public (no-login) pages.

Phase 1 ships the homepage shell, a language switch, and the operational
health check. Services, enquiry, ordering and tracking arrive in later phases.
"""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for

from ..config import Config

bp = Blueprint("public", __name__)


@bp.get("/")
def home():
    return render_template("public/index.html")


@bp.get("/healthz")
def healthz():
    """Lightweight liveness probe (no database access)."""
    return {"status": "ok", "service": "new-star-tailor"}


@bp.get("/set-language/<lang>")
def set_language(lang: str):
    if lang in Config.LANGUAGES:
        session["lang"] = lang
    return redirect(request.referrer or url_for("public.home"))
