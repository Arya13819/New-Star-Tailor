"""Admin payments (Phase 8)."""
from __future__ import annotations

from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user

from ...extensions import db
from ...forms.payment import PaymentForm
from ...models.enums import PaymentMethod, PaymentStatus
from ...models.payment import Payment
from ...repositories import order_repo
from ...services import payment_service
from ...services.payment_service import PaymentError
from ...utils.money import money_sum
from ...utils.security import admin_required
from . import bp


@bp.post("/orders/<int:order_id>/payments")
@admin_required
def payment_record(order_id: int):
    order = order_repo.get_or_404(order_id)
    form = PaymentForm()
    if form.validate_on_submit():
        try:
            payment_service.record_payment(
                order=order,
                amount=form.amount.data,
                method=PaymentMethod(form.method.data),
                transaction_reference=form.transaction_reference.data,
                note=form.note.data,
                actor_id=current_user.id,
            )
        except PaymentError as exc:
            flash(str(exc), "error")
        else:
            flash(_("Payment recorded."), "success")
    else:
        for errs in form.errors.values():
            for err in errs:
                flash(err, "error")
    return redirect(url_for("admin.order_detail", order_id=order.id))


@bp.post("/payments/<int:payment_id>/verify")
@admin_required
def payment_verify(payment_id: int):
    payment = db.session.get(Payment, payment_id)
    if payment is None:
        abort(404)
    payment_service.verify_payment(payment, actor_id=current_user.id)
    flash(_("Payment verified."), "success")
    return redirect(request.referrer or url_for("admin.order_detail", order_id=payment.order_id))


@bp.get("/payments/<int:payment_id>/receipt")
@admin_required
def payment_receipt(payment_id: int):
    payment = db.session.get(Payment, payment_id)
    if payment is None:
        abort(404)
    total_paid = payment_service.paid_for_order(payment.order_id)
    balance = payment_service.balance_for_order(payment.order)
    return render_template(
        "receipts/payment_receipt.html", payment=payment, total_paid=total_paid, balance=balance
    )


@bp.get("/payments")
@admin_required
def payment_list():
    status = request.args.get("status", "").upper() or None
    query = Payment.query
    if status and status in PaymentStatus.__members__:
        query = query.filter(Payment.status == PaymentStatus[status])
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=30, error_out=False
    )

    verified_total = money_sum(
        a for (a,) in db.session.query(Payment.amount)
        .filter(Payment.status == PaymentStatus.VERIFIED)
        .all()
    )
    pending_total = money_sum(
        a for (a,) in db.session.query(Payment.amount)
        .filter(Payment.status == PaymentStatus.PENDING)
        .all()
    )

    return render_template(
        "admin/payments/list.html",
        pagination=pagination,
        payments=pagination.items,
        status=status,
        verified_total=verified_total,
        pending_total=pending_total,
    )
