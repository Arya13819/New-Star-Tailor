"""Admin service catalogue (Phase 6)."""
from __future__ import annotations

from flask import abort, flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user

from ...extensions import db
from ...forms.service import ServiceForm
from ...models.enums import ServiceCategory
from ...models.service import Service
from ...services import catalog_service
from ...utils.security import admin_required
from . import bp


@bp.get("/services")
@admin_required
def service_list():
    services = Service.query.order_by(Service.category, Service.sort_order).all()
    return render_template("admin/services/list.html", services=services)


@bp.post("/services/seed-defaults")
@admin_required
def service_seed_defaults():
    created = catalog_service.seed_defaults(actor_id=current_user.id)
    if created:
        flash(_("Added {count} default service(s).").format(count=created), "success")
    else:
        flash(_("Default services are already in the catalogue."), "message")
    return redirect(url_for("admin.service_list"))


@bp.route("/services/new", methods=["GET", "POST"])
@admin_required
def service_new():
    form = ServiceForm()
    if form.validate_on_submit():
        if Service.query.filter_by(code=form.code.data.strip().upper()).first():
            flash(_("A service with this code already exists."), "error")
        else:
            catalog_service.create_service(
                actor_id=current_user.id,
                code=form.code.data.strip().upper(),
                name_en=form.name_en.data.strip(),
                name_hi=(form.name_hi.data or "").strip() or None,
                category=ServiceCategory(form.category.data),
                default_stitching_price=form.default_stitching_price.data,
                description=(form.description.data or "").strip() or None,
                sort_order=form.sort_order.data or 100,
                is_active=form.is_active.data,
            )
            flash(_("Service added."), "success")
            return redirect(url_for("admin.service_list"))

    return render_template("admin/services/form.html", form=form, mode="new")


@bp.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
@admin_required
def service_edit(service_id: int):
    service = db.session.get(Service, service_id)
    if service is None:
        abort(404)

    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        catalog_service.update_service(
            service,
            actor_id=current_user.id,
            name_en=form.name_en.data.strip(),
            name_hi=(form.name_hi.data or "").strip() or None,
            category=ServiceCategory(form.category.data),
            default_stitching_price=form.default_stitching_price.data,
            description=(form.description.data or "").strip() or None,
            sort_order=form.sort_order.data or 100,
            is_active=form.is_active.data,
        )
        flash(_("Service updated. Existing orders keep their original price."), "success")
        return redirect(url_for("admin.service_list"))

    return render_template(
        "admin/services/form.html", form=form, mode="edit", service=service
    )


@bp.post("/services/<int:service_id>/toggle")
@admin_required
def service_toggle(service_id: int):
    service = db.session.get(Service, service_id)
    if service is None:
        abort(404)
    catalog_service.toggle_active(service, actor_id=current_user.id)
    flash(
        _("{name} is now {state}.").format(
            name=service.name_en, state=_("active") if service.is_active else _("hidden")
        ),
        "success",
    )
    return redirect(url_for("admin.service_list"))
