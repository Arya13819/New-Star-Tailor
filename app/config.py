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


class Config:
    # --- Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = False
    TESTING = False

    # --- Database ---
    # e.g. mysql+pymysql://nst_user:password@127.0.0.1:3306/nst_dev?charset=utf8mb4
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "")
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
    ORDER_NUMBER_PREFIX = "NST-"
    ORDER_NUMBER_PAD = 6
    MEASUREMENT_UNIT = "in"

    # --- Payment provider (connected later; see docs/PAYMENTS.md) ---
    PAYMENT_PROVIDER = os.environ.get("PAYMENT_PROVIDER", "manual")
    PAYMENT_PROVIDER_KEY = os.environ.get("PAYMENT_PROVIDER_KEY", "")
    PAYMENT_PROVIDER_SECRET = os.environ.get("PAYMENT_PROVIDER_SECRET", "")

    # --- WhatsApp / messaging (connected later) ---
    WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY", "")
    WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID", "")

    @staticmethod
    def messaging_configured() -> bool:
        return bool(os.environ.get("WHATSAPP_API_KEY") and os.environ.get("WHATSAPP_PHONE_ID"))

    @staticmethod
    def payments_configured() -> bool:
        provider = os.environ.get("PAYMENT_PROVIDER", "manual")
        if provider == "manual":
            return False
        return bool(os.environ.get("PAYMENT_PROVIDER_KEY"))


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    # Prefer a real MySQL/MariaDB via DATABASE_URL. Until that database is
    # provisioned (see docs/DATABASE_SETUP.md) fall back to a local SQLite
    # file so development is not blocked. Models are written MySQL-first.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(_INSTANCE, "nst_dev.sqlite")
    )


class TestingConfig(Config):
    ENV = "testing"
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    # Set TEST_DATABASE_URL to a MySQL/MariaDB database to run the suite on the
    # real dialect; otherwise an in-memory SQLite DB keeps tests runnable.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
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
