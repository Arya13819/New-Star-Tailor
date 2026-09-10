"""Money helpers must be exact — never floating point."""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.utils.money import ZERO, format_inr, money_sum, percent_of, to_money


def test_to_money_quantises_to_paise():
    assert to_money("700") == Decimal("700.00")
    assert to_money(550) == Decimal("550.00")
    assert to_money("1234.5") == Decimal("1234.50")
    assert to_money(None) == ZERO


def test_to_money_rejects_junk():
    with pytest.raises(ValueError):
        to_money("abc")


def test_percent_of_matches_business_examples():
    # Customer brings cloth -> 50% of stitching.
    assert percent_of(700, 50) == Decimal("350.00")
    assert percent_of(550, 50) == Decimal("275.00")
    # Odd rupee split rounds half up.
    assert percent_of(775, 50) == Decimal("387.50")


def test_money_sum_is_exact():
    # The classic float trap: 0.1 + 0.2. Decimal handles it.
    assert money_sum(["0.10", "0.20"]) == Decimal("0.30")
    assert money_sum([700, 1200]) == Decimal("1900.00")


def test_format_inr_grouping():
    assert format_inr(700) == "₹700"
    assert format_inr("1900.00") == "₹1,900"
    assert format_inr(123456) == "₹1,23,456"
    assert format_inr("1234.50") == "₹1,234.50"
