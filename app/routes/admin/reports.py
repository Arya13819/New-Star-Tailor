"""Admin reports (Phase 14)."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from flask import render_template, request

from ...models.base import utcnow
from ...services import report_service
from ...utils.security import admin_required
from . import bp


def _resolve_range(range_key: str, from_str: str, to_str: str) -> tuple[datetime, datetime, str]:
    now = utcnow()
    if range_key == "today":
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1)
    elif range_key == "week":
        start = now - timedelta(days=7)
        end = now
    elif range_key == "custom" and from_str and to_str:
        try:
            start = datetime.fromisoformat(from_str)
            end = datetime.fromisoformat(to_str) + timedelta(days=1)
        except ValueError:
            start, end = now - timedelta(days=30), now
            range_key = "month"
    else:
        start = now - timedelta(days=30)
        end = now
        range_key = "month"
    return start, end, range_key


@bp.get("/reports")
@admin_required
def reports():
    range_key = request.args.get("range", "month")
    from_str = request.args.get("from", "")
    to_str = request.args.get("to", "")
    start, end, range_key = _resolve_range(range_key, from_str, to_str)

    data = report_service.summary(start, end)
    pending = report_service.pending_payments()

    return render_template(
        "admin/reports/index.html",
        data=data,
        pending=pending,
        range_key=range_key,
        from_str=from_str or date.today().isoformat(),
        to_str=to_str or date.today().isoformat(),
    )
