"""Admin-side customer create/edit form."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from .validators import valid_mobile


class CustomerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    mobile = StringField("Mobile number", validators=[DataRequired(), valid_mobile])
    address = TextAreaField("Address", validators=[Optional(), Length(max=400)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
