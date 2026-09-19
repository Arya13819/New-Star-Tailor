"""Homepage, health check, language switch."""
from __future__ import annotations

from flask import redirect, render_template, request, session, url_for

from ...config import Config
from . import bp


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
