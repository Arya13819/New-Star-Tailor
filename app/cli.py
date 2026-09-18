"""Custom Flask CLI commands.

``nst check`` (Phase 1) and ``nst create-admin`` (Phase 3) so far. Later
phases add ``nst seed``, ``nst notifications process`` and ``nst reminders run``.
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

    @nst.command("create-admin")
    @click.option("--name", prompt=True)
    @click.option("--email", prompt=True)
    @click.option("--mobile", prompt=True, default="", show_default=False)
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    )
    def create_admin(name: str, email: str, mobile: str, password: str):
        """Create (or promote) the shop admin account."""
        from .models.enums import UserRole
        from .models.user import User
        from .utils.security import normalise_mobile

        email = email.strip().lower()
        mobile_clean = normalise_mobile(mobile) if mobile else None
        if mobile_clean and len(mobile_clean) != 10:
            raise click.ClickException("Mobile number must have 10 digits.")
        if len(password) < 8:
            raise click.ClickException("Password must be at least 8 characters.")

        existing = User.query.filter(
            (User.email == email) | (User.mobile == mobile_clean if mobile_clean else False)
        ).first()
        if existing:
            existing.role = UserRole.ADMIN
            existing.name = name
            existing.is_active = True
            existing.set_password(password)
            db.session.commit()
            click.secho(f"Updated existing account -> admin: {email}", fg="green")
            return

        user = User(name=name, email=email, mobile=mobile_clean, role=UserRole.ADMIN)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.secho(f"Admin account created: {email}", fg="green")

    @nst.command("seed-services")
    def seed_services():
        """Load the known default services (idempotent — safe to re-run)."""
        from .services import catalog_service

        created = catalog_service.seed_defaults()
        if created:
            click.secho(f"Added {created} service(s).", fg="green")
        else:
            click.echo("Default services already present — nothing to do.")
