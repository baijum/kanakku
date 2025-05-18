from datetime import datetime, timezone, timedelta
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Date,
    Boolean,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
import secrets


class Book(db.Model):
    """
    Book model represents an accounting book that contains accounts and transactions.
    Each user can have multiple books for different purposes (e.g., personal, business).
    """

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="books", foreign_keys=[user_id])
    accounts = relationship(
        "Account", back_populates="book", lazy=True, cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="book", lazy=True, cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_book_user_name"),)

    def to_dict(self):
        """Convert book to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


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
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def activate(self):
        """Activate user account"""
        self.is_active = True
        db.session.commit()

    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        db.session.commit()

    def generate_reset_token(self):
        """Generate a secure token for password reset with 24-hour expiration"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify reset token validity and expiration"""
        if not self.reset_token or self.reset_token != token:
            return False
        if not self.reset_token_expires_at:
            return False
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        if self.reset_token_expires_at.tzinfo is None:
            self.reset_token_expires_at = self.reset_token_expires_at.replace(
                tzinfo=timezone.utc
            )
        return self.reset_token_expires_at > now

    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expires_at = None
        db.session.commit()

    def get_token(self):
        """Generate JWT token for the user with appropriate expiration"""
        from flask import current_app
        import jwt
        from datetime import datetime, timezone, timedelta

        payload = {
            "user_id": self.id,
            "exp": datetime.now(timezone.utc)
            + current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", timedelta(days=1)),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(
            payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )

    def to_dict(self):
        """Convert user to dictionary for API responses, excluding sensitive information"""
        data = {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "picture": self.picture,
            "active_book_id": self.active_book_id,
        }

        # Include active_book information if available
        if self.active_book_id and self.active_book:
            data["active_book"] = self.active_book.to_dict()

        return data

    def __repr__(self):
        return f"<User {self.email}>"


class Transaction(db.Model):
    """
    Transaction model represents financial transactions in the system.
    Each transaction belongs to a specific user and book, and is associated with an account.
    Includes details like date, amount, currency, and status.
    """

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("account.id"))
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    payee = Column(String(100))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    status = Column(String(1), nullable=True)  # * for cleared, ! for pending
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    book = relationship("Book", back_populates="transactions")
    account = relationship("Account", backref="transactions")

    @staticmethod
    def from_dict(data):
        """Create transaction instance from dictionary data, handling date string conversion"""
        if isinstance(data["date"], str):
            data = data.copy()
            data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        return Transaction(**data)

    def to_dict(self):
        """Convert transaction to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "account_id": self.account_id,
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "payee": self.payee,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

    def to_ledger_string(self):
        """Convert transaction to ledger-compatible format string"""
        date_str = self.date.strftime("%Y-%m-%d")
        status_str = self.status if self.status else ""
        payee_str = self.payee if self.payee else ""

        result = f"{date_str} {status_str} {payee_str}\n"
        result += f"    {self.description}  {self.amount} {self.currency}\n"

        return result

    def __repr__(self):
        return f"<Transaction {self.id}: {self.description}>"


class Account(db.Model):
    """
    Account model represents financial accounts in the system.
    Each account belongs to a specific user and book, and can have multiple transactions.
    Accounts track balance and support different currencies.
    """

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(200))
    currency = Column(String(3), default="INR")
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    book = relationship("Book", back_populates="accounts")

    __table_args__ = (UniqueConstraint("book_id", "name", name="uq_account_book_name"),)

    def to_dict(self):
        """Convert account to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "name": self.name,
            "description": self.description,
            "currency": self.currency,
            "balance": self.balance,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Account {self.name}>"


class Preamble(db.Model):
    """
    Preamble model represents custom configurations or templates for ledger output.
    Users can create multiple preambles and set one as default.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_preamble_user_name"),
    )

    def to_dict(self):
        """Convert preamble to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "content": self.content,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<Preamble {self.name}>"


