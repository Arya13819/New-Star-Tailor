"""Record-a-payment form (master prompt §20-22)."""
from __future__ import annotations

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PaymentForm(FlaskForm):
    amount = DecimalField(
        _l("Amount (₹)"), places=2, rounding=None,
        validators=[DataRequired(), NumberRange(min=0.01)],
    )
    method = SelectField(
        _l("Method"),
        choices=[("CASH", _l("Cash")), ("UPI", _l("UPI")), ("ONLINE", _l("Online"))],
        validators=[DataRequired()],
    )
    transaction_reference = StringField(
        _l("Transaction reference"), validators=[Optional(), Length(max=190)]
    )
    note = StringField(_l("Note"), validators=[Optional(), Length(max=300)])
