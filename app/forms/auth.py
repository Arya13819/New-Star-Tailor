"""Login / registration forms."""
from __future__ import annotations

from flask_babel import gettext
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from .validators import valid_mobile


class AdminLoginForm(FlaskForm):
    identifier = StringField(
        _l("Email or mobile"), validators=[DataRequired(), Length(max=190)]
    )
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember = BooleanField(_l("Keep me signed in"))


class CustomerLoginForm(FlaskForm):
    mobile = StringField(
        _l("Mobile number"), validators=[DataRequired(), valid_mobile]
    )
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember = BooleanField(_l("Keep me signed in"))


class CustomerRegisterForm(FlaskForm):
    name = StringField(_l("Full name"), validators=[DataRequired(), Length(max=120)])
    mobile = StringField(
        _l("Mobile number"), validators=[DataRequired(), valid_mobile]
    )
    address = StringField(_l("Address"), validators=[Optional(), Length(max=400)])
    password = PasswordField(
        _l("Password"), validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        _l("Confirm password"), validators=[DataRequired()]
    )

    def validate_confirm_password(self, field) -> None:  # noqa: ANN001
        if field.data != self.password.data:
            raise ValidationError(gettext("Passwords do not match."))
