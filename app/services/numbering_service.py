"""Server-side, atomic order numbering (master prompt §17).

Order numbers are never generated on the frontend. A single-row counter is
locked (`SELECT ... FOR UPDATE`) inside the same transaction as the order
insert, so two simultaneous walk-in orders can never collide.
"""
from __future__ import annotations

from flask import current_app

from ..extensions import db
from ..models.order import OrderSequence


def next_order_number() -> tuple[str, int]:
    """Return (order_number, seq). Must be called inside a transaction that
    will be committed together with the order it numbers."""
    row = db.session.query(OrderSequence).with_for_update().first()
    if row is None:
        row = OrderSequence(id=1, last_seq=0)
        db.session.add(row)
        db.session.flush()

    row.last_seq += 1
    cfg = current_app.config
    number = f"{cfg['ORDER_NUMBER_PREFIX']}{row.last_seq:0{cfg['ORDER_NUMBER_PAD']}d}"
    return number, row.last_seq
