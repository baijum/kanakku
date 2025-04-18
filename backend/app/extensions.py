from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask import request, g, current_app
import functools
from werkzeug.exceptions import NotFound
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()


# Configure storage based on environment
def get_limiter_storage_uri():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url and not os.environ.get("TESTING"):
        return f"redis://{redis_url}"
    return "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
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
    return db.session.get(User, identity)


# Custom decorator for API token authentication
def api_token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        from .models import ApiToken, User
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from flask_jwt_extended.exceptions import (
            NoAuthorizationError,
            InvalidHeaderError,
            JWTDecodeError,
            WrongTokenError,
            RevokedTokenError,
            FreshTokenRequired,
            CSRFError,
        )

        try:
            # First try JWT token authentication
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                user = db.session.get(User, identity)
                if not user:
                    return {"error": "User associated with JWT not found"}, 401
                g.current_user = user
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
def expired_token_callback(_jwt_header, _jwt_data):
    """Handle expired JWT token"""
    return {"error": "Token has expired"}, 401


@jwt.unauthorized_loader
def unauthorized_callback(error):
    """Handle missing JWT token"""
    return {"error": "Missing or invalid authentication"}, 401


# Custom decorator for rate-limited routes with different limits
def auth_rate_limit(f):
    @functools.wraps(f)
    @limiter.limit("5 per minute")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


# More aggressive rate limiting for failed login attempts
def failed_login_limit(f):
    @functools.wraps(f)
    @limiter.limit("3 per minute")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function
