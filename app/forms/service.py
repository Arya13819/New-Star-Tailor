"""Admin service catalogue form."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp

CATEGORY_CHOICES = [
    ("SHIRT", "Shirt"),
    ("PANT", "Pant"),
    ("POLICE", "Police"),
    ("CRPF", "CRPF"),
    ("ARMY", "Army"),
]


class ServiceForm(FlaskForm):
    code = StringField(
        "Code",
        validators=[
            DataRequired(),
            Length(max=40),
            Regexp(r"^[A-Z0-9_]+$", message="Upper-case letters, digits and underscore only."),
        ],
    )
    name_en = StringField("Name (English)", validators=[DataRequired(), Length(max=120)])
    name_hi = StringField("Name (Hindi)", validators=[Optional(), Length(max=120)])
    category = SelectField("Category", choices=CATEGORY_CHOICES, validators=[DataRequired()])
    default_stitching_price = DecimalField(
        "Stitching price (₹)",
        places=2,
        rounding=None,
        validators=[Optional(), NumberRange(min=0)],
    )
    description = StringField("Description", validators=[Optional(), Length(max=300)])
    sort_order = IntegerField("Sort order", default=100, validators=[Optional()])
    is_active = BooleanField("Active", default=True)
