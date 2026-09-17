"""Admin measurement versioning (Phase 5)."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user

from ...forms.measurement import MeasurementForm
from ...repositories import customer_repo
from ...services import measurement_service
from ...utils.security import admin_required
from . import bp

_NUMERIC_FIELDS = [
    "shirt_length",
    "shirt_chest",
    "shirt_shoulder",
    "shirt_sleeves",
    "shirt_neck",
    "pant_length",
    "pant_waist",
    "pant_hips",
    "pant_mori",
]


def _decimal_or_none(value) -> Decimal | None:  # noqa: ANN001
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


@bp.route("/customers/<int:customer_id>/measurements/new", methods=["GET", "POST"])
@admin_required
def measurement_new(customer_id: int):
    customer = customer_repo.get_or_404(customer_id)
    form = MeasurementForm()

    current = customer.measurement.current_version if customer.measurement else None
    if current and not form.is_submitted():
        # Pre-fill with the last recorded values so the operator only edits
        # what actually changed for a repeat customer.
        for key in _NUMERIC_FIELDS:
            getattr(form, key).data = getattr(current, key)
        form.fitting_preference.data = (
            current.fitting_preference.value if current.fitting_preference else ""
        )
        form.allowance.data = current.allowance

    if form.validate_on_submit():
        data = {key: _decimal_or_none(getattr(form, key).data) for key in _NUMERIC_FIELDS}
        data["fitting_preference"] = form.fitting_preference.data or None
        data["allowance"] = form.allowance.data or None
        data["notes"] = form.notes.data or None
        data["alteration_notes"] = form.alteration_notes.data or None
        data["source"] = form.source.data

        version = measurement_service.add_version(customer, data, actor_id=current_user.id)
        flash(_("Saved as version {n}.").format(n=version.version_number), "success")
        return redirect(url_for("admin.customer_detail", customer_id=customer.id))

    return render_template("admin/customers/measurement_form.html", form=form, customer=customer)
