"""Walk-in order form (master prompt §41)."""
from __future__ import annotations

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

    service_id = SelectField("Service", validators=[DataRequired()])
    quantity = IntegerField(
        "Qty", default=1, validators=[DataRequired(), NumberRange(min=1, max=99)]
    )
    stitching_price = DecimalField(
        "Stitching price (₹)", places=2, rounding=None, validators=[DataRequired(), NumberRange(min=0.01)]
    )
    material_price = DecimalField(
        "Cloth price (₹)", places=2, rounding=None, default=0,
        validators=[Optional(), NumberRange(min=0)],
    )


class OrderForm(FlaskForm):
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    fabric_source = SelectField(
        "Who provides the cloth?",
        choices=[("CUSTOMER", "Customer brings cloth"), ("SHOP", "Shop provides cloth")],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "Priority",
        choices=[("NORMAL", "Normal"), ("URGENT", "Urgent")],
        default="NORMAL",
        validators=[DataRequired()],
    )
    requested_delivery_date = DateField("Customer requested date", validators=[Optional()])
    confirmed_delivery_date = DateField("Confirmed delivery date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
