import os
from datetime import timedelta


class Config:
    """Base configuration."""

    def __init__(self):
        # Initialize with environment variables or default values
        self.SECRET_KEY = (
            os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
        )
        self.SQLALCHEMY_DATABASE_URI = (
            os.environ.get("DATABASE_URL") or "sqlite:///:memory:"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # JWT Settings
        self.JWT_SECRET_KEY = (
            os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
        )
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
        self.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

        # CSRF Settings
        self.WTF_CSRF_ENABLED = True
        self.WTF_CSRF_CHECK_DEFAULT = (
            False  # Disable default CSRF checking, we'll use our custom implementation
        )
        self.WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
        self.WTF_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
        self.WTF_CSRF_SSL_STRICT = True

        # Cookie settings
        self.SESSION_COOKIE_SECURE = (
            os.environ.get("SECURE_COOKIES", "False").lower() == "true"
        )
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = (
            "Lax"  # Less restrictive than 'Strict', allows CSRF to work across domains
        )

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
        self.FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        self.BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

        # Google OAuth Config
        self.GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_DISCOVERY_URL = (
            "https://accounts.google.com/.well-known/openid-configuration"
        )
        # Session configuration
        self.SESSION_TYPE = "filesystem"
        self.SESSION_PERMANENT = False
        self.SESSION_USE_SIGNER = True
        self.SESSION_COOKIE_SECURE = (
            os.environ.get("SECURE_COOKIES", "False").lower() == "true"
        )
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = "Lax"
        # Allow session cookies from different domains (for OAuth flows)
        self.SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN")

        # Encryption settings
        self.ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")


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

        # Re-enable CSRF with improved configuration
        self.WTF_CSRF_ENABLED = True

        # Enhanced CSRF settings for cross-domain support
        self.WTF_CSRF_CHECK_DEFAULT = (
            False  # Disable default CSRF checking, we'll use our custom implementation
        )
        self.WTF_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
        self.WTF_CSRF_HEADERS = ["X-CSRFToken", "X-CSRF-Token"]
        self.WTF_CSRF_SSL_STRICT = False  # Allow HTTPS -> HTTP
        self.WTF_CSRF_TIME_LIMIT = 86400  # 24 hours instead of 1 hour


# Export a dictionary for easy access in create_app
config = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
