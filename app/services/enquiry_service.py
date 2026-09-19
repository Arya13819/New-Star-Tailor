"""Quick public enquiries (master prompt §14 Option A)."""
from __future__ import annotations

from ..extensions import db
from ..models.enquiry import Enquiry
from ..models.enums import EnquiryStatus
from ..utils.security import normalise_mobile


def create_enquiry(*, name: str, mobile: str, address: str | None, message: str | None) -> Enquiry:
    enquiry = Enquiry(
        name=name.strip(),
        mobile=normalise_mobile(mobile),
        address=(address or "").strip() or None,
        message=(message or "").strip() or None,
    )
    db.session.add(enquiry)
    db.session.commit()
    return enquiry


def set_status(enquiry: Enquiry, status: EnquiryStatus) -> Enquiry:
    enquiry.status = status
    db.session.commit()
    return enquiry
