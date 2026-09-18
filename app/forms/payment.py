"""Record-a-payment form (master prompt §20-22)."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PaymentForm(FlaskForm):
    amount = DecimalField(
        "Amount (₹)", places=2, rounding=None, validators=[DataRequired(), NumberRange(min=0.01)]
    )
    method = SelectField(
        "Method",
        choices=[("CASH", "Cash"), ("UPI", "UPI"), ("ONLINE", "Online")],
        validators=[DataRequired()],
    )
    transaction_reference = StringField(
        "Transaction reference", validators=[Optional(), Length(max=190)]
    )
    note = StringField("Note", validators=[Optional(), Length(max=300)])
