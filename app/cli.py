"""Custom Flask CLI commands: ``nst check``, ``nst create-admin``,
``nst seed-services``, ``nst notifications process``, ``nst reminders run``."""
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

    @nst.group("notifications")
    def notifications():
        """Notification queue management."""

    @notifications.command("process")
    def notifications_process():
        """Attempt to dispatch every SCHEDULED notification.

        With no WhatsApp/SMS provider configured this touches nothing and
        says so plainly — it never marks a message SENT that wasn't.
        """
        from .services import notification_service

        result = notification_service.dispatch_pending()
        if not result["configured"]:
            click.secho(
                f"Messaging is not configured — {result['pending']} notification(s) "
                "remain SCHEDULED. Set WHATSAPP_API_KEY and WHATSAPP_PHONE_ID to send.",
                fg="yellow",
            )
        else:
            click.secho(
                f"Sent {result['sent']}, failed {result['failed']} "
                f"(of {result['pending']} pending).",
                fg="green",
            )

    @nst.group("reminders")
    def reminders():
        """Payment reminder scheduling."""

    @reminders.command("run")
    @click.option("--days-after-delivery", default=7, show_default=True, type=int)
    def reminders_run(days_after_delivery: int):
        """Queue a PAYMENT_REMINDER for every delivered order still owing a
        balance, N days after delivery. Safe to run daily via cron — the
        same order is never queued twice on the same day."""
        from .services import notification_service

        count = notification_service.queue_payment_reminders(
            days_after_delivery=days_after_delivery
        )
        click.secho(f"Queued {count} payment reminder(s).", fg="green")
