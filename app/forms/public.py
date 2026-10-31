"""Public-facing forms: enquiry, full online order, order tracking."""
from __future__ import annotations

from flask_babel import gettext
from flask_babel import lazy_gettext as _l
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

from .validators import not_in_the_past, valid_mobile


class EnquiryForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(max=120)])
    mobile = StringField(_l("Mobile number"), validators=[DataRequired(), valid_mobile])
    address = StringField(_l("Address"), validators=[Optional(), Length(max=400)])
    message = TextAreaField(
        _l("What do you need stitched?"), validators=[Optional(), Length(max=2000)]
    )


class OnlineOrderItemForm(FlaskForm):
    class Meta:
        csrf = False

    service_id = SelectField(_l("Service"), validators=[DataRequired()])
    quantity = IntegerField(
        _l("Qty"), default=1, validators=[DataRequired(), NumberRange(min=1, max=99)]
    )


def _inch(label) -> DecimalField:  # noqa: ANN001
    return DecimalField(label, places=2, rounding=None, validators=[Optional()])


class OnlineOrderForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(max=120)])
    mobile = StringField(_l("Mobile number"), validators=[DataRequired(), valid_mobile])
    address = StringField(_l("Address"), validators=[Optional(), Length(max=400)])

    items = FieldList(FormField(OnlineOrderItemForm), min_entries=1)
    fabric_source = SelectField(
        _l("Who provides the cloth?"),
        choices=[
            ("CUSTOMER", _l("I will bring my own cloth")),
            ("SHOP", _l("Shop provides the cloth")),
        ],
        validators=[DataRequired()],
    )
    requested_delivery_date = DateField(
        _l("Preferred delivery date"), validators=[Optional(), not_in_the_past]
    )
    notes = TextAreaField(_l("Notes"), validators=[Optional(), Length(max=2000)])

    provide_measurements = BooleanField(_l("I want to submit my own measurements"))
    shirt_length = _inch(_l("Shirt length"))
    shirt_chest = _inch(_l("Chest"))
    shirt_shoulder = _inch(_l("Shoulder"))
    shirt_sleeves = _inch(_l("Sleeves"))
    shirt_neck = _inch(_l("Neck"))
    pant_length = _inch(_l("Pant length"))
    pant_waist = _inch(_l("Waist"))
    pant_hips = _inch(_l("Hips"))
    pant_mori = _inch(_l("Mori / pant end"))
    fitting_preference = SelectField(
        _l("Fitting preference"),
        choices=[("", "—"), ("LOOSE", _l("Loose")), ("NORMAL", _l("Normal")), ("SLIM", _l("Slim"))],
        validators=[Optional()],
    )
    allowance = StringField(_l("Allowance"), validators=[Optional(), Length(max=120)])
    measurement_ack = BooleanField(
        _l(
            "I confirm these measurements are accurate. New Star Tailor is not "
            "responsible for fit issues caused by measurements I provided myself."
        )
    )

    reference_image = FileField(
        _l("Reference photo (optional)"),
        validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], _l("Images only."))],
    )
    payment_reference = StringField(
        _l("UPI/payment reference, if you've already paid the advance"),
        validators=[Optional(), Length(max=190)],
    )
    payment_amount = DecimalField(
        _l("Amount you paid (₹)"),
        places=2, rounding=None,
        validators=[Optional(), NumberRange(min=0.01)],
    )

    def validate_payment_amount(self, field) -> None:  # noqa: ANN001
        if self.payment_reference.data and field.data is None:
            raise ValidationError(
                gettext("Please enter the amount you paid, so we can match it to your reference.")
            )

    def validate_measurement_ack(self, field) -> None:  # noqa: ANN001
        if self.provide_measurements.data and not field.data:
            raise ValidationError(
                gettext(
                    "Please confirm the measurement acknowledgement, or leave "
                    "measurements to be taken at the shop."
                )
            )


class TrackOrderForm(FlaskForm):
    order_number = StringField(_l("Order number"), validators=[DataRequired(), Length(max=20)])
    mobile = StringField(_l("Mobile number"), validators=[DataRequired(), valid_mobile])
