"""Admin view of public enquiries (Phase 11)."""
from __future__ import annotations

from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _

from ...extensions import db
from ...models.enquiry import Enquiry
from ...models.enums import EnquiryStatus
from ...services import enquiry_service
from ...utils.security import admin_required
from . import bp


@bp.get("/enquiries")
@admin_required
def enquiry_list():
    status = request.args.get("status", "").upper() or None
    query = Enquiry.query
    if status and status in EnquiryStatus.__members__:
        query = query.filter(Enquiry.status == EnquiryStatus[status])
    rows = query.order_by(Enquiry.created_at.desc()).all()
    return render_template("admin/enquiries/list.html", enquiries=rows, status=status)


@bp.post("/enquiries/<int:enquiry_id>/status")
@admin_required
def enquiry_status(enquiry_id: int):
    enq = db.session.get(Enquiry, enquiry_id)
    if enq is None:
        abort(404)
    new_status = request.form.get("status", "")
    if new_status in EnquiryStatus.__members__:
        enquiry_service.set_status(enq, EnquiryStatus[new_status])
        flash(_("Enquiry updated."), "success")
    return redirect(url_for("admin.enquiry_list"))
