"""Customer notifications (master prompt §30-32) — SMS-ready architecture.

Plain SMS only — never WhatsApp (WhatsApp Business API needs Meta business
verification the shop isn't pursuing; SMS needs a DLT-registered sender ID
instead, which is simpler for a single small shop).

Queuing a notification only ever writes a row. Nothing here ever claims a
message was sent unless a real provider confirmed it — until one is
configured (``Config.messaging_configured()``), rows simply stay SCHEDULED
and ``dispatch_pending`` says so honestly.
"""
from __future__ import annotations

from ..config import Config
from ..extensions import db
from ..models.base import utcnow
from ..models.enums import NotificationChannel, NotificationStatus, NotificationType, UserRole
from ..models.notification import Notification


def _customer_wants_hindi(customer) -> bool:
    """A customer's SMS language is their own persisted preference (set via
    the language switcher while logged into the portal), never the admin's
    UI language at the moment a notification happens to be queued — an
    admin marking an order READY, or the reminders cron, has no "current
    language" of the customer's to go by. No recorded preference (walk-in
    customers with no portal login, or an explicit English choice) means
    Hinglish, not English — an SMS in plain English reads as oddly formal
    for this audience."""
    user = customer.user if customer else None
    return bool(user and user.role == UserRole.CUSTOMER and user.preferred_locale == "hi")


def order_confirmation_message(customer, order, grand_total) -> str:
    if _customer_wants_hindi(customer):
        return (
            f"नमस्ते {customer.name}, आपका ऑर्डर {order.order_number} न्यू स्टार टेलर "
            f"में प्राप्त हो गया है। कुल राशि: ₹{grand_total}।"
        )
    return (
        f"Namaste {customer.name}, aapka order {order.order_number} New Star "
        f"Tailor mein mil gaya hai. Total: Rs. {grand_total}."
    )


def order_ready_message(customer, order) -> str:
    if _customer_wants_hindi(customer):
        return (
            f"नमस्ते {customer.name}, आपका ऑर्डर {order.order_number} तैयार है — "
            f"कृपया न्यू स्टार टेलर से ले जाएं।"
        )
    return (
        f"Namaste {customer.name}, aapka order {order.order_number} taiyaar "
        f"hai — New Star Tailor se collect kar lijiye."
    )


def new_enquiry_alert_message(enquiry) -> str:
    """Shop-facing (not customer-facing) — always Hinglish, since this reaches
    the shop's own phone regardless of any customer's language choice."""
    text = f"Nayi enquiry aayi hai: {enquiry.name} ({enquiry.mobile})."
    if enquiry.message:
        text += f" Message: {enquiry.message}"
    return text


def payment_reminder_message(customer, order, balance) -> str:
    if _customer_wants_hindi(customer):
        return (
            f"नमस्ते {customer.name}, आपके ऑर्डर {order.order_number} पर ₹{balance} "
            f"बकाया है। कृपया न्यू स्टार टेलर आकर भुगतान करें।"
        )
    return (
        f"Namaste {customer.name}, aapke order {order.order_number} par Rs. "
        f"{balance} baaki hai. Kripya New Star Tailor aakar payment kar dein."
    )


def queue_notification(
    *,
    customer=None,
    order=None,
    type_: str,
    body: str,
    channel: NotificationChannel = NotificationChannel.SMS,
    scheduled_at=None,
    dedupe_key: str | None = None,
    to_address: str | None = None,
) -> Notification | None:
    """Write a SCHEDULED notification row. Returns None (no-op) if
    ``dedupe_key`` already exists — never queue the same reminder twice.

    ``to_address`` overrides the customer's mobile — used for shop-facing
    alerts (e.g. a new enquiry) that have no Customer record at all yet."""
    if dedupe_key and Notification.query.filter_by(dedupe_key=dedupe_key).first():
        return None

    notification = Notification(
        customer_id=customer.id if customer else None,
        order_id=order.id if order else None,
        channel=channel,
        type=NotificationType(type_),
        status=NotificationStatus.SCHEDULED,
        to_address=to_address or (customer.mobile if customer else None),
        body=body,
        scheduled_at=scheduled_at,
        dedupe_key=dedupe_key,
    )
    db.session.add(notification)
    db.session.flush()
    return notification


def dispatch_pending() -> dict:
    """Attempt to send every SCHEDULED notification.

    With no messaging provider configured (the only state possible today),
    this touches nothing and reports exactly that — it never marks a row
    SENT or FAILED for a message that was simply never attempted.
    """
    pending = Notification.query.filter_by(status=NotificationStatus.SCHEDULED).all()
    if not Config.messaging_configured():
        return {"configured": False, "pending": len(pending), "sent": 0, "failed": 0}

    sent = 0
    failed = 0
    for note in pending:
        try:
            _send_via_provider(note)
            note.status = NotificationStatus.SENT
            note.sent_at = utcnow()
            sent += 1
        except Exception as exc:  # noqa: BLE001
            note.status = NotificationStatus.FAILED
            note.error_message = str(exc)[:500]
            failed += 1
    db.session.commit()
    return {"configured": True, "pending": len(pending), "sent": sent, "failed": failed}


def _send_via_provider(notification: Notification) -> None:
    """Placeholder for the real SMS gateway call once SMS_API_KEY /
    SMS_SENDER_ID are configured. Deliberately unused while
    messaging_configured() is False."""
    raise NotImplementedError(
        "SMS sending is not implemented yet — only the queueing "
        "architecture exists."
    )


def notifications_query(status: str | None = None):
    query = Notification.query
    if status and status in NotificationStatus.__members__:
        query = query.filter(Notification.status == NotificationStatus[status])
    return query.order_by(Notification.created_at.desc())


def queue_payment_reminders(*, days_after_delivery: int = 7) -> int:
    """Queue a PAYMENT_REMINDER for every DELIVERED order with a balance
    still outstanding, at least ``days_after_delivery`` days after delivery.

    Meant to run once a day (``flask nst reminders run``, via cron). The
    dedupe key includes today's date, so re-running the same day is a no-op
    and running it daily naturally gives one reminder per day until the
    balance reaches zero — a simple, honest stand-in for a fuller
    configurable policy later.
    """
    from datetime import date, timedelta

    from ..models.enums import OrderStatus
    from ..models.order import Order
    from . import payment_service

    cutoff = utcnow() - timedelta(days=days_after_delivery)
    candidates = (
        Order.query.filter(
            Order.status == OrderStatus.DELIVERED,
            Order.delivered_at.isnot(None),
            Order.delivered_at <= cutoff,
        )
        .all()
    )

    today_key = date.today().isoformat()
    queued = 0
    for order in candidates:
        balance = payment_service.balance_for_order(order)
        if balance <= 0:
            continue
        result = queue_notification(
            customer=order.customer,
            order=order,
            type_="PAYMENT_REMINDER",
            body=payment_reminder_message(order.customer, order, balance),
            dedupe_key=f"payment_reminder:{order.id}:{today_key}",
        )
        if result is not None:
            queued += 1
    db.session.commit()
    return queued
