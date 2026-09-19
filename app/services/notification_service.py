"""Customer notifications (master prompt §30-32) — WhatsApp-ready architecture.

Queuing a notification only ever writes a row. Nothing here ever claims a
message was sent unless a real provider confirmed it — until one is
configured (``Config.messaging_configured()``), rows simply stay SCHEDULED
and ``dispatch_pending`` says so honestly.
"""
from __future__ import annotations

from ..config import Config
from ..extensions import db
from ..models.base import utcnow
from ..models.enums import NotificationChannel, NotificationStatus, NotificationType
from ..models.notification import Notification


def queue_notification(
    *,
    customer,
    order=None,
    type_: str,
    body: str,
    channel: NotificationChannel = NotificationChannel.WHATSAPP,
    scheduled_at=None,
    dedupe_key: str | None = None,
) -> Notification | None:
    """Write a SCHEDULED notification row. Returns None (no-op) if
    ``dedupe_key`` already exists — never queue the same reminder twice."""
    if dedupe_key and Notification.query.filter_by(dedupe_key=dedupe_key).first():
        return None

    notification = Notification(
        customer_id=customer.id if customer else None,
        order_id=order.id if order else None,
        channel=channel,
        type=NotificationType(type_),
        status=NotificationStatus.SCHEDULED,
        to_address=customer.mobile if customer else None,
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
    """Placeholder for the real WhatsApp Business API call once
    WHATSAPP_API_KEY / WHATSAPP_PHONE_ID are configured. Deliberately unused
    while messaging_configured() is False."""
    raise NotImplementedError(
        "WhatsApp sending is not implemented yet — only the queueing "
        "architecture exists."
    )


def notifications_query(status: str | None = None):
    query = Notification.query
    if status and status in NotificationStatus.__members__:
        query = query.filter(Notification.status == NotificationStatus[status])
    return query.order_by(Notification.created_at.desc())
