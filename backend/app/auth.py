from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
    Response,
    url_for,
    redirect,
    session,
    g,
)
from flask_jwt_extended import (
    create_access_token,
    current_user as flask_jwt_current_user,
)
from app.models import User, db
from app.utils.email_utils import send_password_reset_email
from app.extensions import api_token_required
import requests
import secrets
from datetime import datetime

auth = Blueprint("auth", __name__)


@auth.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create new user
    user = User(
        email=data["email"],
        is_active=False,  # Default is False, users need to be activated by an admin
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "User created successfully. Your account is pending activation by an administrator.",
                "user_id": user.id,
            }
        ),
        201,
    )


# Add OPTIONS handler for CORS preflight requests
@auth.route("/api/auth/login", methods=["OPTIONS"])
def login_options():
    response = Response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


@auth.route("/api/auth/login", methods=["POST"])
def login():
    """Simple login endpoint that accepts email/password and returns a token"""
    # Log the request for debugging
    current_app.logger.debug("LOGIN ENDPOINT CALLED")
    current_app.logger.debug("Request method: {}".format(request.method))
    current_app.logger.debug("Request headers: {}".format(dict(request.headers)))
    current_app.logger.debug("Request data: {}".format(request.get_data(as_text=True)))

    # Get the JSON data or form data
    data = None
    try:
        data = request.get_json(silent=True)
        if data is None:
            # Try to get form data instead
            data = request.form.to_dict() or {}
            current_app.logger.debug("Got form data: {}".format(data))
        else:
            current_app.logger.debug("Got JSON data: {}".format(data))
    except Exception as e:
        current_app.logger.error("Error parsing request data: {}".format(e))
        data = {}

    # Handle case with no data
    if not data:
        current_app.logger.error("No data provided in request")
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    # Basic validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find the user
    user = User.query.filter_by(email=email).first()

    # Check password
    if user and user.check_password(password):
        # Check if user is active
        if not user.is_active:
            return (
                jsonify(
                    {"error": "Account is inactive. Please contact an administrator."}
                ),
                403,
            )

        # Generate token
        try:
            token = create_access_token(
                identity=user.id, additional_claims={"sub": str(user.id)}
            )
            return jsonify({"message": "Login successful", "token": token}), 200
        except Exception as e:
            current_app.logger.error("Token generation error: {}".format(str(e)))
            return jsonify({"error": "Error generating token"}), 500

    # Invalid credentials
    return jsonify({"error": "Invalid email or password"}), 401


@auth.route("/api/auth/logout", methods=["POST"])
@api_token_required
def logout():
    # JWT logout is typically handled client-side by discarding the token.
    # Flask-JWT-Extended offers blocklisting for server-side revocation if needed.
    # Accessing g.current_user isn't strictly necessary here, but okay
    user = g.current_user
    current_app.logger.info(f"Logout endpoint called for user {user.id}")
    return (
        jsonify({"message": "Logout successful (token invalidated client-side)"}),
        200,
    )


@auth.route("/api/auth/me", methods=["GET"])
@api_token_required
def get_current_user():
    # Access the user loaded by the decorator via g.current_user
    user = g.current_user
    if not user:
        # This case should not happen if decorator works correctly
        return jsonify({"error": "User not found"}), 404
    # Explicitly convert user object to dict before jsonify
    return jsonify(user.to_dict()), 200


@auth.route("/api/auth/users/<int:user_id>/activate", methods=["POST"])
@api_token_required
def activate_user(user_id):
    # TODO: Add proper admin role checking using g.current_user
    requesting_user = g.current_user
    if not requesting_user.is_admin:  # Assuming an is_admin flag exists
        return jsonify({"error": "Admin privileges required"}), 403

    # Get the target user
    user_to_update = db.session.get(User, user_id)
    if not user_to_update:
        return jsonify({"error": "User not found"}), 404

    # Get request data
    data = request.get_json()
    is_active = data.get("is_active", True)

    # Update user active status
    if is_active:
        user_to_update.activate()
    else:
        user_to_update.deactivate()

    return (
        jsonify(
            {
                "message": f"User {user_to_update.email} {'activated' if is_active else 'deactivated'} successfully",
                "user": user_to_update.to_dict(),
            }
        ),
        200,
    )


