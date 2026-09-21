"""Homepage, health check, language switch."""
from __future__ import annotations

from flask import (
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from ...config import Config
from . import bp


@bp.get("/")
def home():
    return render_template("public/index.html")


@bp.get("/sw.js")
def service_worker():
    # Served from the root (not /static/) so its default scope covers the
    # whole site, not just /static/ — required for it to control page
    # navigations like "/", "/services", etc.
    response = send_from_directory(current_app.static_folder, "sw.js", mimetype="text/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@bp.get("/healthz")
def healthz():
    """Lightweight liveness probe (no database access)."""
    return {"status": "ok", "service": "new-star-tailor"}


@bp.get("/set-language/<lang>")
def set_language(lang: str):
    if lang in Config.LANGUAGES:
        session["lang"] = lang
    return redirect(request.referrer or url_for("public.home"))
