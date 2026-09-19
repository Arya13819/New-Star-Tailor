"""Public order tracking by order number + mobile (master prompt §35).

Rate-limited and deliberately vague on failure — "not found" either way,
never "wrong mobile for that order" (which would confirm the order exists).
"""
from __future__ import annotations

from flask import render_template

from ...extensions import limiter
from ...forms.public import TrackOrderForm
from ...models.order import Order
from ...services import payment_service
from ...utils.security import normalise_mobile
from . import bp


@bp.route("/track-order", methods=["GET", "POST"])
@limiter.limit("20 per minute", methods=["POST"])
def track_order():
    form = TrackOrderForm()
    result = None
    not_found = False

    if form.validate_on_submit():
        number = form.order_number.data.strip().upper()
        mobile = normalise_mobile(form.mobile.data)
        candidate = Order.query.filter_by(order_number=number).first()
        if candidate and normalise_mobile(candidate.customer.mobile) == mobile:
            result = {
                "order": candidate,
                "balance": payment_service.balance_for_order(candidate),
                "paid": payment_service.paid_for_order(candidate.id),
            }
        else:
            not_found = True

    return render_template(
        "public/track_order.html", form=form, result=result, not_found=not_found
    )
