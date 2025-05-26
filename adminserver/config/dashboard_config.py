"""
Kanakku Monitoring Dashboard Configuration

Configuration settings for the monitoring dashboard application.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Flask configuration
    SECRET_KEY = (
        os.environ.get("DASHBOARD_SECRET_KEY") or "dev-secret-key-change-in-production"
    )
    WTF_CSRF_ENABLED = True

    # Dashboard settings
    UPDATE_INTERVAL = int(os.environ.get("DASHBOARD_UPDATE_INTERVAL", 30))  # seconds
    MAX_LOG_LINES = int(os.environ.get("DASHBOARD_MAX_LOG_LINES", 1000))

    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # CORS settings (for development)
    CORS_ORIGINS = (
        os.environ.get("DASHBOARD_CORS_ORIGINS", "").split(",")
        if os.environ.get("DASHBOARD_CORS_ORIGINS")
        else []
    )

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
    RATELIMIT_DEFAULT = "100 per hour"

    # Logging
    LOG_LEVEL = os.environ.get("DASHBOARD_LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

    # More verbose logging in development
    LOG_LEVEL = "DEBUG"

    # Allow CORS from localhost in development
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5001",
        "http://127.0.0.1:5001",
    ]


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False

    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Production logging
    LOG_LEVEL = "WARNING"

    # No CORS in production (served from same domain)
    CORS_ORIGINS = []

    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        Config.init_app(app)

        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

    # Faster updates for testing
    UPDATE_INTERVAL = 5

    # Reduced log lines for testing
    MAX_LOG_LINES = 100


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
