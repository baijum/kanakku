import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Ledger Settings
    LEDGER_FILE = os.environ.get('LEDGER_FILE') or 'ledger.dat'
    LEDGER_PATH = os.environ.get('LEDGER_PATH') or '/opt/homebrew/bin/ledger' # Default for Homebrew on Apple Silicon

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LEDGER_FILE = ':memory:' # Use in-memory or mock for tests
    JWT_SECRET_KEY = 'test-secret-key'
    SECRET_KEY = 'test-secret-key' # Ensure SECRET_KEY is also set for testing consistency
    LEDGER_PATH = '/opt/homebrew/bin/ledger' # Ensure path is set for testing if needed
    LOGIN_DISABLED = True  # Disable login_required for testing

class ProductionConfig(Config):
    pass

# Export a dictionary for easy access in create_app
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 