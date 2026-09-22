"""Quick public enquiries (master prompt §14 Option A)."""
from __future__ import annotations

from ..config import Config
from ..extensions import db
from ..models.base import utcnow
from ..models.customer import Customer
from ..models.enquiry import Enquiry
from ..models.enums import EnquiryStatus
from ..models.order import Order
from ..utils.security import normalise_mobile
from . import customer_service, notification_service


def create_enquiry(*, name: str, mobile: str, address: str | None, message: str | None) -> Enquiry:
    enquiry = Enquiry(
        name=name.strip(),
        mobile=normalise_mobile(mobile),
        address=(address or "").strip() or None,
        message=(message or "").strip() or None,
    )
    db.session.add(enquiry)
    db.session.flush()

    # Alert the shop's own WhatsApp number — otherwise a new enquiry sits
    # silent until someone happens to check /admin/enquiries.
    notification_service.queue_notification(
        type_="NEW_ENQUIRY",
        to_address=Config.SHOP_PHONE,
        body=notification_service.new_enquiry_alert_message(enquiry),
    )
    db.session.commit()
    return enquiry


def set_status(enquiry: Enquiry, status: EnquiryStatus) -> Enquiry:
    if status == EnquiryStatus.CONVERTED:
        # Only ever set by convert_to_customer/mark_converted, once a real
        # order exists — never a manual, order-less status choice.
        return enquiry
    enquiry.status = status
    db.session.commit()
    return enquiry


def start_conversion(enquiry: Enquiry, *, actor_id: int | None) -> Customer:
    """Create a fresh Customer profile from the enquiry's details so staff
    can jump straight into the normal new-order flow after a confirming
    call. A new profile (not a lookup) matches how a walk-in intake works,
    and mobile numbers are deliberately not unique across customers."""
    return customer_service.create_customer(
        name=enquiry.name,
        mobile=enquiry.mobile,
        address=enquiry.address,
        notes=None,
        actor_id=actor_id,
    )


def mark_converted(enquiry: Enquiry, order: Order) -> Enquiry:
    enquiry.status = EnquiryStatus.CONVERTED
    enquiry.converted_order_id = order.id
    enquiry.converted_at = utcnow()
    db.session.commit()
    return enquiry
