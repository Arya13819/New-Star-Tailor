"""Custom Flask CLI commands.

Phase 1 provides only ``flask nst check``. Later phases add ``nst seed``,
``nst notifications process`` and ``nst reminders run``.
"""
from __future__ import annotations

import click
import sqlalchemy as sa
from flask import Flask, current_app
from sqlalchemy import text

from .extensions import db


def register_cli(app: Flask) -> None:
    @app.cli.group("nst")
    def nst():
        """New Star Tailor management commands."""

    @nst.command("check")
    def check():
        """Print a short configuration and connectivity summary."""
        cfg = current_app.config
        uri = cfg.get("SQLALCHEMY_DATABASE_URI", "")
        safe_uri = uri.split("@")[-1] if "@" in uri else uri
        click.echo(f"Environment      : {cfg.get('ENV')}")
        click.echo(f"Database target  : {safe_uri or '(not configured)'}")

        try:
            db.session.execute(text("SELECT 1"))
            insp = sa.inspect(db.engine)
            tables = [t for t in insp.get_table_names() if t != "alembic_version"]
            rev = None
            if "alembic_version" in insp.get_table_names():
                row = db.session.execute(
                    text("SELECT version_num FROM alembic_version")
                ).first()
                rev = row[0] if row else None
            click.secho(f"Database         : reachable ({len(tables)} tables)", fg="green")
            click.echo(f"Schema revision  : {rev or 'not migrated — run: flask db upgrade'}")
        except Exception as exc:  # noqa: BLE001
            click.secho(f"Database         : NOT reachable ({type(exc).__name__})", fg="yellow")
            click.echo("  -> see docs/DATABASE_SETUP.md")

        click.echo(f"Payments wired   : {cfg['PAYMENT_PROVIDER'] != 'manual' and bool(cfg['PAYMENT_PROVIDER_KEY'])}")
        click.echo(f"Messaging wired  : {bool(cfg['WHATSAPP_API_KEY'] and cfg['WHATSAPP_PHONE_ID'])}")
