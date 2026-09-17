"""Measurement version form (inches, per master prompt §8)."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, TextAreaField
from wtforms.validators import Length, Optional


def _inches(label: str) -> DecimalField:
    return DecimalField(
        label, places=2, rounding=None, validators=[Optional()],
    )


class MeasurementForm(FlaskForm):
    # Shirt
    shirt_length = _inches("Length")
    shirt_chest = _inches("Chest")
    shirt_shoulder = _inches("Shoulder")
    shirt_sleeves = _inches("Sleeves")
    shirt_neck = _inches("Neck")

    # Pant
    pant_length = _inches("Length")
    pant_waist = _inches("Waist")
    pant_hips = _inches("Hips")
    pant_mori = _inches("Mori / pant end")

    fitting_preference = SelectField(
        "Fitting preference",
        choices=[("", "—"), ("LOOSE", "Loose"), ("NORMAL", "Normal"), ("SLIM", "Slim")],
        validators=[Optional()],
    )
    allowance = StringField("Allowance", validators=[Optional(), Length(max=120)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
    alteration_notes = TextAreaField(
        "Alteration notes", validators=[Optional(), Length(max=2000)]
    )
    source = SelectField(
        "Taken by",
        choices=[("SHOP", "Shop (in person)"), ("CUSTOMER", "Customer (self-submitted)")],
        default="SHOP",
    )
