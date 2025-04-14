import os
from datetime import timedelta


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "instance", "app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Settings
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Ledger Settings
    LEDGER_PATH = (
        os.environ.get("LEDGER_PATH") or "/opt/homebrew/bin/ledger"
    )  # Default for Homebrew on Apple Silicon

    # Mail Settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.environ.get("MAIL_DEFAULT_SENDER") or "no-reply@kanakku.app"
    )

    # Application Settings
    FRONTEND_URL = os.environ.get("FRONTEND_URL") or "http://localhost:3000"

    # Google OAuth Config
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    # For development, you can use these OAuth credentials or set up your own in .env
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or None
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or None


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = "test-secret-key"
    SECRET_KEY = (
        "test-secret-key"  # Ensure SECRET_KEY is also set for testing consistency
    )
    LEDGER_PATH = "/opt/homebrew/bin/ledger"  # Ensure path is set for testing if needed


class ProductionConfig(Config):
    # Ensure secret keys are properly set in production
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    # Ensure Google OAuth credentials are properly set in production
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


# Export a dictionary for easy access in create_app
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
