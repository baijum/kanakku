"""Authentication routes using service layer."""

from flask import Blueprint, current_app, g, jsonify, redirect, request
from marshmallow import ValidationError

from ..extensions import api_token_required, auth_rate_limit, csrf_exempt
from ..shared.services import format_api_response, format_error_response
from .schemas import (
    CreateTokenSchema,
    ForgotPasswordSchema,
    GoogleTokenSchema,
    LoginSchema,
    RegisterSchema,
    ResetPasswordSchema,
    UpdatePasswordSchema,
    UpdateTokenSchema,
)
from .services import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/auth/register", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def register():
    """Register endpoint - explicitly exempt from CSRF protection"""
    current_app.logger.info(
        "Register endpoint called - CSRF protection disabled for this endpoint"
    )

    try:
        # Get raw data first to check honeypot before validation
        raw_data = request.get_json() or {}

        # Check honeypot first (before schema validation)
        if AuthService.check_honeypot(raw_data):
            return (
                jsonify(
                    format_error_response("Registration failed. Please try again.")
                ),
                400,
            )

        # Validate input data
        schema = RegisterSchema()
        data = schema.load(raw_data)

        # Verify hCaptcha
        if not AuthService.verify_hcaptcha(data["hcaptcha_token"], request.remote_addr):
            current_app.logger.warning(
                f"hCaptcha verification failed for registration attempt with email: {data.get('email', 'unknown')}"
            )
            return (
                jsonify(
                    format_error_response(
                        "Captcha verification failed. Please try again."
                    )
                ),
                400,
            )

        # Create user
        user, error = AuthService.create_user(
            email=data["email"], password=data["password"], name=data.get("name")
        )

        if error:
            return jsonify(format_error_response(error)), 400

        # Format response (maintain old API contract)
        return (
            jsonify(
                {
                    "message": "User and default book created successfully.",
                    "user_id": user.id,
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/api/v1/auth/login", methods=["OPTIONS"])
@csrf_exempt
def login_options():
    """Handle preflight requests for login endpoint"""
    return "", 200


@auth_bp.route("/api/v1/auth/login", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def login():
    """Login endpoint - explicitly exempt from CSRF protection"""
    current_app.logger.info(
        "Login endpoint called - CSRF protection disabled for this endpoint"
    )

    try:
        # Validate input data
        schema = LoginSchema()
        data = schema.load(request.get_json() or {})

        # Authenticate user
        user, error = AuthService.authenticate_user(
            email=data["email"],
            password=data["password"],
            remote_ip=request.remote_addr,
        )

        if error:
            return jsonify(format_error_response(error)), 401

        # Generate token
        token = AuthService.generate_access_token(user)

        # Format response (maintain old API contract)
        return jsonify({"token": token, "user": user.to_dict()}), 200

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify(format_error_response("Login failed")), 500


@auth_bp.route("/api/v1/auth/logout", methods=["POST"])
@api_token_required
def logout():
    """Logout endpoint"""
    # JWT logout is typically handled client-side by discarding the token.
    # Flask-JWT-Extended offers blocklisting for server-side revocation if needed.
    return jsonify(format_api_response(None, "Logged out successfully")), 200


@auth_bp.route("/api/v1/auth/me", methods=["GET"])
@api_token_required
def get_current_user():
    """Get current user information"""
    try:
        # Maintain old API contract - return user data directly
        return jsonify(g.current_user.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error getting current user: {str(e)}")
        return jsonify({"error": "Failed to get user information"}), 500


@auth_bp.route("/api/v1/auth/profile", methods=["GET"])
@api_token_required
def get_user_profile():
    """Get user profile information"""
    try:
        user_data = g.current_user.to_dict()
        return jsonify(format_api_response(user_data)), 200
    except Exception as e:
        current_app.logger.error(f"Error getting user profile: {str(e)}")
        return jsonify(format_error_response("Failed to get user profile")), 500


@auth_bp.route("/api/v1/auth/toggle-status", methods=["POST"])
@api_token_required
def toggle_user_status():
    """Toggle current user's status"""
    try:
        # Get request data
        data = request.get_json() or {}
        is_active = data.get("is_active")

        if is_active is None:
            return jsonify({"error": "is_active field is required"}), 400

        # Update user active status
        if is_active:
            g.current_user.activate()
        else:
            g.current_user.deactivate()

        # Maintain old API contract
        return (
            jsonify(
                {
                    "message": f"Account {'activated' if is_active else 'deactivated'} successfully",
                    "user": g.current_user.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Error toggling user status: {str(e)}")
        return jsonify({"error": "Failed to update user status"}), 500


@auth_bp.route("/api/v1/auth/users/<int:user_id>/activate", methods=["POST"])
@api_token_required
def activate_user(user_id):
    """Activate user by ID (admin function)"""
    try:
        # TODO: Add proper admin role checking using g.current_user
        requesting_user = g.current_user
        if not requesting_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403

        # Get the target user
        from ..models import User

        user_to_update = User.query.get(user_id)
        if not user_to_update:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json() or {}
        is_active = data.get("is_active", True)

        # Update user active status
        if is_active:
            user_to_update.activate()
        else:
            user_to_update.deactivate()

        # Maintain old API contract
        return (
            jsonify(
                {
                    "message": f"User {user_to_update.email} {'activated' if is_active else 'deactivated'} successfully",
                    "user": user_to_update.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error activating user: {str(e)}")
        return jsonify({"error": "Failed to activate user"}), 500


@auth_bp.route("/api/v1/auth/password", methods=["PUT"])
@api_token_required
def update_password():
    """Update user password"""
    try:
        # Validate input data
        schema = UpdatePasswordSchema()
        data = schema.load(request.get_json() or {})

        # Verify current password
        if not g.current_user.check_password(data["current_password"]):
            return jsonify(format_error_response("Current password is incorrect")), 401

        # Update password
        g.current_user.set_password(data["new_password"])
        from ..extensions import db

        db.session.commit()

        return jsonify({"message": "Password updated successfully"}), 200

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except Exception as e:
        current_app.logger.error(f"Error updating password: {str(e)}")
        return jsonify(format_error_response("Failed to update password")), 500


@auth_bp.route("/api/v1/auth/forgot-password", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def forgot_password():
    """Forgot password endpoint"""
    try:
        # Validate input data
        schema = ForgotPasswordSchema()
        data = schema.load(request.get_json() or {})

        # Verify hCaptcha
        if not AuthService.verify_hcaptcha(data["hcaptcha_token"], request.remote_addr):
            return (
                jsonify(
                    format_error_response(
                        "Captcha verification failed. Please try again."
                    )
                ),
                400,
            )

        # Initiate password reset
        success, error = AuthService.initiate_password_reset(
            data["email"], request.remote_addr
        )

        # Always return success to prevent email enumeration (maintain old API contract)
        return (
            jsonify(
                {"message": "If the email exists, a password reset link has been sent"}
            ),
            200,
        )

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except Exception as e:
        current_app.logger.error(f"Error in forgot password: {str(e)}")
        return (
            jsonify(format_error_response("Failed to process password reset request")),
            500,
        )


@auth_bp.route("/api/v1/auth/reset-password", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def reset_password():
    """Reset password endpoint"""
    try:
        # Validate input data
        schema = ResetPasswordSchema()
        data = schema.load(request.get_json() or {})

        # Verify hCaptcha
        if not AuthService.verify_hcaptcha(data["hcaptcha_token"], request.remote_addr):
            return (
                jsonify(
                    format_error_response(
                        "Captcha verification failed. Please try again."
                    )
                ),
                400,
            )

        # Reset password
        success, error = AuthService.reset_password_with_token(
            data["token"], data["new_password"]
        )

        if success:
            return jsonify({"message": "Password reset successfully"}), 200
        else:
            return jsonify({"error": error or "Failed to reset password"}), 400

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except Exception as e:
        current_app.logger.error(f"Error resetting password: {str(e)}")
        return jsonify(format_error_response("Failed to reset password")), 500


# Google OAuth Routes


@auth_bp.route("/api/v1/auth/google", methods=["GET"])
@csrf_exempt
def google_login():
    """Initiate Google OAuth login"""
    try:
        auth_url, state, error = AuthService.generate_google_auth_url()

        if error:
            return jsonify({"error": error}), 500

        # Maintain old API contract
        return jsonify({"auth_url": auth_url}), 200

    except Exception as e:
        current_app.logger.error(f"Error generating Google auth URL: {str(e)}")
        return (
            jsonify(format_error_response("Failed to generate authorization URL")),
            500,
        )


@auth_bp.route("/api/v1/auth/google/callback", methods=["GET"])
@csrf_exempt
def google_callback():
    """Handle Google OAuth callback"""
    try:
        current_app.logger.info(f"Google auth callback received. URL: {request.url}")
        current_app.logger.debug(f"Google auth callback query params: {request.args}")

        code = request.args.get("code")
        state = request.args.get("state")

        user, redirect_url, error = AuthService.handle_google_callback(code, state)

        if error:
            if redirect_url:
                return redirect(redirect_url)
            return jsonify(format_error_response(error)), 400

        return redirect(redirect_url)

    except Exception as e:
        current_app.logger.error(f"Unexpected error in Google callback: {str(e)}")
        import traceback

        current_app.logger.error(traceback.format_exc())
        return (
            jsonify(
                format_error_response(
                    "Internal server error during Google authentication"
                )
            ),
            500,
        )


@auth_bp.route("/api/v1/auth/google", methods=["POST"])
@csrf_exempt
def google_token_auth():
    """Handle Google authentication with a token directly from the frontend"""
    try:
        # Validate input data
        schema = GoogleTokenSchema()
        data = schema.load(request.get_json() or {})

        # Verify the token
        userinfo = AuthService.verify_oauth_token(data["token"])

        # Create or update user
        user, error = AuthService.create_or_update_google_user(userinfo)
        if error:
            return jsonify(format_error_response(error)), 400

        # Check if user is active
        if not user.is_active:
            current_app.logger.warning(
                f"Google token auth: Inactive user attempted login: {user.email}"
            )
            return (
                jsonify(
                    format_error_response(
                        "Account is deactivated. Please contact support."
                    )
                ),
                403,
            )

        # Generate JWT token
        token = AuthService.generate_access_token(user)

        # Maintain old API contract
        return jsonify({"token": token, "user": user.to_dict()}), 200

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except ValueError as e:
        current_app.logger.warning(f"Invalid Google token: {str(e)}")
        return jsonify(format_error_response("Invalid Google token")), 400
    except Exception as e:
        current_app.logger.error(f"Error in Google token auth: {str(e)}")
        return jsonify(format_error_response("Google authentication failed")), 500


# API Token Management Routes


@auth_bp.route("/api/v1/auth/tokens", methods=["GET"])
@api_token_required
def get_tokens():
    """Get user's API tokens"""
    try:
        tokens = AuthService.get_user_tokens(g.current_user)

        # Return tokens without including the token value for security (maintain old API contract)
        return (
            jsonify(
                [
                    {k: v for k, v in token.to_dict().items() if k != "token"}
                    for token in tokens
                ]
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error getting tokens: {str(e)}")
        return jsonify(format_error_response("Failed to get tokens")), 500


@auth_bp.route("/api/v1/auth/tokens", methods=["POST"])
@api_token_required
def create_token():
    """Create a new API token"""
    try:
        # Validate input data
        schema = CreateTokenSchema()
        data = schema.load(request.get_json() or {})

        # Create token
        token, error = AuthService.create_api_token(
            user=g.current_user,
            name=data["name"],
            description=data.get("description"),
            expires_at=data.get("expires_at"),
        )

        if error:
            return jsonify({"error": error}), 400

        # Include the token value in the response (it will not be shown again) - maintain old API contract
        token_data = token.to_dict()
        token_data["token"] = token.token  # Include the actual token value

        return jsonify(token_data), 201

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except Exception as e:
        current_app.logger.error(f"Error creating token: {str(e)}")
        return jsonify(format_error_response("Failed to create token")), 500


@auth_bp.route("/api/v1/auth/tokens/<int:token_id>", methods=["DELETE"])
@api_token_required
def revoke_token(token_id):
    """Revoke an API token"""
    try:
        token = AuthService.get_api_token_by_id(token_id, g.current_user)
        if not token:
            return jsonify(format_error_response("Token not found")), 404

        if AuthService.revoke_api_token(token):
            return jsonify({"message": "Token revoked successfully"}), 200
        else:
            return jsonify({"error": "Failed to revoke token"}), 500

    except Exception as e:
        current_app.logger.error(f"Error revoking token: {str(e)}")
        return jsonify(format_error_response("Failed to revoke token")), 500


@auth_bp.route("/api/v1/auth/tokens/<int:token_id>", methods=["PUT"])
@api_token_required
def update_token(token_id):
    """Update an API token"""
    try:
        # Validate input data
        schema = UpdateTokenSchema()
        data = schema.load(request.get_json() or {})

        token = AuthService.get_api_token_by_id(token_id, g.current_user)
        if not token:
            return jsonify(format_error_response("Token not found")), 404

        # Update token
        # Handle expires_at specially to distinguish between not provided and explicitly None
        expires_at = data.get("expires_at", ...)  # Use sentinel value if not provided

        if AuthService.update_api_token(
            token=token,
            name=data.get("name"),
            description=data.get("description"),
            expires_at=expires_at,
            is_active=data.get("is_active"),
        ):
            return jsonify(token.to_dict()), 200
        else:
            return jsonify({"error": "Token name already exists"}), 400

    except ValidationError as e:
        return jsonify(format_error_response("Validation failed", e.messages)), 400
    except Exception as e:
        current_app.logger.error(f"Error updating token: {str(e)}")
        return jsonify(format_error_response("Failed to update token")), 500


# Utility Routes


@auth_bp.route("/api/v1/auth/test", methods=["GET"])
@api_token_required
def auth_test():
    """Test authentication endpoint"""
    try:
        # Get auth type from g (set by api_token_required decorator)
        auth_type = getattr(
            g, "auth_type", "JWT"
        )  # Default to JWT for backward compatibility

        # Maintain old API contract
        return (
            jsonify(
                {
                    "message": "Authentication successful",
                    "user_id": g.current_user.id,
                    "email": g.current_user.email,
                    "auth_type": auth_type,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Error in auth test: {str(e)}")
        return jsonify(format_error_response("Authentication test failed")), 500


@auth_bp.route("/api/v1/auth/users", methods=["GET"])
@api_token_required
def get_all_users():
    """Get all users (admin function)"""
    try:
        # Check if user is admin
        requesting_user = g.current_user
        if not requesting_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403

        # Query all users
        users = AuthService.get_all_users()

        # Convert to list of dictionaries with additional admin info
        user_list = []
        for user in users:
            user_data = user.to_dict()
            user_data["is_admin"] = user.is_admin  # Include admin status
            user_list.append(user_data)

        return jsonify({"users": user_list}), 200

    except Exception as e:
        current_app.logger.error(f"Error getting all users: {str(e)}")
        return jsonify(format_error_response("Failed to get users")), 500


@auth_bp.route("/api/v1/auth/refresh", methods=["POST"])
@api_token_required
def refresh_token():
    """Refresh JWT token"""
    try:
        # Generate new token
        token = AuthService.generate_access_token(g.current_user)

        # Maintain old API contract
        return jsonify({"token": token}), 200

    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {str(e)}")
        return jsonify(format_error_response("Failed to refresh token")), 500


@auth_bp.route("/api/v1/auth/test-token-expiration", methods=["GET"])
def test_token_expiration():
    """Test endpoint for token expiration"""
    from datetime import datetime, timezone

    from flask_jwt_extended import get_jwt

    try:
        # This endpoint doesn't require authentication to test expiration
        current_time = datetime.now(timezone.utc)

        # Try to get JWT claims if present
        try:
            claims = get_jwt()
            exp_timestamp = claims.get("exp", 0)
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

            response_data = {
                "current_time": current_time.isoformat(),
                "token_expiry": exp_datetime.isoformat(),
                "is_expired": current_time > exp_datetime,
            }
        except Exception:
            response_data = {
                "current_time": current_time.isoformat(),
                "message": "No valid JWT token found",
            }

        return jsonify(format_api_response(response_data)), 200

    except Exception as e:
        current_app.logger.error(f"Error in token expiration test: {str(e)}")
        return jsonify(format_error_response("Token expiration test failed")), 500