@auth.route("/api/auth/password", methods=["PUT"])
@api_token_required
def update_password():
    """Update the current user's password"""
    # Access user via g
    user = g.current_user
    # Get request data
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Check if new password is provided
    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    # Check if current password matches using the user from g
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    # Update password on the user from g
    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200


@auth.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    """Request a password reset"""
    # Get request data
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Even if user doesn't exist, return success to prevent email enumeration
    if not user:
        current_app.logger.warning(
            f"Password reset requested for non-existent email: {email}"
        )
        return (
            jsonify(
                {
                    "message": "If your email is registered, you will receive a password reset link"
                }
            ),
            200,
        )

    # Check if user is active
    if not user.is_active:
        current_app.logger.warning(
            f"Password reset requested for inactive account: {email}"
        )
        return (
            jsonify(
                {
                    "message": "If your email is registered, you will receive a password reset link"
                }
            ),
            200,
        )

    # Generate and store reset token
    token = user.generate_reset_token()

    # Send reset email
    try:
        send_password_reset_email(user, token)
        return (
            jsonify(
                {
                    "message": "If your email is registered, you will receive a password reset link"
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(
            f"Failed to send password reset email to {email}: {str(e)}"
        )
        return jsonify({"error": "Failed to send password reset email"}), 500


@auth.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    """Reset password using token"""
    # Get request data
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    token = data.get("token")
    new_password = data.get("new_password")

    if not email or not token or not new_password:
        return jsonify({"error": "Email, token, and new password are required"}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Verify the token
    if not user.verify_reset_token(token):
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Update the password
    user.set_password(new_password)

    # Clear the reset token
    user.clear_reset_token()

    return jsonify({"message": "Password has been reset successfully"}), 200


# Google OAuth2 route
@auth.route("/api/auth/google", methods=["GET"])
def google_login():
    # Get Google OAuth2 configuration
    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    if not google_client_id:
        return jsonify({"error": "Google OAuth is not configured"}), 500

    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    # Redirect to Google's OAuth 2.0 server
    redirect_uri = request.url_root.rstrip("/") + url_for("auth.google_callback")

    params = {
        "client_id": google_client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "state": state,
        "response_type": "code",
        "prompt": "select_account",
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    from urllib.parse import urlencode

    auth_url += "?" + urlencode(params)

    return jsonify({"auth_url": auth_url})


@auth.route("/api/auth/google/callback", methods=["GET"])
def google_callback():
    # Verify state parameter to prevent CSRF
    state = request.args.get("state")
    if not state or session.pop("oauth_state", None) != state:
        return jsonify({"error": "Invalid state parameter"}), 400

    # Get authorization code
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = request.url_root.rstrip("/") + url_for("auth.google_callback")

    token_data = {
        "code": code,
        "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
        "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        # Get user info using the access token
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_response = requests.get(
            userinfo_url, headers={"Authorization": f'Bearer {tokens["access_token"]}'}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        # Check if user exists
        user = User.query.filter_by(google_id=userinfo["sub"]).first()

        if not user:
            # Check if email exists
            user = User.query.filter_by(email=userinfo["email"]).first()
            if user:
                # Update existing user with Google ID
                user.google_id = userinfo["sub"]
                user.picture = userinfo.get("picture")
            else:
                # Create new user
                user = User(
                    email=userinfo["email"],
                    google_id=userinfo["sub"],
                    picture=userinfo.get("picture"),
                    is_active=True,  # Auto-activate Google users
                )

            db.session.add(user)
            db.session.commit()

        # Generate JWT token
        token = create_access_token(
            identity=user.id, additional_claims={"sub": str(user.id)}
        )

        # Return token in query parameters for the frontend to consume
        frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/google-auth-callback?token={token}"

        return redirect(redirect_url)

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error in Google OAuth: {str(e)}")
        return jsonify({"error": "Failed to authenticate with Google"}), 500


# API Token Management Endpoints
@auth.route("/api/auth/tokens", methods=["GET"])
@api_token_required
def get_tokens():
    """Get all API tokens for the current user"""
    from app.models import ApiToken

    # Get the user from JWT or API token auth
    user = g.current_user
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Log the request for debugging
    current_app.logger.debug(f"Getting tokens for user ID: {user.id}")

    tokens = ApiToken.query.filter_by(user_id=user.id).all()
    # Always return a 200 with an empty array if no tokens exist
    return jsonify([token.to_dict() for token in tokens]), 200


@auth.route("/api/auth/tokens", methods=["POST"])
@api_token_required
def create_token():
    """Create a new API token for the current user"""
    from app.models import ApiToken

    # Get the user from JWT or API token auth
    user = g.current_user
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Token name is required"}), 400

    # Parse expiry date if provided
    expires_at = None
    if "expires_at" in data and data["expires_at"]:
        try:
            expires_at = datetime.fromisoformat(
                data["expires_at"].replace("Z", "+00:00")
            )
        except ValueError:
            return jsonify({"error": "Invalid expiry date format"}), 400

    # Generate a new token
    token_value = ApiToken.generate_token()
    token = ApiToken(
        user_id=user.id, token=token_value, name=name, expires_at=expires_at
    )

    db.session.add(token)
    db.session.commit()

    # Include the token value in the response (it will not be shown again)
    token_dict = token.to_dict()
    token_dict["token"] = token_value

    return jsonify(token_dict), 201


@auth.route("/api/auth/tokens/<int:token_id>", methods=["DELETE"])
@api_token_required
def revoke_token(token_id):
    """Revoke (delete) an API token"""
    from app.models import ApiToken

    # Get the user from JWT or API token auth
    user = g.current_user
    if not user:
        return jsonify({"error": "User not found"}), 404

    token = ApiToken.query.filter_by(id=token_id, user_id=user.id).first()
    if not token:
        return jsonify({"error": "Token not found"}), 404

    db.session.delete(token)
    db.session.commit()

    return jsonify({"message": "Token revoked successfully"}), 200


@auth.route("/api/auth/tokens/<int:token_id>", methods=["PUT"])
@api_token_required
def update_token(token_id):
    """Update an API token (name or expiry)"""
    from app.models import ApiToken

    # Get the user from JWT or API token auth
    user = g.current_user
    if not user:
        return jsonify({"error": "User not found"}), 404

    token = ApiToken.query.filter_by(id=token_id, user_id=user.id).first()
    if not token:
        return jsonify({"error": "Token not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update name if provided
    if "name" in data:
        token.name = data["name"]

    # Update expiry if provided
    if "expires_at" in data:
        if data["expires_at"]:
            try:
                token.expires_at = datetime.fromisoformat(
                    data["expires_at"].replace("Z", "+00:00")
                )
            except ValueError:
                return jsonify({"error": "Invalid expiry date format"}), 400
        else:
            token.expires_at = None

    # Update active status if provided
    if "is_active" in data:
        token.is_active = bool(data["is_active"])

    db.session.commit()

    return jsonify(token.to_dict()), 200


# Simple test route to verify authentication status
@auth.route("/api/auth/test", methods=["GET"])
@api_token_required
def auth_test():
    """Test authentication status"""

    user = g.current_user
    if not user:
        return jsonify({"error": "User not found"}), 404

    return (
        jsonify(
            {
                "message": "Authentication successful",
                "user_id": user.id,
                "email": user.email,
                "auth_type": "JWT" if flask_jwt_current_user else "API Token",
            }
        ),
        200,
    )
