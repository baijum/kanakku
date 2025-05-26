"""
Unified authentication and user management service.

Consolidates authentication logic from backend and provides consistent
interface for user management across modules.
"""

from typing import Dict
from datetime import datetime, timezone

from .base import (
    BaseService,
    StatelessService,
    ServiceResult,
    require_user_context,
    log_service_call,
)


class AuthService(StatelessService):
    """Unified service for authentication and user management."""

    @log_service_call("authenticate_user")
    def authenticate_user(
        self, email: str, password: str, remote_ip: str = None
    ) -> ServiceResult:
        """
        Authenticate a user with email and password.
        Consolidates logic from backend/app/auth_bp/services.py
        """
        try:
            from shared.imports import User
            from ..database import get_database_session

            with get_database_session() as session:
                user = session.query(User).filter_by(email=email).first()

                if not user:
                    return ServiceResult.error_result(
                        "Invalid email or password", error_code="AUTHENTICATION_FAILED"
                    )

                if not user.check_password(password):
                    return ServiceResult.error_result(
                        "Invalid email or password", error_code="AUTHENTICATION_FAILED"
                    )

                if not user.is_active:
                    return ServiceResult.error_result(
                        "Account is not active", error_code="ACCOUNT_INACTIVE"
                    )

                # Update last login
                user.last_login = datetime.now(timezone.utc)
                session.commit()

                return ServiceResult.success_result(
                    data={
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "is_active": user.is_active,
                        "last_login": (
                            user.last_login.isoformat() if user.last_login else None
                        ),
                    },
                    metadata={"authentication_method": "password"},
                )

        except Exception as e:
            self.logger.error(f"Authentication failed for {email}: {e}")
            return ServiceResult.error_result(
                "Authentication failed", error_code="AUTHENTICATION_ERROR"
            )

    @log_service_call("create_user")
    def create_user(self, email: str, password: str, name: str = None) -> ServiceResult:
        """Create a new user account."""
        try:
            from shared.imports import User, Book
            from ..database import database_session

            with database_session() as session:
                # Check if user already exists
                existing_user = session.query(User).filter_by(email=email).first()
                if existing_user:
                    return ServiceResult.error_result(
                        "User with this email already exists", error_code="USER_EXISTS"
                    )

                # Create new user
                user = User(email=email, name=name)
                user.set_password(password)

                session.add(user)
                session.flush()  # Get user ID

                # Create default book for new user
                default_book = Book(user_id=user.id, name="Book 1")
                session.add(default_book)
                session.flush()

                # Set active book
                user.active_book_id = default_book.id

                return ServiceResult.success_result(
                    data={
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "is_active": user.is_active,
                        "default_book_id": default_book.id,
                    },
                    metadata={"operation": "created"},
                )

        except Exception as e:
            self.logger.error(f"Failed to create user {email}: {e}")
            return ServiceResult.error_result(
                f"Failed to create user: {str(e)}", error_code="USER_CREATE_FAILED"
            )

    @log_service_call("get_user_by_id")
    def get_user_by_id(self, user_id: int) -> ServiceResult:
        """Get user by ID."""
        try:
            from shared.imports import User
            from ..database import get_database_session

            with get_database_session() as session:
                user = session.query(User).filter_by(id=user_id).first()

                if not user:
                    return ServiceResult.error_result(
                        "User not found", error_code="USER_NOT_FOUND"
                    )

                return ServiceResult.success_result(
                    data={
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "is_active": user.is_active,
                        "created_at": (
                            user.created_at.isoformat() if user.created_at else None
                        ),
                        "last_login": (
                            user.last_login.isoformat() if user.last_login else None
                        ),
                        "active_book_id": user.active_book_id,
                    }
                )

        except Exception as e:
            self.logger.error(f"Failed to get user {user_id}: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve user", error_code="USER_RETRIEVAL_FAILED"
            )

    @log_service_call("get_user_by_email")
    def get_user_by_email(self, email: str) -> ServiceResult:
        """Get user by email."""
        try:
            from shared.imports import User
            from ..database import get_database_session

            with get_database_session() as session:
                user = session.query(User).filter_by(email=email).first()

                if not user:
                    return ServiceResult.error_result(
                        "User not found", error_code="USER_NOT_FOUND"
                    )

                return ServiceResult.success_result(
                    data={
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "is_active": user.is_active,
                        "created_at": (
                            user.created_at.isoformat() if user.created_at else None
                        ),
                        "last_login": (
                            user.last_login.isoformat() if user.last_login else None
                        ),
                        "active_book_id": user.active_book_id,
                    }
                )

        except Exception as e:
            self.logger.error(f"Failed to get user by email {email}: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve user", error_code="USER_RETRIEVAL_FAILED"
            )

    @log_service_call("update_user_password")
    def update_user_password(self, user_id: int, new_password: str) -> ServiceResult:
        """Update user password."""
        try:
            from shared.imports import User
            from ..database import database_session

            with database_session() as session:
                user = session.query(User).filter_by(id=user_id).first()

                if not user:
                    return ServiceResult.error_result(
                        "User not found", error_code="USER_NOT_FOUND"
                    )

                user.set_password(new_password)
                user.updated_at = datetime.now(timezone.utc)

                return ServiceResult.success_result(
                    data={"password_updated": True}, metadata={"user_id": user_id}
                )

        except Exception as e:
            self.logger.error(f"Failed to update password for user {user_id}: {e}")
            return ServiceResult.error_result(
                "Failed to update password", error_code="PASSWORD_UPDATE_FAILED"
            )

    @log_service_call("generate_access_token")
    def generate_access_token(self, user_id: int) -> ServiceResult:
        """Generate JWT access token for user."""
        try:
            # This would typically use Flask-JWT-Extended in Flask context
            # For now, return a placeholder that can be implemented based on context
            return ServiceResult.success_result(
                data={"access_token": f"token_for_user_{user_id}"},
                metadata={"token_type": "jwt", "user_id": user_id},
            )

        except Exception as e:
            self.logger.error(f"Failed to generate token for user {user_id}: {e}")
            return ServiceResult.error_result(
                "Failed to generate access token", error_code="TOKEN_GENERATION_FAILED"
            )


