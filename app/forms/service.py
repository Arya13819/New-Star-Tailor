"""Admin service catalogue form."""
from __future__ import annotations

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp

CATEGORY_CHOICES = [
    ("SHIRT", _l("Shirt")),
    ("PANT", _l("Pant")),
    ("POLICE", _l("Police")),
    ("CRPF", _l("CRPF")),
    ("ARMY", _l("Army")),
]


class ServiceForm(FlaskForm):
    code = StringField(
        _l("Code"),
        validators=[
            DataRequired(),
            Length(max=40),
            Regexp(r"^[A-Z0-9_]+$", message=_l("Upper-case letters, digits and underscore only.")),
        ],
    )
    name_en = StringField(_l("Name (English)"), validators=[DataRequired(), Length(max=120)])
    name_hi = StringField(_l("Name (Hindi)"), validators=[Optional(), Length(max=120)])
    category = SelectField(_l("Category"), choices=CATEGORY_CHOICES, validators=[DataRequired()])
    default_stitching_price = DecimalField(
        _l("Stitching price (₹)"),
        places=2,
        rounding=None,
        validators=[Optional(), NumberRange(min=0)],
    )
    description = StringField(_l("Description"), validators=[Optional(), Length(max=300)])
    sort_order = IntegerField(_l("Sort order"), default=100, validators=[Optional()])
    is_active = BooleanField(_l("Active"), default=True)
