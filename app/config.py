"""Application configuration.

All secrets and environment-specific values come from environment variables
(loaded from a local ``.env`` file in development via python-dotenv).
Nothing sensitive is hard-coded here.
"""
from __future__ import annotations

import os
from datetime import timedelta

_ROOT = os.path.dirname(os.path.dirname(__file__))
_INSTANCE = os.path.join(_ROOT, "instance")


def _bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _normalized_db_url(env_var: str, default: str = "") -> str:
    """Render (and Heroku, and most managed-Postgres providers) hand out
    connection strings starting ``postgres://`` — a scheme SQLAlchemy 1.4+
    rejects outright. Rewritten to ``postgresql://`` so the same env var
    works whether it came from Render or was typed by hand."""
    url = os.environ.get(env_var, default)
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


class Config:
    # --- Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = False
    TESTING = False

    # --- Database ---
    # e.g. postgresql+psycopg2://user:password@host:5432/nst_prod
    # (MySQL/MariaDB also still works locally: mysql+pymysql://...)
    SQLALCHEMY_DATABASE_URI = _normalized_db_url("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # --- Sessions / cookies ---
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)

    # --- CSRF ---
    WTF_CSRF_TIME_LIMIT = None  # tie CSRF token lifetime to the session

    # --- Internationalisation ---
    LANGUAGES = {"en": "English", "hi": "हिन्दी"}
    BABEL_DEFAULT_LOCALE = os.environ.get("DEFAULT_LOCALE", "en")
    BABEL_DEFAULT_TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
    BABEL_TRANSLATION_DIRECTORIES = "translations"

    # --- Uploads (reference images) ---
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", "8")) * 1024 * 1024
    UPLOAD_DIR = os.environ.get(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "uploads"),
    )
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

    # --- Rate limiting ---
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True

    # --- Business defaults (all overridable from the Settings table at runtime) ---
    SHOP_NAME = "New Star Tailor"
    SHOP_ADDRESS = (
        "Old UCO Bank Gully, Near Patel Plaza, Tagore Marg, "
        "Neemuch, Madhya Pradesh, India"
    )
    SHOP_PHONE = "9352672795"
    SHOP_LATITUDE = "24.4570252"
    SHOP_LONGITUDE = "74.870045"
    SHOP_CITY = "Neemuch"
    SHOP_REGION = "Madhya Pradesh"
    SHOP_POSTAL_CODE = "458441"
    SHOP_COUNTRY = "IN"
    SHOP_HOURS_DAYS = "Mo-Sa"
    SHOP_HOURS_OPENS = "10:00"
    SHOP_HOURS_CLOSES = "20:00"
    ORDER_NUMBER_PREFIX = "NST-"
    # Minimum digit width, e.g. NST-0001. Not a hard cap — order #10000 still
    # prints in full as NST-10000, so this never needs to be "widened" later;
    # raise it only to change how many leading zeros a low order number shows.
    ORDER_NUMBER_PAD = 4
    MEASUREMENT_UNIT = "in"

    # --- Payment provider (connected later; see docs/PAYMENTS.md) ---
    PAYMENT_PROVIDER = os.environ.get("PAYMENT_PROVIDER", "manual")
    PAYMENT_PROVIDER_KEY = os.environ.get("PAYMENT_PROVIDER_KEY", "")
    PAYMENT_PROVIDER_SECRET = os.environ.get("PAYMENT_PROVIDER_SECRET", "")

    # --- SMS messaging (connected later) ---
    # Plain SMS only — never WhatsApp. India requires DLT-registered
    # sender IDs/templates for transactional SMS regardless of provider.
    SMS_API_KEY = os.environ.get("SMS_API_KEY", "")
    SMS_SENDER_ID = os.environ.get("SMS_SENDER_ID", "")

    @staticmethod
    def messaging_configured() -> bool:
        return bool(os.environ.get("SMS_API_KEY") and os.environ.get("SMS_SENDER_ID"))

    @staticmethod
    def payments_configured() -> bool:
        provider = os.environ.get("PAYMENT_PROVIDER", "manual")
        if provider == "manual":
            return False
        return bool(os.environ.get("PAYMENT_PROVIDER_KEY"))


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    # Prefer a real Postgres/MySQL via DATABASE_URL. Until that database is
    # provisioned fall back to a local SQLite file so development is never
    # blocked.
    SQLALCHEMY_DATABASE_URI = _normalized_db_url("DATABASE_URL") or (
        "sqlite:///" + os.path.join(_INSTANCE, "nst_dev.sqlite")
    )


class TestingConfig(Config):
    ENV = "testing"
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    # Set TEST_DATABASE_URL to a Postgres/MySQL database to run the suite on
    # the real dialect; otherwise an in-memory SQLite DB keeps tests runnable.
    SQLALCHEMY_DATABASE_URI = _normalized_db_url(
        "TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:"
    )
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    ENV = "production"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def resolve_config(name: str | None = None) -> type[Config]:
    key = (name or os.environ.get("FLASK_ENV") or "production").strip().lower()
    return CONFIG_MAP.get(key, ProductionConfig)
