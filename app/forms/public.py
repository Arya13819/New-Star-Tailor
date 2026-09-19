"""Public-facing forms: enquiry, full online order, order tracking."""
from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    FieldList,
    FormField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

from .validators import valid_mobile


class EnquiryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    mobile = StringField("Mobile number", validators=[DataRequired(), valid_mobile])
    address = StringField("Address", validators=[Optional(), Length(max=400)])
    message = TextAreaField("What do you need stitched?", validators=[Optional(), Length(max=2000)])


class OnlineOrderItemForm(FlaskForm):
    class Meta:
        csrf = False

    service_id = SelectField("Service", validators=[DataRequired()])
    quantity = IntegerField(
        "Qty", default=1, validators=[DataRequired(), NumberRange(min=1, max=99)]
    )


_INCH = lambda label: DecimalField(  # noqa: E731
    label, places=2, rounding=None, validators=[Optional()]
)


class OnlineOrderForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    mobile = StringField("Mobile number", validators=[DataRequired(), valid_mobile])
    address = StringField("Address", validators=[Optional(), Length(max=400)])

    items = FieldList(FormField(OnlineOrderItemForm), min_entries=1)
    fabric_source = SelectField(
        "Who provides the cloth?",
        choices=[("CUSTOMER", "I will bring my own cloth"), ("SHOP", "Shop provides the cloth")],
        validators=[DataRequired()],
    )
    requested_delivery_date = DateField("Preferred delivery date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])

    provide_measurements = BooleanField("I want to submit my own measurements")
    shirt_length = _INCH("Shirt length")
    shirt_chest = _INCH("Chest")
    shirt_shoulder = _INCH("Shoulder")
    shirt_sleeves = _INCH("Sleeves")
    shirt_neck = _INCH("Neck")
    pant_length = _INCH("Pant length")
    pant_waist = _INCH("Waist")
    pant_hips = _INCH("Hips")
    pant_mori = _INCH("Mori / pant end")
    fitting_preference = SelectField(
        "Fitting preference",
        choices=[("", "—"), ("LOOSE", "Loose"), ("NORMAL", "Normal"), ("SLIM", "Slim")],
        validators=[Optional()],
    )
    allowance = StringField("Allowance", validators=[Optional(), Length(max=120)])
    measurement_ack = BooleanField(
        "I confirm these measurements are accurate. New Star Tailor is not "
        "responsible for fit issues caused by measurements I provided myself."
    )

    reference_image = FileField(
        "Reference photo (optional)",
        validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only.")],
    )
    payment_reference = StringField(
        "UPI/payment reference, if you've already paid the advance", validators=[Optional(), Length(max=190)]
    )

    def validate_measurement_ack(self, field) -> None:  # noqa: ANN001
        if self.provide_measurements.data and not field.data:
            raise ValidationError(
                "Please confirm the measurement acknowledgement, or leave "
                "measurements to be taken at the shop."
            )


class TrackOrderForm(FlaskForm):
    order_number = StringField("Order number", validators=[DataRequired(), Length(max=20)])
    mobile = StringField("Mobile number", validators=[DataRequired(), valid_mobile])
