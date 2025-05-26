import functools
import os

from flask import current_app, g, jsonify, request
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import NotFound

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()
csrf = CSRFProtect()


# Define a function to handle CSRF validation that includes header tokens
def custom_csrf_check():
    """Custom CSRF check that works with header-based tokens"""
    from flask import abort, current_app, request
    from flask_wtf.csrf import validate_csrf

    # Skip for exempted views or methods
    if request.method not in current_app.config.get(
        "WTF_CSRF_METHODS", ["POST", "PUT", "PATCH", "DELETE"]
    ):
        return

    # Skip if the endpoint doesn't exist
    if not request.endpoint:
        return

    # Skip if the view has the csrf_exempt decorator
    view_func = current_app.view_functions.get(request.endpoint)
    if view_func and getattr(view_func, "_csrf_exempt", False):
        return

    # Skip CSRF validation for API token requests
    # Check if X-API-Key header is present (API token authentication)
    if request.headers.get("X-API-Key"):
        return

    # Check if Authorization header contains a Token (API token authentication)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Token "):
        return

    # Try to get the token from header
    token = request.headers.get("X-CSRFToken")

    # If not in header, try X-CSRF-Token (alternative spelling)
    if not token:
        token = request.headers.get("X-CSRF-Token")

    # If not in headers, fallback to checking cookies
    if not token:
        token = request.cookies.get("csrf_token")

    # If we found a token, validate it
    if token:
        try:
            validate_csrf(token)
            return  # Valid token
        except Exception as e:
            current_app.logger.error(f"CSRF validation error: {str(e)}")
            abort(400)  # Use Flask's abort to trigger the error handler

    # If no token was found in headers or cookies, let the default CSRF handling take over
    # The default handling will check form data and raise an error if needed


# Setup function to register our custom CSRF handler
def setup_csrf(app):
    """Set up custom CSRF handling with header support"""
    csrf.init_app(app)

    # Register our custom check function as a before_request handler
    app.before_request(custom_csrf_check)

    # Register the error handler
    app.register_error_handler(400, handle_csrf_error)


# Configure storage based on environment
def get_limiter_storage_uri():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url and not os.environ.get("TESTING"):
        return redis_url
    return "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri=get_limiter_storage_uri(),
    strategy="fixed-window",
)


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    user = db.session.get(User, user_id)
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from .models import User

    identity = jwt_data["sub"]
    # Convert string identity back to integer for database lookup
    try:
        user_id = int(identity)
        return db.session.get(User, user_id)
    except (ValueError, TypeError):
        return None


# Custom decorator for API token authentication
def api_token_required(f):
    # First apply csrf_exempt to the function
    f = csrf_exempt(f)

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        from flask_jwt_extended.exceptions import (
            CSRFError,
            FreshTokenRequired,
            InvalidHeaderError,
            JWTDecodeError,
            NoAuthorizationError,
            RevokedTokenError,
            WrongTokenError,
        )

        from .models import ApiToken, User

        try:
            # First try JWT token authentication
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                # Convert string identity back to integer for database lookup
                try:
                    user_id = int(identity)
                    user = db.session.get(User, user_id)
                except (ValueError, TypeError):
                    user = None
                if not user:
                    return {"error": "User associated with JWT not found"}, 401
                g.current_user = user
                g.auth_type = "JWT"
                # Call the actual route function
                return f(*args, **kwargs)
            except (
                NoAuthorizationError,
                InvalidHeaderError,
                JWTDecodeError,
                WrongTokenError,
                RevokedTokenError,
                FreshTokenRequired,
                CSRFError,
            ) as jwt_error:
                # JWT authentication failed or specific JWT error occurred, try API token
                current_app.logger.debug(
                    f"JWT Auth failed/not provided: {jwt_error}. Trying API Token."
                )

                # Check for X-API-Key header first
                x_api_key = request.headers.get("X-API-Key", "").strip()
                if x_api_key:
                    # Look up the token directly from the X-API-Key header
                    api_token = ApiToken.query.filter_by(token=x_api_key).first()

                    # If token exists and is valid
                    if api_token and api_token.is_valid():
                        user = db.session.get(User, api_token.user_id)
                        if user:
                            g.current_user = user
                            g.auth_type = "API Token"
                            api_token.update_last_used()
                            # Call the actual route function if API token auth succeeds
                            return f(*args, **kwargs)

                # If X-API-Key didn't work, try Authorization header
                auth_header = request.headers.get("Authorization", "").strip()

                # If no Authorization header is provided at all
                if not auth_header:
                    return {"error": "Authentication required"}, 401

                # Check if it's an API token (Token prefix)
                if auth_header.startswith("Token "):
                    token_value = auth_header.split(" ", 1)[1].strip()

                    # Look up the token
                    api_token = ApiToken.query.filter_by(token=token_value).first()

                    # If token exists and is valid
                    if api_token and api_token.is_valid():
                        user = db.session.get(User, api_token.user_id)
                        if user:
                            g.current_user = user
                            g.auth_type = "API Token"
                            api_token.update_last_used()
                            # Call the actual route function again if API token auth succeeds
                            return f(*args, **kwargs)

                # Authentication failed (neither valid JWT nor valid API token)
                current_app.logger.warning(
                    f"Authentication failed for request to {request.path}"
                )
                return {"error": "Authentication required"}, 401
            # Let NotFound exceptions propagate to Flask's handler
            except NotFound:
                raise
            except Exception as e:
                # Catch other unexpected errors during the core route execution
                current_app.logger.error(
                    f"Unexpected error during authenticated route execution: {str(e)}",
                    exc_info=True,
                )
                # It might be better to return a 500 here instead of 401
                return {"error": "An internal server error occurred"}, 500

        except NotFound:
            # Catch NotFound if it happens *outside* the inner try-except (less likely)
            # Let Flask handle the 404 response
            raise
        except Exception as e:
            # Catch any other unexpected errors during setup/auth logic
            current_app.logger.error(
                f"Unexpected error in auth wrapper: {str(e)}", exc_info=True
            )
            return {
                "error": "An internal server error occurred during authentication"
            }, 500

    return decorated_function


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid JWT token"""
    return {"error": "Invalid token"}, 401


@jwt.expired_token_loader
def expired_token_callback(_jwt_header, jwt_data):
    """Handle expired JWT token"""
    # Log the token expiry event with user information
    try:
        user_id = jwt_data.get("sub") if jwt_data else "unknown"
        current_app.logger.info(f"JWT token expired for user ID: {user_id}")
    except Exception as e:
        current_app.logger.error(f"Error logging token expiry: {str(e)}")

    return {"error": "Token has expired", "code": "token_expired"}, 401


@jwt.unauthorized_loader
def unauthorized_callback(error):
    """Handle missing JWT token"""
    return {"error": "Missing or invalid authentication"}, 401


# Custom decorator for rate-limited routes with different limits
def auth_rate_limit(f):
    @functools.wraps(f)
    @limiter.limit("50 per minute")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


# More aggressive rate limiting for failed login attempts
def failed_login_limit(f):
    @functools.wraps(f)
    @limiter.limit("30 per minute")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


# CSRF error handler
def handle_csrf_error(e):
    current_app.logger.warning(
        f"CSRF validation failed: {request.remote_addr} - {request.method} {request.path}"
    )
    return jsonify(error="CSRF validation failed. Please try again."), 400


# Decorator to exempt routes from CSRF protection
def csrf_exempt(view):
    """Mark a view as exempt from CSRF protection."""
    if hasattr(view, "_csrf_exempt"):
        return view

    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        return view(*args, **kwargs)

    wrapped._csrf_exempt = True
    return wrapped
