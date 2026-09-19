"""Customer portal (Phase 10).

Every view here is scoped to the signed-in customer's own profiles
(``owned_customer_ids()``) — never trusts an id from the URL alone. Someone
else's order/measurement is a 404, not a 403, so a guessed id doesn't even
confirm it exists (master prompt §35/§64/§76: no cross-customer data leaks).
"""
from __future__ import annotations

from flask import Blueprint, abort, current_app, render_template, send_from_directory
from flask_login import current_user

from ..extensions import db
from ..models.order import Order
from ..models.payment import Payment
from ..models.reference_image import ReferenceImage
from ..services import payment_service
from ..utils.measurement_fields import PANT_FIELDS, SHIRT_FIELDS
from ..utils.security import customer_required, owned_customer_ids

bp = Blueprint("customer", __name__, url_prefix="/customer")


@bp.get("/dashboard")
@customer_required
def dashboard():
    owned = owned_customer_ids()
    orders = (
        Order.query.filter(Order.customer_id.in_(owned))
        .order_by(Order.created_at.desc())
        .all()
        if owned
        else []
    )
    open_orders = [o for o in orders if o.status.value != "DELIVERED"]
    outstanding = sum(
        (payment_service.balance_for_order(o) for o in orders), start=0
    )
    return render_template(
        "customer/dashboard.html",
        user=current_user,
        profiles=current_user.customers,
        recent_orders=orders[:5],
        open_count=len(open_orders),
        outstanding=outstanding,
    )


@bp.get("/orders")
@customer_required
def orders():
    owned = owned_customer_ids()
    rows = (
        Order.query.filter(Order.customer_id.in_(owned))
        .order_by(Order.created_at.desc())
        .all()
        if owned
        else []
    )
    with_balance = [(o, payment_service.balance_for_order(o)) for o in rows]
    return render_template("customer/orders.html", orders=with_balance)


@bp.get("/orders/<int:order_id>")
@customer_required
def order_detail(order_id: int):
    order = db.session.get(Order, order_id)
    if order is None or order.customer_id not in owned_customer_ids():
        abort(404)
    paid = payment_service.paid_for_order(order.id)
    balance = payment_service.balance_for_order(order)
    return render_template(
        "customer/order_detail.html", order=order, paid=paid, balance=balance
    )


@bp.get("/orders/<int:order_id>/receipt")
@customer_required
def order_receipt(order_id: int):
    order = db.session.get(Order, order_id)
    if order is None or order.customer_id not in owned_customer_ids():
        abort(404)
    paid = payment_service.paid_for_order(order.id)
    balance = payment_service.balance_for_order(order)
    return render_template("receipts/order_receipt.html", order=order, paid=paid, balance=balance)


@bp.get("/orders/<int:order_id>/images/<int:image_id>")
@customer_required
def order_image(order_id: int, image_id: int):
    order = db.session.get(Order, order_id)
    if order is None or order.customer_id not in owned_customer_ids():
        abort(404)
    image = db.session.get(ReferenceImage, image_id)
    if image is None or image.order_id != order_id:
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_DIR"], image.storage_path)


@bp.get("/measurements")
@customer_required
def measurements():
    return render_template(
        "customer/measurements.html",
        profiles=current_user.customers,
        shirt_fields=SHIRT_FIELDS,
        pant_fields=PANT_FIELDS,
    )


@bp.get("/payments")
@customer_required
def payments():
    owned = owned_customer_ids()
    rows = (
        Payment.query.filter(Payment.customer_id.in_(owned))
        .order_by(Payment.created_at.desc())
        .all()
        if owned
        else []
    )
    return render_template("customer/payments.html", payments=rows)
