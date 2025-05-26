import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler

from flask import Flask, g, has_request_context, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from .accounts_bp import accounts_bp
from .api import api as api_bp
from .auth_bp import auth_bp
from .books_bp import books_bp
from .config import config
from .email_automation import email_automation as email_automation_bp
from .errors import errors as errors_bp
from .extensions import db, jwt, limiter, login_manager, mail, setup_csrf
from .ledger import ledger as ledger_bp
from .mappings import mappings_bp
from .preamble import preamble as preamble_bp
from .reports_bp import reports_bp
from .settings import settings as settings_bp
from .swagger import swagger as swagger_bp
from .transactions_bp import transactions_bp


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

    # Serve favicon.ico
    @app.route("/favicon.ico")
    def favicon():
        # In a real app, you'd likely have a favicon.ico in a static folder
        # return send_from_directory(os.path.join(app.root_path, 'static'),
        #                            'favicon.ico', mimetype='image/vnd.microsoft.icon')
        # For now, just return No Content to prevent 404s
        return "", 204

    # Load configuration based on config_name
    config_instance = config[config_name]()

    # Transfer config from instance to Flask app.config
    for key in dir(config_instance):
        if not key.startswith("_"):  # Skip private attributes
            value = getattr(config_instance, key)
            if not callable(value):  # Skip methods
                app.config[key] = value

    # Initialize Flask-Session
    # Session(app)

    # Configure CORS to allow any origin
    CORS(
        app,
        origins=[app.config["FRONTEND_URL"]],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-CSRFToken"],
        expose_headers=["Content-Type", "X-CSRFToken"],
    )

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Initialize CSRF protection with our custom validator
    setup_csrf(app)  # This function now calls csrf.init_app internally

    # Initialize Flask-Migrate
    _ = Migrate(app, db)

    # Setup logging after config is loaded
    setup_logging(app)

    # Request ID middleware
    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())
        app.logger.debug(f"Request started: {request.method} {request.path}")

    # Global CSRF exemption logic if needed
    @app.before_request
    def csrf_protect():
        if request.method != "GET" and request.path.startswith("/api/v1/"):
            # Log CSRF debug info
            app.logger.debug(
                f"CSRF check for {request.path} - Headers: {request.headers.get('X-CSRFToken', 'NONE')}"
            )

            # Check for API token authentication and exempt from CSRF if found
            x_api_key = request.headers.get("X-API-Key")
            auth_header = request.headers.get("Authorization", "")

            # If API token authentication is being used, exempt from CSRF
            if x_api_key or auth_header.startswith("Token "):
                app.logger.debug(
                    f"API token detected, exempting from CSRF: {request.path}"
                )
                request._csrf_exempt = True

    @app.after_request
    def log_response(response):
        app.logger.debug(
            f"Request completed: {request.method} {request.path} - Status: {response.status_code}"
        )

        # Add security headers
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com; "
            "img-src 'self' data:"
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
        app.register_blueprint(auth_bp)
        app.register_blueprint(transactions_bp)
        app.register_blueprint(accounts_bp)
        app.register_blueprint(books_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(ledger_bp)
        app.register_blueprint(preamble_bp)
        app.register_blueprint(mappings_bp)
        app.register_blueprint(errors_bp)
        app.register_blueprint(swagger_bp)
        app.register_blueprint(settings_bp)
        app.register_blueprint(email_automation_bp)

    # Rate limiting error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(
            f"Rate limit exceeded: {request.remote_addr} - {request.method} {request.path}"
        )
        return jsonify(error="Rate limit exceeded. Please try again later."), 429

    # Apply ProxyFix middleware to handle reverse proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    return app
