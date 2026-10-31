"""Admin customer management (Phase 4)."""
from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user

from ...forms.customer import CustomerForm
from ...repositories import customer_repo
from ...services import customer_service
from ...utils.measurement_fields import PANT_FIELDS, SHIRT_FIELDS
from ...utils.security import admin_required, normalise_mobile
from . import bp


@bp.get("/customers")
@admin_required
def customer_list():
    term = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    pagination = customer_repo.search(term, page=page)
    return render_template(
        "admin/customers/list.html", pagination=pagination, customers=pagination.items, term=term
    )


@bp.route("/customers/new", methods=["GET", "POST"])
@admin_required
def customer_new():
    form = CustomerForm()
    prefill_mobile = request.args.get("mobile", "")
    if request.method == "GET" and prefill_mobile:
        form.mobile.data = prefill_mobile

    existing_matches = []
    mobile_to_check = form.mobile.data or prefill_mobile
    if mobile_to_check and len(normalise_mobile(mobile_to_check)) == 10:
        existing_matches = customer_repo.find_by_mobile(normalise_mobile(mobile_to_check))

    if form.validate_on_submit():
        customer = customer_service.create_customer(
            name=form.name.data,
            mobile=form.mobile.data,
            address=form.address.data,
            notes=form.notes.data,
            actor_id=current_user.id,
        )
        flash(_("Customer added."), "success")
        return redirect(url_for("admin.customer_detail", customer_id=customer.id))

    return render_template(
        "admin/customers/form.html",
        form=form,
        mode="new",
        existing_matches=existing_matches,
    )


@bp.get("/customers/<int:customer_id>")
@admin_required
def customer_detail(customer_id: int):
    customer = customer_repo.get_or_404(customer_id)
    return render_template(
        "admin/customers/detail.html",
        customer=customer,
        shirt_fields=SHIRT_FIELDS,
        pant_fields=PANT_FIELDS,
    )


@bp.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@admin_required
def customer_edit(customer_id: int):
    customer = customer_repo.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer_service.update_customer(
            customer,
            name=form.name.data,
            mobile=form.mobile.data,
            address=form.address.data,
            notes=form.notes.data,
            actor_id=current_user.id,
        )
        flash(_("Customer updated."), "success")
        return redirect(url_for("admin.customer_detail", customer_id=customer.id))

    return render_template(
        "admin/customers/form.html", form=form, mode="edit", customer=customer, existing_matches=[]
    )
