"""Login / registration forms."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from ..utils.security import normalise_mobile


def _valid_mobile(form, field) -> None:  # noqa: ANN001
    if len(normalise_mobile(field.data)) != 10:
        raise ValidationError("Enter a valid 10-digit mobile number.")


class AdminLoginForm(FlaskForm):
    identifier = StringField(
        "Email or mobile", validators=[DataRequired(), Length(max=190)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")


class CustomerLoginForm(FlaskForm):
    mobile = StringField(
        "Mobile number", validators=[DataRequired(), _valid_mobile]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")


class CustomerRegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    mobile = StringField(
        "Mobile number", validators=[DataRequired(), _valid_mobile]
    )
    address = StringField("Address", validators=[Optional(), Length(max=400)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired()]
    )

    def validate_confirm_password(self, field) -> None:  # noqa: ANN001
        if field.data != self.password.data:
            raise ValidationError("Passwords do not match.")
