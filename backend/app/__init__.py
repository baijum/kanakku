from flask import Flask, request, g, has_request_context, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import logging
import uuid
import sys
import os
from logging.handlers import RotatingFileHandler

from .extensions import db, login_manager, mail, jwt, limiter, csrf, handle_csrf_error
from .config import config


def setup_logging(app):
    """Configure application logging with structured formatting."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Configure the log formatter with more information
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(request_id)s] %(module)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # File handler for all logs (rotating to keep file size manageable)
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, "kanakku.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Error log file for errors only
    error_file_handler = RotatingFileHandler(
        os.path.join(logs_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # Set the base logger level
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # Clear existing handlers and add our custom handlers
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    app.logger.addHandler(console_handler)

    # Add filter to inject request ID into log records
    class RequestIDLogFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, "request_id"):
                record.request_id = "no_request_id"
                # Only try to get request ID if we're in a request context
                if has_request_context():
                    record.request_id = getattr(g, "request_id", "no_request_id")
            return True

    for handler in app.logger.handlers:
        handler.addFilter(RequestIDLogFilter())

    # Log application startup
    app.logger.info("Application startup complete")


def create_app(config_name="default"):
    app = Flask(__name__)

    # Load configuration based on config_name
    config_instance = config[config_name]()

    # Transfer config from instance to Flask app.config
    for key in dir(config_instance):
        if not key.startswith("_"):  # Skip private attributes
            value = getattr(config_instance, key)
            if not callable(value):  # Skip methods
                app.config[key] = value

    # Configure CORS to allow any origin
    CORS(app, origins=[app.config["FRONTEND_URL"]], supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Initialize CSRF protection
    csrf.init_app(app)
    app.register_error_handler(400, handle_csrf_error)

    # Initialize Flask-Migrate
    _ = Migrate(app, db)

    # Setup logging after config is loaded
    setup_logging(app)

    # Request ID middleware
    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())
        app.logger.debug(f"Request started: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        app.logger.debug(
            f"Request completed: {request.method} {request.path} - Status: {response.status_code}"
        )

        # Add security headers
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database: {str(e)}", exc_info=True)

        # Register blueprints
        from .auth import auth as auth_blueprint

        app.register_blueprint(auth_blueprint)

        from .ledger import ledger as ledger_blueprint

        app.register_blueprint(ledger_blueprint)

        from .reports import reports as reports_blueprint

        app.register_blueprint(reports_blueprint)

        from .transactions import transactions as transactions_blueprint

        app.register_blueprint(transactions_blueprint)

        from .accounts import accounts as accounts_blueprint

        app.register_blueprint(accounts_blueprint)

        from .preamble import preamble as preamble_blueprint

        app.register_blueprint(preamble_blueprint)

        from .books import books as books_blueprint

        app.register_blueprint(books_blueprint)

        from .errors import errors as errors_blueprint

        app.register_blueprint(errors_blueprint)

        from .api import api as api_blueprint

        app.register_blueprint(api_blueprint)

        # Register Swagger UI blueprint
        from .swagger import swagger as swagger_blueprint

        app.register_blueprint(swagger_blueprint)

    # Rate limiting error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(
            f"Rate limit exceeded: {request.remote_addr} - {request.method} {request.path}"
        )
        return jsonify(error="Rate limit exceeded. Please try again later."), 429

    return app
