from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
    Response,
    url_for,
    redirect,
    g,
    session,
)
from flask_jwt_extended import (
    create_access_token,
    current_user as flask_jwt_current_user,
)
from app.models import User, db
from app.utils.email_utils import send_password_reset_email
from app.extensions import (
    api_token_required,
    auth_rate_limit,
    limiter,
    csrf_exempt,
)
import requests
import secrets
from datetime import datetime, timedelta

auth = Blueprint("auth", __name__)

# Keep track of failed login attempts
# Structure: {ip_address: {email: [timestamp, timestamp, ...]}}
failed_attempts = {}

# Keep track of password reset attempts
# Structure: {email: [timestamp, timestamp, ...]}
reset_attempts = {}


# Helper function to clean up old failed attempts
def cleanup_failed_attempts():
    now = datetime.now()
    limit = now - timedelta(minutes=15)  # Remove attempts older than 15 minutes

    for ip in list(failed_attempts.keys()):
        for email in list(failed_attempts[ip].keys()):
            # Filter out old timestamps
            failed_attempts[ip][email] = [
                ts for ts in failed_attempts[ip][email] if ts > limit
            ]

            # If no recent attempts remain, remove the email entry
            if not failed_attempts[ip][email]:
                del failed_attempts[ip][email]

        # If no emails remain for this IP, remove the IP entry
        if not failed_attempts[ip]:
            del failed_attempts[ip]


def verify_oauth_token(token):
    """
    Verify an OAuth token and return user information.
    For Google OAuth, this would normally call the Google API to verify the token.

    Args:
        token: The OAuth token to verify

    Returns:
        A dictionary containing user information from the verified token
    """
    # In a real implementation, this would verify the token with Google's API
    try:
        # Only make a real request if not in testing mode
        if not current_app.config.get("TESTING", False):
            # Make request to Google's tokeninfo endpoint
            response = requests.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.json()
        else:
            # For testing, return mock data
            return {
                "sub": "12345",
                "email": "googleuser@example.com",
                "name": "Google User",
                "picture": "https://example.com/photo.jpg",
            }
    except Exception as e:
        current_app.logger.error(f"Error verifying OAuth token: {e}")
        raise ValueError("Invalid OAuth token")


