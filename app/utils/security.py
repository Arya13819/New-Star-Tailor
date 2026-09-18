"""Auth helpers: role-gated view decorators and input normalisation."""
from __future__ import annotations

import re
from functools import wraps

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user

from ..models.enums import UserRole


def normalise_mobile(raw: str) -> str:
    """Keep digits only, last 10 (Indian mobile numbers)."""
    digits = re.sub(r"\D", "", raw or "")
    return digits[-10:] if len(digits) >= 10 else digits


def admin_required(view):
    """Require an authenticated ADMIN. Anyone else is sent to admin login /
    refused with 403 if merely logged in as the wrong role."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_("Please sign in to continue."), "warning")
            return redirect(url_for("auth.admin_login", next=request.path))
        if current_user.role != UserRole.ADMIN:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def customer_required(view):
    """Require an authenticated CUSTOMER (an admin is not a customer account
    and is deliberately not granted access to the customer portal)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_("Please sign in to continue."), "warning")
            return redirect(url_for("auth.customer_login", next=request.path))
        if current_user.role != UserRole.CUSTOMER:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _(text: str) -> str:  # local alias to avoid a circular import at module load
    from flask_babel import gettext

    return gettext(text)


def owned_customer_ids() -> list[int]:
    """Every Customer profile (self + linked family members) the signed-in
    customer account may see. Used to enforce data isolation (master prompt
    §64/§76: one customer must never see another's orders/measurements)."""
    return [c.id for c in current_user.customers]


def safe_next_url(candidate: str | None, default_endpoint: str) -> str:
    """Only follow a same-site relative ``next`` path — never an open redirect."""
    if candidate and candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return url_for(default_endpoint)
