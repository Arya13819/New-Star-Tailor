"""Admin visibility into the notification queue (Phase 13)."""
from __future__ import annotations

from flask import render_template, request

from ...config import Config
from ...services import notification_service
from ...utils.security import admin_required
from . import bp


@bp.get("/notifications")
@admin_required
def notification_list():
    status = request.args.get("status", "").upper() or None
    rows = notification_service.notifications_query(status).limit(100).all()
    return render_template(
        "admin/notifications/list.html",
        notifications=rows,
        status=status,
        messaging_configured=Config.messaging_configured(),
    )
