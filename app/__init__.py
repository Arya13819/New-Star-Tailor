"""Application factory for NEW STAR TAILOR."""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, request, session

from .config import Config, resolve_config
from .extensions import babel, csrf, db, limiter, login_manager, migrate

load_dotenv()

__version__ = "0.1.0"


def _select_locale() -> str:
    languages = list(Config.LANGUAGES.keys())
    # 1. explicit override via ?lang=
    requested = request.args.get("lang")
    if requested in languages:
        session["lang"] = requested
    # 2. remembered choice
    chosen = session.get("lang")
    if chosen in languages:
        return chosen
    # 3. browser preference, else default
    return request.accept_languages.best_match(languages) or Config.BABEL_DEFAULT_LOCALE


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(resolve_config(config_name))

    # Production runs behind Nginx (TLS-terminating reverse proxy — see
    # docs/DEPLOYMENT.md). Without this, request.is_secure is always False
    # and url_for(_external=True) always emits http://, breaking HSTS,
    # secure cookies, and the canonical/Open Graph URLs. Harmless when there
    # is no proxy (dev/tests): X-Forwarded-* headers simply aren't sent.
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    _configure_logging(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context(app)
    _register_security_headers(app)
    _register_cli(app)

    return app


def _configure_logging(app: Flask) -> None:
    level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    app.logger.setLevel(level)


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    # Import models so they register on db.metadata for Flask-Migrate.
    from . import models  # noqa: F401

    # Batch mode lets Alembic emit ALTERs SQLite can run; not needed on MySQL.
    is_sqlite = app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite")
    migrate.init_app(app, db, render_as_batch=is_sqlite)
    csrf.init_app(app)
    limiter.init_app(app)
    babel.init_app(app, locale_selector=_select_locale)

    login_manager.init_app(app)
    login_manager.login_view = "auth.admin_login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def _load_user(user_id: str):
        from .models.user import User

        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None


def _register_blueprints(app: Flask) -> None:
    from .routes.admin import bp as admin_bp
    from .routes.api import bp as api_bp
    from .routes.auth import bp as auth_bp
    from .routes.customer_portal import bp as customer_bp
    from .routes.public import bp as public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # API blueprint is JSON-only; exempt it from form CSRF (it uses other auth).
    csrf.exempt(api_bp)


def _register_error_handlers(app: Flask) -> None:
    from .utils.errors import register_error_handlers

    register_error_handlers(app)


def _register_context(app: Flask) -> None:
    from datetime import date

    from flask_babel import get_locale

    @app.context_processor
    def inject_globals():
        return {
            "APP_VERSION": __version__,
            "now_year": date.today().year,
            "LANGUAGES": app.config["LANGUAGES"],
            "CURRENT_LOCALE": str(get_locale() or app.config["BABEL_DEFAULT_LOCALE"]),
            "SHOP": {
                "name": app.config["SHOP_NAME"],
                "address": app.config["SHOP_ADDRESS"],
                "phone": app.config["SHOP_PHONE"],
                "latitude": app.config["SHOP_LATITUDE"],
                "longitude": app.config["SHOP_LONGITUDE"],
                "city": app.config["SHOP_CITY"],
                "region": app.config["SHOP_REGION"],
                "postal_code": app.config["SHOP_POSTAL_CODE"],
                "country": app.config["SHOP_COUNTRY"],
                "hours_days": app.config["SHOP_HOURS_DAYS"],
                "hours_opens": app.config["SHOP_HOURS_OPENS"],
                "hours_closes": app.config["SHOP_HOURS_CLOSES"],
            },
            "MESSAGING_CONFIGURED": Config.messaging_configured(),
            "PAYMENTS_CONFIGURED": Config.payments_configured(),
        }


def _register_security_headers(app: Flask) -> None:
    from .utils.headers import register_security_headers

    register_security_headers(app)


def _register_cli(app: Flask) -> None:
    from .cli import register_cli

    register_cli(app)
