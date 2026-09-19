"""Walk-in order form (master prompt §41)."""
from __future__ import annotations

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    FieldList,
    FormField,
    IntegerField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange, Optional


class OrderItemForm(FlaskForm):
    class Meta:
        csrf = False  # CSRF is on the parent OrderForm only

    service_id = SelectField(_l("Service"), validators=[DataRequired()])
    quantity = IntegerField(
        _l("Qty"), default=1, validators=[DataRequired(), NumberRange(min=1, max=99)]
    )
    stitching_price = DecimalField(
        _l("Stitching price (₹)"), places=2, rounding=None,
        validators=[DataRequired(), NumberRange(min=0.01)],
    )
    material_price = DecimalField(
        _l("Cloth price (₹)"), places=2, rounding=None, default=0,
        validators=[Optional(), NumberRange(min=0)],
    )


class OrderForm(FlaskForm):
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    fabric_source = SelectField(
        _l("Who provides the cloth?"),
        choices=[("CUSTOMER", _l("Customer brings cloth")), ("SHOP", _l("Shop provides cloth"))],
        validators=[DataRequired()],
    )
    priority = SelectField(
        _l("Priority"),
        choices=[("NORMAL", _l("Normal")), ("URGENT", _l("Urgent"))],
        default="NORMAL",
        validators=[DataRequired()],
    )
    requested_delivery_date = DateField(_l("Customer requested date"), validators=[Optional()])
    confirmed_delivery_date = DateField(_l("Confirmed delivery date"), validators=[Optional()])
    notes = TextAreaField(_l("Notes"), validators=[Optional()])
