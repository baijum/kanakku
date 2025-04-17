import os
from datetime import timedelta


class Config:
    """Base configuration."""

    def __init__(self):
        # Initialize with environment variables or default values
        self.SECRET_KEY = (
            os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
        )
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL"
        ) or "sqlite:///" + os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
            "instance",
            "app.db",
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # JWT Settings
        self.JWT_SECRET_KEY = (
            os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
        )
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
        self.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

        # Ledger Settings
        self.LEDGER_PATH = (
            os.environ.get("LEDGER_PATH") or "/opt/homebrew/bin/ledger"
        )  # Default for Homebrew on Apple Silicon

        # Mail Settings
        self.MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
        self.MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
        self.MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in [
            "true",
            "on",
            "1",
        ]
        self.MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
        self.MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
        self.MAIL_DEFAULT_SENDER = (
            os.environ.get("MAIL_DEFAULT_SENDER") or "no-reply@kanakku.app"
        )

        # Application Settings
        self.FRONTEND_URL = os.environ.get("FRONTEND_URL") or "http://localhost:3000"

        # Google OAuth Config
        self.GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_DISCOVERY_URL = (
            "https://accounts.google.com/.well-known/openid-configuration"
        )


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        # For development, you can use these OAuth credentials or set up your own in .env
        self.GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or None
        self.GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or None


class TestConfig(Config):
    __test__ = False

    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.WTF_CSRF_ENABLED = False
        self.JWT_SECRET_KEY = "test-secret-key"
        self.SECRET_KEY = (
            "test-secret-key"  # Ensure SECRET_KEY is also set for testing consistency
        )
        self.LEDGER_PATH = (
            "/opt/homebrew/bin/ledger"  # Ensure path is set for testing if needed
        )


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        # Ensure secret keys are properly set in production
        if os.environ.get("SECRET_KEY"):
            self.SECRET_KEY = os.environ.get("SECRET_KEY")
        if os.environ.get("JWT_SECRET_KEY"):
            self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        # Ensure Google OAuth credentials are properly set in production
        if os.environ.get("GOOGLE_CLIENT_ID"):
            self.GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        if os.environ.get("GOOGLE_CLIENT_SECRET"):
            self.GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


# Export a dictionary for easy access in create_app
config = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
