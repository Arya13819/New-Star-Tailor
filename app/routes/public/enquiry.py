"""Public enquiry + complete online order (master prompt §14)."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user

from ...extensions import db
from ...forms.public import EnquiryForm, OnlineOrderForm
from ...models.enums import FabricSource, OrderPriority, OrderSource, PaymentMethod, UserRole
from ...models.reference_image import ReferenceImage
from ...models.service import Service
from ...services import (
    customer_service,
    enquiry_service,
    measurement_service,
    order_service,
    payment_service,
)
from ...services.order_service import OrderError
from ...utils.uploads import UploadError, save_reference_image
from . import bp

_MEASURE_FIELDS = [
    "shirt_length", "shirt_chest", "shirt_shoulder", "shirt_sleeves", "shirt_neck",
    "pant_length", "pant_waist", "pant_hips", "pant_mori",
]


def _decimal_or_none(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def _priced_services() -> list[Service]:
    return (
        Service.query.filter(
            Service.is_active.is_(True), Service.default_stitching_price.isnot(None)
        )
        .order_by(Service.category, Service.sort_order)
        .all()
    )


@bp.route("/enquiry", methods=["GET", "POST"])
def enquiry():
    form = EnquiryForm()
    if form.validate_on_submit():
        enquiry_service.create_enquiry(
            name=form.name.data,
            mobile=form.mobile.data,
            address=form.address.data,
            message=form.message.data,
        )
        flash(_("Thank you. We have received your enquiry and will contact you soon."), "success")
        return redirect(url_for("public.enquiry"))
    return render_template("public/enquiry.html", form=form)


@bp.route("/order", methods=["GET", "POST"])
def order():
    services = _priced_services()
    choices = [
        (str(s.id), f"{s.name_en} — ₹{s.default_stitching_price:.2f}") for s in services
    ]
    form = OnlineOrderForm()
    for item_form in form.items:
        item_form.service_id.choices = choices

    if not services:
        if form.is_submitted():
            flash(_("Online ordering is temporarily unavailable — please call the shop."), "error")
        return render_template("public/order.html", form=form, services=services)

    if form.validate_on_submit():
        # Find or reuse the customer profile.
        if current_user.is_authenticated and current_user.role == UserRole.CUSTOMER:
            profile = current_user.customers[0] if current_user.customers else None
            if profile is None:
                profile = customer_service.create_customer(
                    name=form.name.data, mobile=form.mobile.data,
                    address=form.address.data, notes=None, actor_id=None,
                )
                profile.user_id = current_user.id
                db.session.commit()
        else:
            profile = customer_service.create_customer(
                name=form.name.data, mobile=form.mobile.data,
                address=form.address.data, notes=None, actor_id=None,
            )

        self_ack = False
        if form.provide_measurements.data:
            data = {key: _decimal_or_none(getattr(form, key).data) for key in _MEASURE_FIELDS}
            data["fitting_preference"] = form.fitting_preference.data or None
            data["allowance"] = form.allowance.data or None
            data["notes"] = None
            data["alteration_notes"] = None
            data["source"] = "CUSTOMER"
            measurement_service.add_version(profile, data, actor_id=None)
            self_ack = True

        by_id = {s.id: s for s in services}
        items_data = []
        for item_form in form.items:
            service = by_id.get(int(item_form.service_id.data))
            if service is None:
                continue
            items_data.append(
                {
                    "service_id": service.id,
                    "service_name": service.name_en,
                    "category": service.category,
                    "quantity": item_form.quantity.data,
                    "stitching_price": service.default_stitching_price,
                    # Material for shop-supplied cloth needs a fabric chosen in
                    # person — staff confirm and add it when they call back.
                    "material_price": 0,
                }
            )

        try:
            new_order = order_service.create_order(
                customer=profile,
                items=items_data,
                fabric_source=FabricSource(form.fabric_source.data),
                priority=OrderPriority.NORMAL,
                requested_delivery_date=form.requested_delivery_date.data,
                notes=form.notes.data,
                actor_id=None,
                source=OrderSource.WEBSITE,
                self_measurement_acknowledged=self_ack,
            )
        except OrderError as exc:
            flash(str(exc), "error")
            return render_template("public/order.html", form=form, services=services)

        if form.reference_image.data:
            try:
                meta = save_reference_image(form.reference_image.data)
                db.session.add(ReferenceImage(order_id=new_order.id, **meta))
                db.session.commit()
            except UploadError as exc:
                flash(str(exc), "warning")

        if form.payment_reference.data and new_order.required_advance > 0:
            payment_service.record_payment(
                order=new_order,
                amount=new_order.required_advance,
                method=PaymentMethod.ONLINE,
                transaction_reference=form.payment_reference.data,
                note="Submitted via the online order form — pending verification.",
                actor_id=None,
            )

        # Rendered directly (not a redirect keyed by a guessable order id) so
        # order details are only ever shown to the browser that just placed
        # the order — never to anyone who might enumerate an id.
        return render_template("public/order_success.html", order=new_order)

    return render_template("public/order.html", form=form, services=services)
