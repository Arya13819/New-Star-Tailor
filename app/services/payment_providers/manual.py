"""Default provider: no external gateway connected.

Every method here is honest about doing nothing — no fake "success", no
invented reference numbers. Online payments simply stay PENDING until an
admin manually verifies them (or a real provider replaces this class).
"""
from __future__ import annotations

from typing import Any

from .base import PaymentProvider


class NotConfiguredError(RuntimeError):
    """Raised when the app tries to talk to a payment gateway that isn't set up."""


class ManualProvider(PaymentProvider):
    name = "manual"

    def create_payment(self, *, order, amount, **kwargs) -> dict[str, Any]:
        raise NotConfiguredError(
            "No online payment provider is configured yet. Record cash/UPI "
            "payments directly, or set PAYMENT_PROVIDER + credentials."
        )

    def verify_payment(self, *, provider_reference: str) -> bool:
        raise NotConfiguredError("No online payment provider is configured yet.")

    def handle_webhook(self, *, headers: dict, body: bytes) -> dict[str, Any]:
        raise NotConfiguredError("No online payment provider is configured yet.")

    def refund_payment(self, *, provider_reference: str, amount) -> dict[str, Any]:
        raise NotConfiguredError("No online payment provider is configured yet.")


def get_provider() -> PaymentProvider:
    """Provider registry. Real providers register themselves here once
    credentials exist — for now everything resolves to ManualProvider."""
    return ManualProvider()
