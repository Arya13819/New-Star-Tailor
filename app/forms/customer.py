"""Admin-side customer create/edit form."""
from __future__ import annotations

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from .validators import valid_mobile


class CustomerForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(max=120)])
    mobile = StringField(_l("Mobile number"), validators=[DataRequired(), valid_mobile])
    address = TextAreaField(_l("Address"), validators=[Optional(), Length(max=400)])
    notes = TextAreaField(_l("Notes"), validators=[Optional(), Length(max=2000)])
