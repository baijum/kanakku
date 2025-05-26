"""Authentication service layer containing all business logic for user authentication and management."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

import requests
from flask import current_app, session
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models.book import Book
from ..models.other import ApiToken
from ..models.user import User
from ..shared.services import BaseService
from ..utils.email_utils import send_password_reset_email


class AuthService(BaseService):
    """Service class for authentication-related operations"""

    # Keep track of failed login attempts
    # Structure: {ip_address: {email: [timestamp, timestamp, ...]}}
    failed_attempts = {}

    # Keep track of password reset attempts
    # Structure: {email: [timestamp, timestamp, ...]}
    reset_attempts = {}

    @classmethod
    def cleanup_failed_attempts(cls):
        """Clean up old failed login attempts"""
        now = datetime.now()
        limit = now - timedelta(minutes=15)  # Remove attempts older than 15 minutes

        for ip in list(cls.failed_attempts.keys()):
            for email in list(cls.failed_attempts[ip].keys()):
                # Filter out old timestamps
                cls.failed_attempts[ip][email] = [
                    ts for ts in cls.failed_attempts[ip][email] if ts > limit
                ]

                # If no recent attempts remain, remove the email entry
                if not cls.failed_attempts[ip][email]:
                    del cls.failed_attempts[ip][email]

            # If no emails remain for this IP, remove the IP entry
            if not cls.failed_attempts[ip]:
                del cls.failed_attempts[ip]

    @staticmethod
    def verify_oauth_token(token: str) -> Dict:
        """
        Verify an OAuth token and return user information.
        For Google OAuth, this would normally call the Google API to verify the token.

        Args:
            token: The OAuth token to verify

        Returns:
            A dictionary containing user information from the verified token
        """
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

    @staticmethod
    def verify_hcaptcha(token: str, remote_ip: str) -> bool:
        """
        Verify an hCaptcha token with the hCaptcha API.

        Args:
            token: The hCaptcha response token from the frontend
            remote_ip: The IP address of the user

        Returns:
            bool: True if verification succeeds, False otherwise
        """
        # Skip verification in testing mode
        if current_app.config.get("TESTING", False):
            current_app.logger.info("Skipping hCaptcha verification in testing mode")
            return True

        # Get the secret key from environment
        secret_key = current_app.config.get("HCAPTCHA_SECRET_KEY")
        if not secret_key:
            current_app.logger.error("HCAPTCHA_SECRET_KEY not configured")
            return False

        # Prepare the verification request
        verification_url = "https://api.hcaptcha.com/siteverify"
        data = {
            "secret": secret_key,
            "response": token,
            "remoteip": remote_ip,
        }

        try:
            # Make the verification request
            response = requests.post(verification_url, data=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            success = result.get("success", False)

            if success:
                current_app.logger.info(
                    f"hCaptcha verification successful for IP: {remote_ip}"
                )
            else:
                error_codes = result.get("error-codes", [])
                current_app.logger.warning(
                    f"hCaptcha verification failed for IP: {remote_ip}, errors: {error_codes}"
                )

            return success

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error verifying hCaptcha token: {e}")
            return False
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error during hCaptcha verification: {e}"
            )
            return False

    @staticmethod
    def check_honeypot(data: Dict) -> bool:
        """
        Check honeypot fields to detect bots.

        Args:
            data: Request data dictionary

        Returns:
            bool: True if honeypot is triggered (likely bot), False otherwise
        """
        # Honeypot check - if website field is filled, it's likely a bot
        # Also check for the old username field for backward compatibility
        honeypot_website = data.get("website", "")
        honeypot_username = data.get("username", "")

        if honeypot_website or honeypot_username:
            honeypot_value = honeypot_website or honeypot_username
            field_name = "website" if honeypot_website else "username"
            current_app.logger.warning(
                f"Honeypot triggered for registration attempt with email: {data.get('email', 'unknown')} - {field_name} field filled: '{honeypot_value}'"
            )
            return True
        return False

    @staticmethod
    def create_user(
        email: str, password: str, name: str = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user account.

        Args:
            email: User's email address
            password: User's password
            name: User's name (optional)

        Returns:
            Tuple of (User object, error message). User is None if creation failed.
        """
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None, "User with this email already exists"

            # Create new user
            user = User(email=email, name=name)
            user.set_password(password)

            db.session.add(user)
            db.session.flush()  # Get user ID
            current_app.logger.info(f"New user created and flushed (ID: {user.id})")

            # Create default book for new user
            from ..models.book import Book

            default_book = Book(user_id=user.id, name="Book1")
            db.session.add(default_book)
            db.session.flush()  # Get book ID
            current_app.logger.info(
                f"Default book created and flushed (ID: {default_book.id}) for user {user.id}"
            )

            # Set active book ID
            user.active_book_id = default_book.id
            current_app.logger.info(
                f"Setting active_book_id to {default_book.id} for user {user.id}"
            )

            db.session.commit()
            current_app.logger.info(
                f"Committed transaction for user {user.email} (ID: {user.id})"
            )

            current_app.logger.info(f"New user registered: {email}")
            return user, None

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during user creation: {str(e)}")
            return None, "Failed to create user account"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error during user creation: {str(e)}")
            return None, "Failed to create user account"

    @classmethod
    def authenticate_user(
        cls, email: str, password: str, remote_ip: str
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email address
            password: User's password
            remote_ip: Client's IP address for rate limiting

        Returns:
            Tuple of (User object, error message). User is None if authentication failed.
        """
        try:
            # Clean up old failed attempts
            cls.cleanup_failed_attempts()

            # Check for too many failed attempts from this IP for this email
            if (
                remote_ip in cls.failed_attempts
                and email in cls.failed_attempts[remote_ip]
            ):
                recent_attempts = len(cls.failed_attempts[remote_ip][email])
                if recent_attempts >= 5:
                    current_app.logger.warning(
                        f"Too many failed login attempts for {email} from IP {remote_ip}"
                    )
                    return (
                        None,
                        "Too many failed login attempts. Please try again later.",
                    )

            # Find user by email
            user = User.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                # Record failed attempt
                if remote_ip not in cls.failed_attempts:
                    cls.failed_attempts[remote_ip] = {}
                if email not in cls.failed_attempts[remote_ip]:
                    cls.failed_attempts[remote_ip][email] = []

                cls.failed_attempts[remote_ip][email].append(datetime.now())

                current_app.logger.warning(
                    f"Failed login attempt for {email} from IP {remote_ip}"
                )
                return None, "Invalid email or password"

            # Check if user is active
            if not user.is_active:
                current_app.logger.warning(f"Login attempt for inactive user: {email}")
                return None, "Account is deactivated. Please contact support."

            # Clear any failed attempts for this user on successful login
            if (
                remote_ip in cls.failed_attempts
                and email in cls.failed_attempts[remote_ip]
            ):
                del cls.failed_attempts[remote_ip][email]
                if not cls.failed_attempts[remote_ip]:
                    del cls.failed_attempts[remote_ip]

            current_app.logger.info(f"Successful login for user: {email}")
            return user, None

        except Exception as e:
            current_app.logger.error(f"Error during authentication: {str(e)}")
            return None, "Authentication failed"

    @staticmethod
    def generate_access_token(user: User) -> str:
        """
        Generate JWT access token for user.

        Args:
            user: User object

        Returns:
            JWT access token string
        """
        return create_access_token(identity=str(user.id))

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's ID

        Returns:
            User object or None if not found
        """
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User's email address

        Returns:
            User object or None if not found
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_user_password(user: User, new_password: str) -> bool:
        """
        Update user's password.

        Args:
            user: User object
            new_password: New password

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user.set_password(new_password)
            db.session.commit()
            current_app.logger.info(f"Password updated for user: {user.email}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating password: {str(e)}")
            return False

    @classmethod
    def initiate_password_reset(
        cls, email: str, remote_ip: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Initiate password reset process.

        Args:
            email: User's email address
            remote_ip: Client's IP address for rate limiting

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Rate limiting for password reset attempts
            now = datetime.now()
            limit = now - timedelta(minutes=15)

            # Clean up old attempts
            if email in cls.reset_attempts:
                cls.reset_attempts[email] = [
                    ts for ts in cls.reset_attempts[email] if ts > limit
                ]

            # Check if too many attempts
            if email in cls.reset_attempts and len(cls.reset_attempts[email]) >= 3:
                current_app.logger.warning(
                    f"Too many password reset attempts for {email} from IP {remote_ip}"
                )
                return (
                    False,
                    "Too many password reset attempts. Please try again later.",
                )

            # Find user
            user = User.query.filter_by(email=email).first()
            if not user:
                # Don't reveal if email exists or not
                current_app.logger.info(
                    f"Password reset requested for non-existent email: {email}"
                )
                return True, None

            # Generate reset token
            reset_token = user.generate_reset_token()

            # Send reset email
            if send_password_reset_email(user, reset_token):
                # Record the attempt
                if email not in cls.reset_attempts:
                    cls.reset_attempts[email] = []
                cls.reset_attempts[email].append(now)

                current_app.logger.info(f"Password reset email sent to: {email}")
                return True, None
            else:
                current_app.logger.error(
                    f"Failed to send password reset email to: {email}"
                )
                return False, "Failed to send reset email"

        except Exception as e:
            current_app.logger.error(
                f"Error during password reset initiation: {str(e)}"
            )
            return False, "Failed to initiate password reset"

    @staticmethod
    def reset_password_with_token(
        token: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Reset password using reset token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Find user with this token
            user = User.query.filter_by(reset_token=token).first()
            if not user:
                current_app.logger.warning(
                    f"Password reset attempted with invalid token: {token}"
                )
                return False, "Invalid or expired reset token"

            # Verify token
            if not user.verify_reset_token(token):
                current_app.logger.warning(
                    f"Password reset attempted with expired token for user: {user.email}"
                )
                return False, "Invalid or expired reset token"

            # Update password
            user.set_password(new_password)
            user.clear_reset_token()

            current_app.logger.info(f"Password reset successful for user: {user.email}")
            return True, None

        except Exception as e:
            current_app.logger.error(f"Error during password reset: {str(e)}")
            return False, "Failed to reset password"

    @staticmethod
    def create_or_update_google_user(
        user_info: Dict,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Create or update user from Google OAuth information.

        Args:
            user_info: User information from Google OAuth

        Returns:
            Tuple of (User object, error_message)
        """
        try:
            google_id = user_info.get("sub")
            email = user_info.get("email")
            name = user_info.get("name")
            picture = user_info.get("picture")

            if not google_id or not email:
                return None, "Invalid Google user information"

            # Check if user exists by Google ID
            user = User.query.filter_by(google_id=google_id).first()

            if user:
                # Update existing user info
                user.name = name
                user.picture = picture
                db.session.commit()
                current_app.logger.info(f"Updated existing Google user: {email}")
                return user, None

            # Check if user exists by email
            user = User.query.filter_by(email=email).first()

            if user:
                # Link existing account to Google
                user.google_id = google_id
                user.picture = picture
                if name and not user.name:
                    user.name = name
                db.session.commit()
                current_app.logger.info(f"Linked existing user to Google: {email}")
                return user, None

            # Create new user
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                picture=picture,
                is_active=True,  # Auto-activate Google users
            )

            db.session.add(user)
            db.session.flush()  # Get user ID
            current_app.logger.info(
                f"Google OAuth: New user created and flushed (ID: {user.id})"
            )

            # Create default book for new user
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

            db.session.commit()
            current_app.logger.info(
                f"Google OAuth: Committed transaction for user {user.email} (ID: {user.id})"
            )

            return user, None

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error during Google user creation: {str(e)}"
            )
            return None, "Failed to create or update user"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during Google user creation: {str(e)}")
            return None, "Failed to create or update user"

    # Google OAuth Methods

    @staticmethod
    def generate_google_auth_url() -> (
        Tuple[Optional[str], Optional[str], Optional[str]]
    ):
        """
        Generate Google OAuth authorization URL.

        Returns:
            Tuple of (auth_url, state, error_message)
        """
        try:
            google_client_id = current_app.config.get("GOOGLE_CLIENT_ID")
            if not google_client_id:
                return None, None, "Google OAuth is not configured"

            # Generate a random state and store it in session
            state = secrets.token_urlsafe(16)
            session["oauth_state"] = state

            current_app.logger.debug(
                f"Generated OAuth state and stored in session: {state}"
            )

            # Use the backend URL for the callback
            backend_url = current_app.config.get("BACKEND_URL", "http://localhost:5000")
            redirect_uri = backend_url.rstrip("/") + "/api/v1/auth/google/callback"

            current_app.logger.debug(f"Google login using redirect URI: {redirect_uri}")

            params = {
                "client_id": google_client_id,
                "redirect_uri": redirect_uri,
                "scope": "openid email profile",
                "state": state,
                "response_type": "code",
                "prompt": "select_account",
            }

            auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(
                params
            )
            return auth_url, state, None

        except Exception as e:
            current_app.logger.error(f"Error generating Google auth URL: {str(e)}")
            return None, None, "Failed to generate authorization URL"

    @staticmethod
    def handle_google_callback(
        code: str, state: str
    ) -> Tuple[Optional[User], Optional[str], Optional[str]]:
        """
        Handle Google OAuth callback.

        Args:
            code: Authorization code from Google
            state: State parameter for validation

        Returns:
            Tuple of (User object, redirect_url, error_message)
        """
        try:
            # Validate state parameter
            stored_state = session.pop("oauth_state", None)
            if not state or state != stored_state:
                current_app.logger.error(
                    f"Invalid OAuth state. Received: {state}, Expected: {stored_state}"
                )
                return None, None, "Invalid OAuth state parameter"

            if not code:
                current_app.logger.error("Authorization code not provided")
                return None, None, "Authorization code not provided"

            # Exchange code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            backend_url = current_app.config.get("BACKEND_URL", "http://localhost:5000")
            redirect_uri = backend_url.rstrip("/") + "/api/v1/auth/google/callback"

            current_app.logger.debug(f"Google callback redirect_uri: {redirect_uri}")

            token_data = {
                "code": code,
                "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
                "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }

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

            # Create or update user
            user, error = AuthService.create_or_update_google_user(userinfo)
            if error:
                return None, None, error

            # Check if user is active
            if not user.is_active:
                current_app.logger.warning(
                    f"Google OAuth: Inactive user attempted login: {user.email}"
                )
                frontend_url = current_app.config.get(
                    "FRONTEND_URL", "http://localhost:3000"
                )
                redirect_url = f"{frontend_url}/login?error=account_inactive"
                return None, redirect_url, "Account is inactive"

            # Generate JWT token
            token = create_access_token(identity=str(user.id))
            current_app.logger.debug(f"JWT token created for user: {user.email}")

            # Return token in query parameters for the frontend to consume
            frontend_url = current_app.config.get(
                "FRONTEND_URL", "http://localhost:3000"
            )
            redirect_url = f"{frontend_url}/google-auth-callback?token={token}"
            current_app.logger.debug(f"Redirecting to: {redirect_url}")

            return user, redirect_url, None

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error in Google OAuth: {str(e)}")
            return None, None, "Failed to authenticate with Google"
        except Exception as e:
            current_app.logger.error(f"Unexpected error in Google callback: {str(e)}")
            return None, None, "Internal server error during Google authentication"

    @staticmethod
    def toggle_user_status(user: User) -> bool:
        """
        Toggle user's active status.

        Args:
            user: User object

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user.is_active = not user.is_active
            db.session.commit()
            status = "activated" if user.is_active else "deactivated"
            current_app.logger.info(f"User {status}: {user.email}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error toggling user status: {str(e)}")
            return False

    @staticmethod
    def activate_user_by_id(
        user_id: int, admin_user: User
    ) -> Tuple[bool, Optional[str]]:
        """
        Activate user by ID (admin function).

        Args:
            user_id: ID of user to activate
            admin_user: Admin user performing the action

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # TODO: Add proper admin role checking
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            user.activate()
            current_app.logger.info(
                f"User activated by admin {admin_user.email}: {user.email}"
            )
            return True, None

        except Exception as e:
            current_app.logger.error(f"Error activating user: {str(e)}")
            return False, "Failed to activate user"

    @staticmethod
    def get_all_users() -> list[User]:
        """
        Get all users (admin function).

        Returns:
            List of all users
        """
        return User.query.all()

    # API Token Management Methods

    @staticmethod
    def get_user_tokens(user: User) -> list[ApiToken]:
        """
        Get all API tokens for a user.

        Args:
            user: User object

        Returns:
            List of user's API tokens
        """
        return ApiToken.query.filter_by(user_id=user.id).all()

    @staticmethod
    def create_api_token(
        user: User, name: str, description: str = None, expires_at=None
    ) -> Tuple[Optional[ApiToken], Optional[str]]:
        """
        Create a new API token for user.

        Args:
            user: User object
            name: Token name
            description: Token description (optional) - currently not stored in model
            expires_at: Token expiration datetime (optional)

        Returns:
            Tuple of (ApiToken object, error_message)
        """
        try:
            # Check if token name already exists for this user
            existing_token = ApiToken.query.filter_by(
                user_id=user.id, name=name
            ).first()
            if existing_token:
                return None, "Token with this name already exists"

            # Create new token (description not supported by current model)
            token = ApiToken(
                user_id=user.id,
                token=ApiToken.generate_token(),
                name=name,
                expires_at=expires_at,
            )

            db.session.add(token)
            db.session.commit()

            current_app.logger.info(f"API token created for user {user.email}: {name}")
            return token, None

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating API token: {str(e)}")
            return None, "Failed to create API token"

    @staticmethod
    def get_api_token_by_id(token_id: int, user: User) -> Optional[ApiToken]:
        """
        Get API token by ID for a specific user.

        Args:
            token_id: Token ID
            user: User object

        Returns:
            ApiToken object or None if not found
        """
        return ApiToken.query.filter_by(id=token_id, user_id=user.id).first()

    @staticmethod
    def update_api_token(
        token: ApiToken,
        name: str = None,
        description: str = None,
        expires_at=...,
        is_active: bool = None,
    ) -> bool:
        """
        Update API token.

        Args:
            token: ApiToken object
            name: New name (optional)
            description: New description (optional) - currently not stored in model
            expires_at: New expiration datetime (optional)
            is_active: New active status (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if name is not None:
                # Check if new name conflicts with existing tokens for this user
                existing_token = (
                    ApiToken.query.filter_by(user_id=token.user_id, name=name)
                    .filter(ApiToken.id != token.id)
                    .first()
                )

                if existing_token:
                    return False

                token.name = name

            # Note: description field is not supported by current model
            # if description is not None:
            #     token.description = description

            if expires_at is not ...:
                token.expires_at = expires_at

            if is_active is not None:
                token.is_active = is_active

            db.session.commit()
            current_app.logger.info(f"API token updated: {token.name}")
            return True

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating API token: {str(e)}")
            return False

    @staticmethod
    def revoke_api_token(token: ApiToken) -> bool:
        """
        Revoke (delete) an API token.

        Args:
            token: ApiToken object

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db.session.delete(token)
            db.session.commit()
            current_app.logger.info(f"API token revoked: {token.name}")
            return True

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error revoking API token: {str(e)}")
            return False

    @staticmethod
    def get_api_token_by_value(token_value: str) -> Optional[ApiToken]:
        """
        Get API token by token value.

        Args:
            token_value: Token string value

        Returns:
            ApiToken object or None if not found
        """
        return ApiToken.query.filter_by(token=token_value).first()
