"""Shared WTForms validators."""
from __future__ import annotations

from flask_babel import gettext as _
from wtforms.validators import ValidationError

from ..utils.security import normalise_mobile


def valid_mobile(form, field) -> None:  # noqa: ANN001 - WTForms validator signature
    if len(normalise_mobile(field.data or "")) != 10:
        raise ValidationError(_("Enter a valid 10-digit mobile number."))
