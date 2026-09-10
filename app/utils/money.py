"""Decimal-safe money helpers.

Every monetary value in this application is a ``decimal.Decimal`` quantised to
paise (2 places). Floating point is never used for money.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

TWO_PLACES = Decimal("0.01")
ZERO = Decimal("0.00")


def to_money(value: object) -> Decimal:
    """Coerce *value* to a 2-dp Decimal. Raises ValueError on junk."""
    if isinstance(value, Decimal):
        dec = value
    elif isinstance(value, (int,)):
        dec = Decimal(value)
    elif isinstance(value, str):
        try:
            dec = Decimal(value.strip() or "0")
        except InvalidOperation as exc:
            raise ValueError(f"Not a valid amount: {value!r}") from exc
    elif isinstance(value, float):
        # Only reachable from external/legacy data — convert via str to avoid
        # binary-float artefacts, then treat as suspect.
        dec = Decimal(str(value))
    elif value is None:
        dec = ZERO
    else:
        raise ValueError(f"Not a valid amount: {value!r}")
    return dec.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def money_sum(values) -> Decimal:
    total = ZERO
    for v in values:
        total += to_money(v)
    return total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def percent_of(amount: object, percent: object) -> Decimal:
    """``percent`` as a whole number, e.g. percent_of(700, 50) -> Decimal('350.00')."""
    return (to_money(amount) * Decimal(str(percent)) / Decimal(100)).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )


def format_inr(amount: object) -> str:
    """Indian-grouped rupee string, e.g. '₹1,23,456.00' (no paise if whole)."""
    dec = to_money(amount)
    negative = dec < 0
    whole, frac = divmod(abs(int(dec * 100)), 100)
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = head[::-1]
        head = ",".join(head[i : i + 2] for i in range(0, len(head), 2))[::-1]
        s = f"{head},{tail}"
    out = f"₹{s}" if frac == 0 else f"₹{s}.{frac:02d}"
    return f"-{out}" if negative else out
