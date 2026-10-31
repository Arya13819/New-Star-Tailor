"""Measurement version form (inches, per master prompt §8)."""
from __future__ import annotations

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, TextAreaField
from wtforms.validators import Length, Optional


def _inches(label) -> DecimalField:  # noqa: ANN001
    return DecimalField(
        label, places=2, rounding=None, validators=[Optional()],
    )


class MeasurementForm(FlaskForm):
    # Shirt
    shirt_length = _inches(_l("Length"))
    shirt_chest = _inches(_l("Chest"))
    shirt_shoulder = _inches(_l("Shoulder"))
    shirt_sleeves = _inches(_l("Sleeves"))
    shirt_neck = _inches(_l("Neck"))

    # Pant
    pant_length = _inches(_l("Length"))
    pant_waist = _inches(_l("Waist"))
    pant_hips = _inches(_l("Hips"))
    pant_mori = _inches(_l("Mori / pant end"))

    fitting_preference = SelectField(
        _l("Fitting preference"),
        choices=[("", "—"), ("LOOSE", _l("Loose")), ("NORMAL", _l("Normal")), ("SLIM", _l("Slim"))],
        validators=[Optional()],
    )
    allowance = StringField(_l("Allowance"), validators=[Optional(), Length(max=120)])
    notes = TextAreaField(_l("Notes"), validators=[Optional(), Length(max=2000)])
    alteration_notes = TextAreaField(
        _l("Alteration notes"), validators=[Optional(), Length(max=2000)]
    )
    source = SelectField(
        _l("Taken by"),
        choices=[("SHOP", _l("Shop (in person)")), ("CUSTOMER", _l("Customer (self-submitted)"))],
        default="SHOP",
    )
