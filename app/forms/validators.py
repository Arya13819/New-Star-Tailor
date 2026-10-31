"""Shared WTForms validators."""
from __future__ import annotations

from datetime import date

from flask_babel import gettext as _
from wtforms.validators import ValidationError

from ..utils.security import normalise_mobile


def valid_mobile(form, field) -> None:  # noqa: ANN001 - WTForms validator signature
    if len(normalise_mobile(field.data or "")) != 10:
        raise ValidationError(_("Enter a valid 10-digit mobile number."))


def not_in_the_past(form, field) -> None:  # noqa: ANN001 - WTForms validator signature
    """Only for dates entered when an order is first created — never attach
    this to a field that re-submits an already-stored date on later edits,
    since a legitimately old delivery date would then block unrelated
    changes (e.g. editing notes) once that date has simply passed."""
    if field.data and field.data < date.today():
        raise ValidationError(_("That date is in the past."))
