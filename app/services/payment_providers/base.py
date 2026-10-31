"""Payment provider abstraction (master prompt §26).

A concrete provider is dropped in later by setting ``PAYMENT_PROVIDER`` (and
its credentials) in the environment — nothing here invents credentials or
fakes a successful payment. Until a real provider is configured, ``manual``
(see manual.py) is used: it never calls out to anything, and every online
payment sits PENDING until a human verifies it.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PaymentProvider(ABC):
    """Interface every real payment gateway integration must implement."""

    name: str = "base"

    @abstractmethod
    def create_payment(self, *, order, amount, **kwargs) -> dict[str, Any]:
        """Start a payment with the provider. Returns provider-specific data
        the frontend needs (e.g. a checkout URL or order token)."""

    @abstractmethod
    def verify_payment(self, *, provider_reference: str) -> bool:
        """Ask the provider directly whether a payment succeeded."""

    @abstractmethod
    def handle_webhook(self, *, headers: dict, body: bytes) -> dict[str, Any]:
        """Validate and parse an incoming webhook. Returns a normalised event:
        {"event_id": str, "status": "paid"|"failed", "amount": Decimal, ...}.
        Must raise on an invalid signature — never trust an unverified payload.
        """

    @abstractmethod
    def refund_payment(self, *, provider_reference: str, amount) -> dict[str, Any]:
        """Issue a refund. Not exposed anywhere yet (no UI calls this)."""