@auth.route("/api/v1/auth/register", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def register():
    """Register endpoint - explicitly exempt from CSRF protection"""
    current_app.logger.info(
        "Register endpoint called - CSRF protection disabled for this endpoint"
    )

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    try:
        # Create new user
        user = User(
            email=data["email"],
            is_active=True,  # Assuming auto-activation for now
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()  # Assigns user.id within the transaction
        current_app.logger.info(
            f"User object created for {user.email}, flushed (ID: {user.id})"
        )

        # Create a default book for the user
        from app.models import Book

        default_book = Book(user_id=user.id, name="Book1")
        db.session.add(default_book)
        db.session.flush()  # Assigns default_book.id within the transaction
        current_app.logger.info(
            f"Default book created for user {user.id}, flushed (Book ID: {default_book.id})"
        )

        # Set the default book as active
        user.active_book_id = default_book.id
        current_app.logger.info(
            f"Setting active_book_id to {default_book.id} for user {user.id}"
        )

        # Commit all changes at once
        db.session.commit()
        current_app.logger.info(f"Committed transaction for user {user.id}")

        # Get the committed user ID for the response
        user_id = user.id

        return (
            jsonify(
                {
                    "message": "User and default book created successfully.",  # Updated message
                    "user_id": user_id,
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error during registration for {data.get('email')}: {str(e)}",
            exc_info=True,
        )
        return (
            jsonify({"error": "An internal error occurred during registration."}),
            500,
        )


# Add OPTIONS handler for CORS preflight requests
@auth.route("/api/v1/auth/login", methods=["OPTIONS"])
@csrf_exempt
def login_options():
    response = Response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept, Authorization, X-CSRFToken",
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


@auth.route("/api/v1/auth/login", methods=["POST"])
@auth_rate_limit
@csrf_exempt
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

    # Get client IP address
    ip_address = request.remote_addr

    # Check if this IP + email combo has too many failed attempts
    if ip_address in failed_attempts and email in failed_attempts[ip_address]:
        # Apply stricter rate limiting if there are 3+ recent failures
        recent_failures = failed_attempts[ip_address][email]
        if len(recent_failures) >= 3:
            current_app.logger.warning(
                f"Multiple failed login attempts for email {email} from IP {ip_address}"
            )
            # Use the failed_login_limit decorator logic manually
            remaining = limiter.limiter.get_window_stats(
                "3 per minute", request.remote_addr
            )[1]

            if remaining <= 0:
                cleanup_failed_attempts()  # Clean up old attempts
                return (
                    jsonify(
                        {"error": "Too many login attempts. Please try again later."}
                    ),
                    429,
                )

    # Find the user
    user = User.query.filter_by(email=email).first()

    # Check password
    if user and user.check_password(password):
        # Success - reset failed attempts for this IP + email
        if ip_address in failed_attempts and email in failed_attempts[ip_address]:
            del failed_attempts[ip_address][email]
            if not failed_attempts[ip_address]:
                del failed_attempts[ip_address]

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
            # Ensure identity is string
            token = create_access_token(identity=str(user.id))

            # Get user data for response
            user_data = user.to_dict()

            # Ensure the user has an active book
            if not user.active_book_id:
                from app.models import Book

                # Find any book or create one
                book = Book.query.filter_by(user_id=user.id).first()
                if book:
                    user.active_book_id = book.id
                    db.session.commit()
                    user_data = user.to_dict()  # Refresh with updated data

            return jsonify({"token": token, "user": user_data}), 200
        except Exception as e:
            current_app.logger.error(
                f"Error during token generation for user {email}: {str(e)}",
                exc_info=True,
            )
            return jsonify({"error": "An error occurred during login"}), 500
    else:
        # Failed login - record the attempt
        now = datetime.now()

        if ip_address not in failed_attempts:
            failed_attempts[ip_address] = {}

        if email not in failed_attempts[ip_address]:
            failed_attempts[ip_address][email] = []

        failed_attempts[ip_address][email].append(now)

        # Clean up old attempts periodically
        if len(failed_attempts) > 100:  # Arbitrary threshold to avoid memory issues
            cleanup_failed_attempts()

        # Log the failed attempt
        current_app.logger.warning(
            f"Failed login attempt for email {email} from IP {ip_address}"
        )

        return jsonify({"error": "Invalid email or password"}), 401


@auth.route("/api/v1/auth/logout", methods=["POST"])
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


@auth.route("/api/v1/auth/me", methods=["GET"])
@api_token_required
def get_current_user():
    # Access the user loaded by the decorator via g.current_user
    user = g.current_user
    if not user:
        # This case should not happen if decorator works correctly
        return jsonify({"error": "User not found"}), 404
    # Explicitly convert user object to dict before jsonify
    return jsonify(user.to_dict()), 200


@auth.route("/api/v1/auth/profile", methods=["GET"])
@api_token_required
def get_user_profile():
    """Get the current user's profile including active book."""
    # Access the user loaded by the decorator via g.current_user
    user = g.current_user
    if not user:
        # This case should not happen if decorator works correctly
        return jsonify({"error": "User not found"}), 404

    # Create profile data
    profile = user.to_dict()

    # Ensure active_book_id is included
    if not profile.get("active_book_id") and user.active_book_id:
        profile["active_book_id"] = user.active_book_id

    # If we don't have an active book yet, set one
    if not user.active_book_id:
        from app.models import Book

        # Find any book or create one
        book = Book.query.filter_by(user_id=user.id).first()
        if book:
            user.active_book_id = book.id
            db.session.commit()
            profile["active_book_id"] = book.id

    return jsonify(profile), 200


@auth.route("/api/v1/auth/users/<int:user_id>/activate", methods=["POST"])
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


@auth.route("/api/v1/auth/password", methods=["PUT"])
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


@auth.route("/api/v1/auth/forgot-password", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def forgot_password():
    """Request a password reset"""
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"]

    # Check for repeated password reset attempts
    if email in reset_attempts:
        # Apply stricter rate limiting if there are many recent reset attempts
        now = datetime.now()
        recent_resets = [
            ts for ts in reset_attempts[email] if (now - ts).total_seconds() < 3600
        ]  # Last hour

        if len(recent_resets) >= 3:
            current_app.logger.warning(
                f"Multiple password reset attempts for email {email}"
            )
            return (
                jsonify(
                    {
                        "error": "Too many password reset attempts. Please try again later."
                    }
                ),
                429,
            )

        # Update the attempts list
        reset_attempts[email] = recent_resets + [now]
    else:
        reset_attempts[email] = [datetime.now()]

    # Find the user
    user = User.query.filter_by(email=email).first()

    # Whether we find a user or not, don't reveal this information
    if user:
        try:
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires_at = datetime.now() + timedelta(hours=1)
            db.session.commit()

            # Send password reset email
            send_password_reset_email(user, reset_token)
            current_app.logger.info(f"Password reset token generated for user {email}")
        except Exception as e:
            current_app.logger.error(
                f"Error generating reset token for {email}: {str(e)}", exc_info=True
            )
            # Still return success to avoid leaking information

    # Always return success to prevent email enumeration
    return (
        jsonify(
            {
                "message": "If an account exists with this email, a password reset link has been sent."
            }
        ),
        200,
    )


@auth.route("/api/v1/auth/reset-password", methods=["POST"])
@auth_rate_limit
@csrf_exempt
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    # Get client IP address for rate limiting
    ip_address = request.remote_addr

    # Apply stricter rate limiting based on IP to prevent brute force attacks
    now = datetime.now()
    if ip_address in failed_attempts and "reset_token" in failed_attempts[ip_address]:
        # Check for excessive attempts
        recent_failures = [
            ts
            for ts in failed_attempts[ip_address]["reset_token"]
            if (now - ts).total_seconds() < 900
        ]  # Last 15 minutes

        if len(recent_failures) >= 5:
            current_app.logger.warning(
                f"Multiple failed password reset attempts from IP {ip_address}"
            )
            return jsonify({"error": "Too many attempts. Please try again later."}), 429

    # Find user by reset token
    user = User.query.filter(
        User.reset_token == token, User.reset_token_expires_at > datetime.now()
    ).first()

    if not user:
        # Record the failed attempt
        if ip_address not in failed_attempts:
            failed_attempts[ip_address] = {}

        if "reset_token" not in failed_attempts[ip_address]:
            failed_attempts[ip_address]["reset_token"] = []

        failed_attempts[ip_address]["reset_token"].append(now)

        current_app.logger.warning(
            f"Invalid or expired reset token attempt from IP {ip_address}"
        )
        return jsonify({"error": "Invalid or expired token"}), 400

    try:
        # Update password
        user.set_password(new_password)

        # Clear reset token
        user.reset_token = None
        user.reset_token_expires_at = None

        # Commit changes
        db.session.commit()

        # Clear any failed reset attempts from this IP
        if (
            ip_address in failed_attempts
            and "reset_token" in failed_attempts[ip_address]
        ):
            del failed_attempts[ip_address]["reset_token"]
            if not failed_attempts[ip_address]:
                del failed_attempts[ip_address]

        current_app.logger.info(f"Password reset successful for user {user.email}")

        return jsonify({"message": "Password has been reset successfully"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error during password reset: {str(e)}", exc_info=True
        )
        return jsonify({"error": "Failed to reset password"}), 500


# Google OAuth2 route
@auth.route("/api/v1/auth/google", methods=["GET"])
@csrf_exempt
def google_login():
    # Get Google OAuth2 configuration
    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    if not google_client_id:
        return jsonify({"error": "Google OAuth is not configured"}), 500

    # Generate a random state and store it in session
    state = secrets.token_urlsafe(16)

    # Store state in session for validation
    session["oauth_state"] = state

    # Log the state for debugging
    current_app.logger.debug(f"Generated OAuth state and stored in session: {state}")

    # Use the backend URL for the callback
    backend_url = current_app.config.get("BACKEND_URL", request.url_root)
    redirect_uri = backend_url.rstrip("/") + url_for("auth.google_callback")

    current_app.logger.debug(f"Google login using redirect URI: {redirect_uri}")

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


@auth.route("/api/v1/auth/google/callback", methods=["GET"])
@csrf_exempt
def google_callback():
    try:
        # Add request logging
        current_app.logger.info(f"Google auth callback received. URL: {request.url}")
        current_app.logger.debug(f"Google auth callback query params: {request.args}")

        # Validate state parameter
        state = request.args.get("state")
        stored_state = session.pop("oauth_state", None)

        if not state or state != stored_state:
            current_app.logger.error(
                f"Invalid OAuth state. Received: {state}, Expected: {stored_state}"
            )
            return jsonify({"error": "Invalid OAuth state parameter"}), 400

        # Get authorization code
        code = request.args.get("code")
        if not code:
            current_app.logger.error("Authorization code not provided")
            return jsonify({"error": "Authorization code not provided"}), 400

        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        backend_url = current_app.config.get("BACKEND_URL", request.url_root)
        redirect_uri = backend_url.rstrip("/") + url_for("auth.google_callback")
        current_app.logger.debug(f"Google callback redirect_uri: {redirect_uri}")

        token_data = {
            "code": code,
            "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
            "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            current_app.logger.debug("Exchanging code for token with Google")
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            current_app.logger.debug("Successfully received token from Google")

            # Get user info using the access token
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_response = requests.get(
                userinfo_url,
                headers={"Authorization": f'Bearer {tokens["access_token"]}'},
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
            current_app.logger.debug(f"User info received: {userinfo.get('email')}")

            # Check if user exists
            user = User.query.filter_by(google_id=userinfo["sub"]).first()

            if not user:
                # Check if email exists
                user = User.query.filter_by(email=userinfo["email"]).first()
                if user:
                    # Update existing user with Google ID
                    current_app.logger.debug(
                        f"Updating existing user with Google ID: {user.email}"
                    )
                    user.google_id = userinfo["sub"]
                    user.picture = userinfo.get("picture")
                else:
                    # Create new user
                    current_app.logger.debug(
                        f"Creating new user from Google auth: {userinfo['email']}"
                    )
                    user = User(
                        email=userinfo["email"],
                        google_id=userinfo["sub"],
                        picture=userinfo.get("picture"),
                        is_active=True,  # Auto-activate Google users
                    )
                    db.session.add(user)
                    db.session.flush()  # Get user ID
                    current_app.logger.info(
                        f"Google OAuth: New user created and flushed (ID: {user.id})"
                    )

                    # --- Add Default Book Creation ---
                    from app.models import Book

                    default_book = Book(user_id=user.id, name="Book1")
                    db.session.add(default_book)
                    db.session.flush()  # Get book ID
                    current_app.logger.info(
                        f"Google OAuth: Default book created and flushed (ID: {default_book.id}) for user {user.id}"
                    )

                    # Set active book ID
                    user.active_book_id = default_book.id
                    current_app.logger.info(
                        f"Google OAuth: Setting active_book_id to {default_book.id} for user {user.id}"
                    )
                    # --- End Default Book Creation ---

                # Commit user creation/update and potentially book creation
                db.session.commit()
                current_app.logger.info(
                    f"Google OAuth: Committed transaction for user {user.email} (ID: {user.id})"
                )

            # Generate JWT token (Use user ID as identity, standard practice)
            token = create_access_token(identity=str(user.id))
            current_app.logger.debug(f"JWT token created for user: {user.email}")
            current_app.logger.debug(f"JWT token length: {len(token)}")

            # Return token in query parameters for the frontend to consume
            frontend_url = current_app.config.get(
                "FRONTEND_URL", "http://localhost:3000"
            )
            redirect_url = f"{frontend_url}/google-auth-callback?token={token}"
            current_app.logger.debug(f"Redirecting to: {redirect_url}")

            return redirect(redirect_url)

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error in Google OAuth: {str(e)}")
            return jsonify({"error": "Failed to authenticate with Google"}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in Google callback: {str(e)}")
        import traceback

        current_app.logger.error(traceback.format_exc())
        return (
            jsonify({"error": "Internal server error during Google authentication"}),
            500,
        )


@auth.route("/api/v1/auth/google", methods=["POST"])
@csrf_exempt
def google_token_auth():
    """Handle Google authentication with a token directly from the frontend."""
    # Get token from request
    data = request.get_json()
    if not data or "token" not in data:
        return jsonify({"error": "No token provided"}), 400

    try:
        # Verify the token
        userinfo = verify_oauth_token(data["token"])

        # Check if user exists by Google ID
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

            # Create a default book for the user if they don't have one
            from app.models import Book

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                default_book = Book(user_id=user.id, name="Book1")
                db.session.add(default_book)
                db.session.commit()

                # Set the default book as active
                user.active_book_id = default_book.id
                db.session.commit()

        # Generate JWT token
        # Ensure identity is string
        token = create_access_token(identity=str(user.id))

        # Return user info and token
        return (
            jsonify(
                {"message": "Login successful", "token": token, "user": user.to_dict()}
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error in Google token auth: {str(e)}")
        return jsonify({"error": "Failed to authenticate with Google"}), 500


# API Token Management Endpoints
@auth.route("/api/v1/auth/tokens", methods=["GET"])
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
    # Return tokens without including the token value for security
    return (
        jsonify(
            [
                {k: v for k, v in token.to_dict().items() if k != "token"}
                for token in tokens
            ]
        ),
        200,
    )


@auth.route("/api/v1/auth/tokens", methods=["POST"])
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


@auth.route("/api/v1/auth/tokens/<int:token_id>", methods=["DELETE"])
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


@auth.route("/api/v1/auth/tokens/<int:token_id>", methods=["PUT"])
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
@auth.route("/api/v1/auth/test", methods=["GET"])
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
