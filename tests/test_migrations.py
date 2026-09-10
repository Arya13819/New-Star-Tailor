"""The Alembic migration applies and reverses cleanly on a fresh database."""
from __future__ import annotations

from flask_migrate import downgrade, upgrade
from sqlalchemy import inspect

from app import create_app
from app.extensions import db


def test_migration_upgrade_then_downgrade(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'm.sqlite'}")
    app = create_app("testing")

    with app.app_context():
        upgrade()
        tables = set(inspect(db.engine).get_table_names())
        assert {
            "users",
            "customers",
            "measurements",
            "measurement_versions",
            "services",
            "orders",
            "order_items",
            "order_sequences",
            "payments",
            "payment_events",
            "reference_images",
            "notifications",
            "settings",
            "audit_logs",
        }.issubset(tables)
        assert "alembic_version" in tables

        downgrade(revision="base")
        remaining = set(inspect(db.engine).get_table_names())
        remaining.discard("alembic_version")
        assert remaining == set()
