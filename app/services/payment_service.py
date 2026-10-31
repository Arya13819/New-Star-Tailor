"""Payment aggregation (read side) + recording (Phase 8 adds mutations below).

Balance is always computed server-side from *verified* payments only — the
frontend's numbers are never trusted (master prompt §23).
"""
from __future__ import annotations

from decimal import Decimal

from flask_babel import gettext as _

from ..extensions import db
from ..models.audit_log import AuditLog
from ..models.enums import PaymentMethod, PaymentStatus
from ..models.order import Order
from ..models.payment import Payment
from ..utils.money import money_sum, to_money


class PaymentError(ValueError):
    """Raised for a business-rule violation the UI should show as a message."""


def paid_for_order(order_id: int) -> Decimal:
    amounts = (
        db.session.query(Payment.amount)
        .filter(Payment.order_id == order_id, Payment.status == PaymentStatus.VERIFIED)
        .all()
    )
    return money_sum(a for (a,) in amounts)


def pending_for_order(order_id: int) -> Decimal:
    amounts = (
        db.session.query(Payment.amount)
        .filter(Payment.order_id == order_id, Payment.status == PaymentStatus.PENDING)
        .all()
    )
    return money_sum(a for (a,) in amounts)


def balance_for_order(order: Order) -> Decimal:
    return to_money(to_money(order.grand_total) - paid_for_order(order.id))


def _sync_advance_flag(order: Order) -> None:
    order.advance_satisfied = paid_for_order(order.id) + Decimal("0.000001") >= to_money(
        order.required_advance
    )


def record_payment(
    *,
    order: Order,
    amount,
    method: PaymentMethod,
    transaction_reference: str | None,
    note: str | None,
    actor_id: int | None,
) -> Payment:
    amount = to_money(amount)
    if amount <= 0:
        raise PaymentError(_("Enter an amount greater than zero."))

    balance = balance_for_order(order)
    if amount - balance > Decimal("0.50"):
        raise PaymentError(
            _("That is more than the outstanding balance (₹%(balance)s).", balance=balance)
        )

    # Cash/UPI is collected and confirmed in person; online awaits verification
    # (by a future provider webhook, or a manual check) — never fabricated.
    verified = method in (PaymentMethod.CASH, PaymentMethod.UPI)

    payment = Payment(
        order_id=order.id,
        customer_id=order.customer_id,
        amount=amount,
        method=method,
        status=PaymentStatus.VERIFIED if verified else PaymentStatus.PENDING,
        transaction_reference=(transaction_reference or "").strip() or None,
        note=(note or "").strip() or None,
        recorded_by_id=actor_id,
        verified_by_id=actor_id if verified else None,
    )
    if verified:
        from ..models.base import utcnow

        payment.verified_at = utcnow()

    db.session.add(payment)
    db.session.flush()
    _sync_advance_flag(order)

    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="payment",
            entity_id=payment.id,
            action="record",
            to_value=f"order={order.id} amount={amount} method={method.value} status={payment.status.value}",
        )
    )
    db.session.commit()
    return payment


def verify_payment(payment: Payment, *, actor_id: int | None) -> Payment:
    from ..models.base import utcnow

    if payment.status == PaymentStatus.VERIFIED:
        return payment
    payment.status = PaymentStatus.VERIFIED
    payment.verified_by_id = actor_id
    payment.verified_at = utcnow()
    db.session.flush()
    _sync_advance_flag(payment.order)
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="payment",
            entity_id=payment.id,
            action="verify",
        )
    )
    db.session.commit()
    return payment