class ApiToken(db.Model):
    """
    ApiToken model for API authentication without using JWT.
    Allows for long-lived, named API tokens for programmatic access.
    """

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime, nullable=True)

    @staticmethod
    def generate_token():
        """Generate a secure random token for API authentication"""
        return secrets.token_urlsafe(48)  # 64 bytes

    def is_expired(self):
        """Check if token has expired"""
        if not self.expires_at:
            return False  # No expiration date
        now = datetime.now(timezone.utc)
        # Ensure timezone-aware comparison
        if self.expires_at.tzinfo is None:
            self.expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        return self.expires_at < now

    def is_valid(self):
        """Check if token is valid (active and not expired)"""
        return self.is_active and not self.is_expired()

    def update_last_used(self):
        """Update the last used timestamp to now"""
        self.last_used_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self):
        """Convert API token to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "token": self.token,  # Note: only shown once when created
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
        }

    def __repr__(self):
        return f"<ApiToken {self.name}>"


class EmailConfiguration(db.Model):
    """
    EmailConfiguration model represents email account configuration for transaction import.
    Each user can configure email settings to automatically import transactions from bank emails.
    """
    __tablename__ = 'user_email_configurations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_enabled = Column(Boolean, default=False)
    imap_server = Column(String(255), default='imap.gmail.com')
    imap_port = Column(Integer, default=993)
    email_address = Column(String(255), nullable=False)
    app_password = Column(String(255), nullable=False)  # Will be encrypted
    polling_interval = Column(String(50), default='hourly')  # hourly, daily, etc.
    last_check_time = Column(DateTime, nullable=True)
    sample_emails = Column(Text, nullable=True)  # JSON string of sample emails
    last_processed_email_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", backref="email_configuration", lazy=True)

    def to_dict(self):
        """Convert configuration to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_enabled": self.is_enabled,
            "imap_server": self.imap_server,
            "imap_port": self.imap_port,
            "email_address": self.email_address,
            "polling_interval": self.polling_interval,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "last_processed_email_id": self.last_processed_email_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<EmailConfiguration {self.email_address}>"


class BankAccountMapping(db.Model):
    """
    BankAccountMapping model represents mappings between bank account identifiers
    and ledger account names. Used for automated transaction processing from bank emails.
    """
    __tablename__ = 'bank_account_mappings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    account_identifier = Column(String(100), nullable=False)  # Masked account number like XX1234
    ledger_account = Column(String(255), nullable=False)  # Full ledger account path like "Assets:Bank:Axis"
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", backref="bank_account_mappings", lazy=True)
    book = relationship("Book", backref="bank_account_mappings", lazy=True)

    __table_args__ = (
        UniqueConstraint("book_id", "account_identifier", name="uq_bank_account_mapping_book_identifier"),
    )

    def to_dict(self):
        """Convert mapping to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "account_identifier": self.account_identifier,
            "ledger_account": self.ledger_account,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<BankAccountMapping {self.account_identifier} -> {self.ledger_account}>"


class ExpenseAccountMapping(db.Model):
    """
    ExpenseAccountMapping model represents mappings between merchant/payee names
    and ledger expense accounts. Used for automated transaction categorization from bank emails.
    """
    __tablename__ = 'expense_account_mappings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    merchant_name = Column(String(255), nullable=False)  # Merchant/payee name as it appears in bank emails
    ledger_account = Column(String(255), nullable=False)  # Full ledger account path like "Expenses:Food:Restaurant"
    description = Column(String(255), nullable=True)  # Additional description for the mapping
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", backref="expense_account_mappings", lazy=True)
    book = relationship("Book", backref="expense_account_mappings", lazy=True)

    __table_args__ = (
        UniqueConstraint("book_id", "merchant_name", name="uq_expense_account_mapping_book_merchant"),
    )

    def to_dict(self):
        """Convert mapping to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "merchant_name": self.merchant_name,
            "ledger_account": self.ledger_account,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ExpenseAccountMapping {self.merchant_name} -> {self.ledger_account}>"
