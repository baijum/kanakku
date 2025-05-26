import secrets
from datetime import datetime, timedelta, timezone

from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..utils.logging_utils import log_debug


class User(UserMixin, db.Model):
    """
    User model represents application users with authentication and profile information.
    Supports both traditional username/password and Google OAuth authentication.
    """

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    name = Column(String(100))
    active_book_id = Column(
        Integer,
        ForeignKey("book.id"),
        nullable=True,
    )
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Password reset fields
    reset_token = Column(String(100), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)

    # Google Auth fields
    google_id = Column(String(100), unique=True, nullable=True)
    picture = Column(String(500), nullable=True)

    # Define relationships once, with consistent backrefs
    transactions = relationship(
        "Transaction", backref="user", lazy=True, foreign_keys="Transaction.user_id"
    )
    accounts = relationship(
        "Account", backref="user", lazy=True, foreign_keys="Account.user_id"
    )
    preambles = relationship(
        "Preamble", backref="user", lazy=True, foreign_keys="Preamble.user_id"
    )
    api_tokens = relationship(
        "ApiToken", backref="user", lazy=True, foreign_keys="ApiToken.user_id"
    )
    books = relationship("Book", back_populates="user", foreign_keys="Book.user_id")
    active_book = relationship("Book", foreign_keys=[active_book_id])

    def set_password(self, password):
        """Set user password by generating a secure hash"""
        log_debug(
            "Setting password for user",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )
        self.password_hash = generate_password_hash(password)
        log_debug("Password hash generated successfully", module_name="User")

    def check_password(self, password):
        """Verify password against stored hash"""
        log_debug(
            "Checking password for user",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )
        result = check_password_hash(self.password_hash, password)
        log_debug(
            f"Password check result: {'success' if result else 'failed'}",
            extra_data={"user_id": self.id},
            module_name="User",
        )
        return result

    def activate(self):
        """Activate user account"""
        log_debug(
            "Activating user account",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )
        self.is_active = True
        db.session.commit()
        log_debug("User account activated successfully", module_name="User")

    def deactivate(self):
        """Deactivate user account"""
        log_debug(
            "Deactivating user account",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )
        self.is_active = False
        db.session.commit()
        log_debug("User account deactivated successfully", module_name="User")

    def generate_reset_token(self):
        """Generate a secure token for password reset with 24-hour expiration"""
        log_debug(
            "Generating password reset token",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        log_debug(
            "Password reset token generated",
            extra_data={
                "user_id": self.id,
                "expires_at": self.reset_token_expires_at.isoformat(),
            },
            module_name="User",
        )
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify reset token validity and expiration"""
        log_debug(
            "Verifying password reset token",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )

        if not self.reset_token or self.reset_token != token:
            log_debug(
                "Reset token verification failed: token mismatch", module_name="User"
            )
            return False
        if not self.reset_token_expires_at:
            log_debug(
                "Reset token verification failed: no expiration set", module_name="User"
            )
            return False

        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        if self.reset_token_expires_at.tzinfo is None:
            self.reset_token_expires_at = self.reset_token_expires_at.replace(
                tzinfo=timezone.utc
            )

        is_valid = self.reset_token_expires_at > now
        log_debug(
            f"Reset token verification result: {'valid' if is_valid else 'expired'}",
            extra_data={
                "user_id": self.id,
                "expires_at": self.reset_token_expires_at.isoformat(),
                "current_time": now.isoformat(),
            },
            module_name="User",
        )
        return is_valid

    def clear_reset_token(self):
        """Clear reset token after use"""
        log_debug(
            "Clearing password reset token",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )
        self.reset_token = None
        self.reset_token_expires_at = None
        db.session.commit()
        log_debug("Password reset token cleared", module_name="User")

    def get_token(self):
        """Generate JWT token for the user with appropriate expiration"""
        from datetime import datetime, timedelta, timezone

        import jwt
        from flask import current_app

        log_debug(
            "Generating JWT token for user",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )

        payload = {
            "user_id": self.id,
            "exp": datetime.now(timezone.utc)
            + current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", timedelta(days=1)),
            "iat": datetime.now(timezone.utc),
        }

        token = jwt.encode(
            payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )

        log_debug(
            "JWT token generated successfully",
            extra_data={"user_id": self.id, "expires_at": payload["exp"].isoformat()},
            module_name="User",
        )

        return token

    def to_dict(self):
        """Convert user to dictionary for API responses, excluding sensitive information"""
        log_debug(
            "Converting user to dictionary",
            extra_data={"user_id": self.id, "email": self.email},
            module_name="User",
        )

        data = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "picture": self.picture,
            "active_book_id": self.active_book_id,
        }

        # Include active_book information if available
        if self.active_book_id and self.active_book:
            log_debug(
                "Including active book information in user dict", module_name="User"
            )
            data["active_book"] = self.active_book.to_dict()

        log_debug("User dictionary conversion completed", module_name="User")
        return data

    def __repr__(self):
        return f"<User {self.email}>"