class UserManagementService(BaseService):
    """Service for user management operations that require user context."""

    @require_user_context
    @log_service_call("update_profile")
    def update_profile(self, profile_data: Dict) -> ServiceResult:
        """Update user profile information."""
        try:
            from shared.imports import User

            user = self.session.query(User).filter_by(id=self.user_id).first()

            if not user:
                return ServiceResult.error_result(
                    "User not found", error_code="USER_NOT_FOUND"
                )

            # Update allowed fields
            updatable_fields = ["name", "email"]
            updated_fields = []

            for field in updatable_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
                    updated_fields.append(field)

            if updated_fields:
                user.updated_at = datetime.now(timezone.utc)
                self.session.commit()

            return ServiceResult.success_result(
                data={
                    "user_id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "updated_fields": updated_fields,
                },
                metadata={"operation": "profile_updated"},
            )

        except Exception as e:
            self.logger.error(f"Failed to update profile for user {self.user_id}: {e}")
            return ServiceResult.error_result(
                "Failed to update profile", error_code="PROFILE_UPDATE_FAILED"
            )

    @require_user_context
    @log_service_call("get_user_tokens")
    def get_user_tokens(self) -> ServiceResult:
        """Get API tokens for the current user."""
        try:
            from shared.imports import ApiToken

            tokens = (
                self.session.query(ApiToken)
                .filter_by(user_id=self.user_id, is_active=True)
                .all()
            )

            token_list = []
            for token in tokens:
                token_data = {
                    "id": token.id,
                    "name": token.name,
                    "description": token.description,
                    "created_at": (
                        token.created_at.isoformat() if token.created_at else None
                    ),
                    "expires_at": (
                        token.expires_at.isoformat() if token.expires_at else None
                    ),
                    "last_used_at": (
                        token.last_used_at.isoformat() if token.last_used_at else None
                    ),
                    "is_active": token.is_active,
                }
                # Don't include the actual token value for security
                token_list.append(token_data)

            return ServiceResult.success_result(
                data=token_list, metadata={"token_count": len(token_list)}
            )

        except Exception as e:
            self.logger.error(f"Failed to get tokens for user {self.user_id}: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve API tokens", error_code="TOKEN_RETRIEVAL_FAILED"
            )

    @require_user_context
    @log_service_call("create_api_token")
    def create_api_token(
        self, name: str, description: str = None, expires_at=None
    ) -> ServiceResult:
        """Create a new API token for the current user."""
        try:
            from shared.imports import ApiToken
            import secrets

            # Generate secure token
            token_value = secrets.token_urlsafe(32)

            api_token = ApiToken(
                user_id=self.user_id,
                name=name,
                description=description,
                token=token_value,
                expires_at=expires_at,
                is_active=True,
            )

            self.session.add(api_token)
            self.session.flush()

            return ServiceResult.success_result(
                data={
                    "token_id": api_token.id,
                    "name": api_token.name,
                    "token": token_value,  # Only return on creation
                    "description": api_token.description,
                    "expires_at": (
                        api_token.expires_at.isoformat()
                        if api_token.expires_at
                        else None
                    ),
                    "created_at": (
                        api_token.created_at.isoformat()
                        if api_token.created_at
                        else None
                    ),
                },
                metadata={"operation": "token_created"},
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create API token for user {self.user_id}: {e}"
            )
            return ServiceResult.error_result(
                "Failed to create API token", error_code="TOKEN_CREATE_FAILED"
            )

    @require_user_context
    @log_service_call("revoke_api_token")
    def revoke_api_token(self, token_id: int) -> ServiceResult:
        """Revoke an API token."""
        try:
            from shared.imports import ApiToken

            token = (
                self.session.query(ApiToken)
                .filter_by(id=token_id, user_id=self.user_id)
                .first()
            )

            if not token:
                return ServiceResult.error_result(
                    "API token not found", error_code="TOKEN_NOT_FOUND"
                )

            token.is_active = False
            token.updated_at = datetime.now(timezone.utc)
            self.session.commit()

            return ServiceResult.success_result(
                data={"token_revoked": True}, metadata={"token_id": token_id}
            )

        except Exception as e:
            self.logger.error(
                f"Failed to revoke token {token_id} for user {self.user_id}: {e}"
            )
            return ServiceResult.error_result(
                "Failed to revoke API token", error_code="TOKEN_REVOKE_FAILED"
            )
