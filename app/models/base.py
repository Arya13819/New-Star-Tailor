"""Model base helpers and mixins."""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


@event.listens_for(Engine, "connect")
def _enforce_sqlite_foreign_keys(dbapi_connection, connection_record):  # noqa: ANN001
    """Make SQLite enforce foreign keys / ON DELETE, matching MySQL InnoDB.

    No effect on MySQL/MariaDB connections.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Applied to every table so MySQL/MariaDB uses InnoDB + utf8mb4 (Devanagari).
# SQLite ignores these keys.
TABLE_ARGS = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}


def utcnow() -> datetime:
    """Naive UTC timestamp (columns are ``DateTime`` without tz)."""
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class PkMixin:
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)


__all__ = ["db", "sa", "Mapped", "mapped_column", "TimestampMixin", "PkMixin", "TABLE_ARGS", "utcnow"]
