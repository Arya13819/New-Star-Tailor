"""Admin order management (Phase 7)."""
from __future__ import annotations

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_babel import gettext as _
from flask_login import current_user

from ...extensions import db
from ...forms.order import OrderForm
from ...forms.payment import PaymentForm
from ...models.enums import FabricSource, OrderPriority, OrderStatus
from ...models.reference_image import ReferenceImage
from ...models.service import Service
from ...repositories import customer_repo, order_repo
from ...services import order_service, payment_service
from ...services.order_service import OrderError
from ...utils.security import admin_required
from . import bp


def _priced_services() -> list[Service]:
    return (
        Service.query.filter(
            Service.is_active.is_(True), Service.default_stitching_price.isnot(None)
        )
        .order_by(Service.category, Service.sort_order)
        .all()
    )


@bp.get("/orders")
@admin_required
def order_list():
    status = request.args.get("status", "").upper() or None
    term = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    pagination = order_repo.search(status, term, page=page)
    counts = order_repo.counts_by_status()
    return render_template(
        "admin/orders/list.html",
        pagination=pagination,
        orders=pagination.items,
        counts=counts,
        status=status,
        term=term,
        payment_service=payment_service,
    )


@bp.route("/orders/new", methods=["GET", "POST"])
@admin_required
def order_new():
    customer_id = request.args.get("customer_id", type=int)

    if not customer_id:
        term = request.args.get("q", "").strip()
        matches = customer_repo.search(term).items if term else []
        return render_template("admin/orders/pick_customer.html", term=term, matches=matches)

    customer = customer_repo.get_or_404(customer_id)
    services = _priced_services()
    choices = [
        (str(s.id), f"{s.name_en} — ₹{s.default_stitching_price:.2f}") for s in services
    ]

    form = OrderForm()
    for item_form in form.items:
        item_form.service_id.choices = choices

    if request.method == "POST" and not services:
        flash(_("No services have a price set yet — add one under Services first."), "error")
    elif form.validate_on_submit():
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
                    "stitching_price": item_form.stitching_price.data,
                    "material_price": item_form.material_price.data or 0,
                }
            )
        try:
            order = order_service.create_order(
                customer=customer,
                items=items_data,
                fabric_source=FabricSource(form.fabric_source.data),
                priority=OrderPriority(form.priority.data),
                requested_delivery_date=form.requested_delivery_date.data,
                confirmed_delivery_date=form.confirmed_delivery_date.data,
                notes=form.notes.data,
                actor_id=current_user.id,
            )
        except OrderError as exc:
            flash(str(exc), "error")
        else:
            flash(
                _("Order {number} created.").format(number=order.order_number), "success"
            )
            return redirect(url_for("admin.order_detail", order_id=order.id))

    return render_template(
        "admin/orders/form.html", form=form, customer=customer, services=services
    )


@bp.get("/orders/<int:order_id>")
@admin_required
def order_detail(order_id: int):
    order = order_repo.get_or_404(order_id)
    paid = payment_service.paid_for_order(order.id)
    pending = payment_service.pending_for_order(order.id)
    balance = payment_service.balance_for_order(order)
    return render_template(
        "admin/orders/detail.html",
        order=order,
        paid=paid,
        pending=pending,
        balance=balance,
        payment_form=PaymentForm(),
    )


@bp.get("/orders/<int:order_id>/receipt")
@admin_required
def order_receipt(order_id: int):
    order = order_repo.get_or_404(order_id)
    paid = payment_service.paid_for_order(order.id)
    balance = payment_service.balance_for_order(order)
    return render_template("receipts/order_receipt.html", order=order, paid=paid, balance=balance)


@bp.post("/orders/<int:order_id>/status")
@admin_required
def order_status(order_id: int):
    order = order_repo.get_or_404(order_id)
    new_status = request.form.get("status", "")
    if new_status not in OrderStatus.__members__:
        flash(_("Unknown status."), "error")
    else:
        order_service.update_status(order, OrderStatus[new_status], actor_id=current_user.id)
        flash(_("Status updated."), "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))


@bp.post("/orders/<int:order_id>/details")
@admin_required
def order_update_details(order_id: int):
    order = order_repo.get_or_404(order_id)
    priority_raw = request.form.get("priority")
    date_raw = request.form.get("confirmed_delivery_date", "")
    notes = request.form.get("notes", "")

    confirmed_date = None
    if date_raw:
        from datetime import date

        try:
            confirmed_date = date.fromisoformat(date_raw)
        except ValueError:
            confirmed_date = None

    order_service.update_details(
        order,
        priority=OrderPriority(priority_raw) if priority_raw in OrderPriority.__members__ else None,
        confirmed_delivery_date=confirmed_date,
        notes=notes,
        actor_id=current_user.id,
    )
    flash(_("Order details updated."), "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))


@bp.get("/orders/<int:order_id>/images/<int:image_id>")
@admin_required
def order_image(order_id: int, image_id: int):
    image = db.session.get(ReferenceImage, image_id)
    if image is None or image.order_id != order_id:
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_DIR"], image.storage_path)
