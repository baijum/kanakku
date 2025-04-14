from flask import Flask, jsonify, current_app, request
from flask_sqlalchemy import SQLAlchemy

# from flask_login import LoginManager # Remove if not used for API
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .extensions import db, mail  # Add mail
from .config import config
from .models import User

# Initialize JWTManager globally (or within create_app)
jwt = JWTManager()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)

    # Configure CORS to allow any origin
    CORS(
        app,
        origins=["*", "http://localhost:3000"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
        supports_credentials=True,
    )

    # Add a CORS after_request handler to ensure all responses have CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,Accept,X-Requested-With",
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
        )
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

    app.config.from_object(config[config_name])

    # Initialize extensions that don't depend on app context first
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    # login_manager.init_app(app) # Remove if not used
    # login_manager.login_view = 'auth.login' # Remove if not used

    # --- JWT Error Handlers --- #
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logging.error(f"JWT Expired. Header: {jwt_header}, Payload: {jwt_payload}")
        return jsonify(code=401, err="Token has expired"), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        app.logger.error(f"JWT Invalid. Error: {error_string}")
        return jsonify({"msg": f"Invalid token: {error_string}"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        app.logger.error(f"JWT Missing. Error: {error_string}")
        return jsonify({"msg": f"Missing Authorization Header: {error_string}"}), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        logging.warning(f"JWT Not Fresh. Header: {jwt_header}, Payload: {jwt_payload}")
        return jsonify(code=401, err="Fresh token required"), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        logging.warning(f"JWT Revoked. Header: {jwt_header}, Payload: {jwt_payload}")
        return jsonify(code=401, err="Token has been revoked"), 401

    @jwt.user_lookup_error_loader
    def user_lookup_error_callback(jwt_header, jwt_data):
        identity = jwt_data.get("sub") or jwt_data.get("identity", "Unknown")
        app.logger.error(f"Error loading user from JWT. Identity: {identity}")
        return jsonify({"msg": f"Error loading user {identity}"}), 401

    # --- End JWT Error Handlers --- #

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        logging.warning(f"JWT Data Received: {jwt_data}")
        # Try to get id from 'sub' claim first, then fall back to 'identity'
        identity = jwt_data.get("sub") or jwt_data.get("identity")
        if not identity:
            logging.error("JWT Claim 'sub' or 'identity' not found in jwt_data")
            return None
        # Handle both string and integer IDs - convert to int if string
        try:
            user_id = int(identity) if isinstance(identity, str) else identity
        except ValueError:
            logging.error(f"Could not convert JWT identity to int: {identity}")
            return None
        user = User.query.filter_by(id=user_id).one_or_none()
        if not user:
            logging.warning(f"User not found for ID: {user_id}")
        return user

    # --------------------------------------------

    # Now work within the app context for DB creation and blueprints
    with app.app_context():
        # Import models needed for create_all
        from .models import Transaction, Account, Preamble

        db.create_all()

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
        from .errors import errors as errors_blueprint

        app.register_blueprint(errors_blueprint)
        from .api import api as api_blueprint

        app.register_blueprint(api_blueprint)

        # Register error handlers (remain inside app_context)
        @app.errorhandler(404)
        def not_found_error(error):
            return jsonify({"error": "Not found"}), 404

        @app.errorhandler(405)
        def method_not_allowed_error(error):
            return jsonify({"error": "Method not allowed"}), 405

        @app.errorhandler(403)
        def forbidden_error(error):
            app.logger.error(f"403 Forbidden Error: {error}")
            app.logger.error(f"Request path: {request.path}")
            app.logger.error(f"Request method: {request.method}")
            app.logger.error(f"Request headers: {dict(request.headers)}")
            app.logger.error(f"Request data: {request.get_data(as_text=True)}")
            return (
                jsonify(
                    {
                        "error": "Forbidden - You do not have permission to access this resource"
                    }
                ),
                403,
            )

        @app.errorhandler(422)
        def unprocessable_entity_error(error):
            # Log the original error and its type
            logging.error(f"Global 422 Error Handler Triggered.", exc_info=True)
            logging.error(f"Original error type: {type(error)}")
            logging.error(
                f"Original error message: {getattr(error, 'description', 'N/A')}"
            )
            logging.error(f"Original error args: {getattr(error, 'args', 'N/A')}")

            # Determine a more specific message if possible
            error_msg = "Unprocessable Entity"
            if hasattr(error, "description"):
                if (
                    isinstance(error.description, dict)
                    and "message" in error.description
                ):
                    error_msg = error.description[
                        "message"
                    ]  # Extract specific message if available
                elif isinstance(error.description, str):
                    error_msg = error.description

            return (
                jsonify(
                    {
                        "error": "Unprocessable Entity",
                        "message": error_msg,  # Return more specific message
                    }
                ),
                422,
            )

        @app.errorhandler(500)
        def internal_error(error):
            # Ensure rollback happens within the session context
            try:
                db.session.rollback()
            except Exception as rollback_error:
                app.logger.error(f"Error during rollback: {rollback_error}")
            return jsonify({"error": "Internal server error"}), 500

    return app
