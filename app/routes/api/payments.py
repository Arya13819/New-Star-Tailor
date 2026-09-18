"""Online payment webhook (master prompt §25-26).

Inert until a real ``PAYMENT_PROVIDER`` is configured — always says so
plainly rather than pretending to process anything. When a provider is
connected, duplicate webhook deliveries can never double-credit an order:
every event is recorded in ``payment_events`` under a UNIQUE(provider,
event_id) constraint before any payment is touched.
"""
from __future__ import annotations

from flask import current_app, jsonify, request

from ...extensions import db
from ...models.enums import PaymentStatus
from ...models.payment import Payment, PaymentEvent
from ...services.payment_providers.manual import NotConfiguredError, get_provider
from . import bp


@bp.post("/payments/webhook")
def payments_webhook():
    provider_name = current_app.config.get("PAYMENT_PROVIDER", "manual")
    if provider_name == "manual":
        return jsonify(
            error="No online payment provider is configured. "
            "Payments are recorded manually from the order page."
        ), 501

    provider = get_provider()
    try:
        event = provider.handle_webhook(
            headers=dict(request.headers), body=request.get_data()
        )
    except NotConfiguredError as exc:
        return jsonify(error=str(exc)), 501
    except Exception as exc:  # noqa: BLE001 - never trust an unverified payload
        current_app.logger.warning("Rejected payment webhook: %s", exc)
        return jsonify(error="Invalid webhook payload"), 400

    event_id = event.get("event_id")
    if not event_id:
        return jsonify(error="Webhook missing an event id"), 400

    if PaymentEvent.query.filter_by(provider=provider_name, event_id=event_id).first():
        return jsonify(status="already processed"), 200

    payment = None
    payment_id = event.get("payment_id")
    if payment_id:
        payment = db.session.get(Payment, payment_id)

    if payment and event.get("status") == "paid":
        payment.status = PaymentStatus.VERIFIED
        from ...models.base import utcnow

        payment.verified_at = utcnow()
    elif payment and event.get("status") == "failed":
        payment.status = PaymentStatus.FAILED

    db.session.add(
        PaymentEvent(
            provider=provider_name,
            event_id=event_id,
            event_type=event.get("type"),
            payment_id=payment.id if payment else None,
            order_id=payment.order_id if payment else None,
        )
    )
    db.session.commit()
    return jsonify(status="processed"), 200
