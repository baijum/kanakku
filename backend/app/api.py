from urllib.parse import urlparse

from flask import Blueprint, current_app, jsonify
from flask_wtf.csrf import generate_csrf
from werkzeug.exceptions import MethodNotAllowed

api = Blueprint("api", __name__)


# Health check endpoint
@api.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@api.route("/api/v1/csrf-token", methods=["GET"])
def get_csrf_token():
    """Get a CSRF token for the current session"""
    token = generate_csrf()
    response = jsonify({"csrf_token": token})

    # Log data for debugging
    current_app.logger.info(f"Generating CSRF token: {token[:10]}...")
    
    # Get domain from frontend URL for cookie (if configured)
    frontend_url = current_app.config.get("FRONTEND_URL")
    if frontend_url:
        current_app.logger.info(f"Frontend URL: {frontend_url}")
        try:
            parsed_url = urlparse(frontend_url)
            domain = parsed_url.netloc
            if ":" in domain:  # Remove port if present
                domain = domain.split(":")[0]

            current_app.logger.info(f"Setting cookie domain to: {domain}")
        except Exception as e:
            current_app.logger.error(f"Error parsing frontend URL: {e}")
            domain = None
    else:
        current_app.logger.info("No frontend URL configured")
        domain = None

    # Set CSRF token in a cookie as well for better cross-domain support
    response.set_cookie(
        "csrf_token",
        token,
        max_age=3600,  # 1 hour
        secure=True,
        httponly=False,  # Needs to be accessible from JavaScript
        samesite="None",  # Allow cross-site requests with credentials
        domain=domain if domain else None,
        path="/",
    )

    # Add CSRF token to response headers too
    response.headers["X-CSRFToken"] = token

    return response


@api.errorhandler(MethodNotAllowed)
def handle_405_error(e):
    return jsonify({"error": "Method not allowed"}), 405


# Remove all other duplicate/mocked endpoints below this line
