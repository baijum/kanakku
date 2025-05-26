import secrets
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..extensions import db


class Preamble(db.Model):
    """
    Preamble model represents custom configurations or templates for ledger output.
    Users can create multiple preambles and set one as default.
    """

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
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
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
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
        """Generate a secure random token"""
        return secrets.token_hex(32)

    def is_expired(self):
        """Check if token is expired"""
        if not self.expires_at:
            return False
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            self.expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        return self.expires_at <= now

    def is_valid(self):
        """Check if token is valid (active and not expired)"""
        return self.is_active and not self.is_expired()

    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self):
        """Convert API token to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "name": self.name,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
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

    __tablename__ = "user_email_configurations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_enabled = Column(Boolean, default=False)
    imap_server = Column(String(255), default="imap.gmail.com")
    imap_port = Column(Integer, default=993)
    email_address = Column(String(255), nullable=False)
    app_password = Column(String(255), nullable=False)  # Will be encrypted
    polling_interval = Column(String(50), default="hourly")  # hourly, daily, etc.
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
        """Convert email configuration to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_enabled": self.is_enabled,
            "imap_server": self.imap_server,
            "imap_port": self.imap_port,
            "email_address": self.email_address,
            "polling_interval": self.polling_interval,
            "last_check_time": (
                self.last_check_time.isoformat() if self.last_check_time else None
            ),
            "last_processed_email_id": self.last_processed_email_id,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

    def __repr__(self):
        return f"<EmailConfiguration {self.email_address}>"


class BankAccountMapping(db.Model):
    """
    BankAccountMapping model represents mappings between bank account identifiers
    and ledger account names. Used for automated transaction processing from bank emails.
    """

    __tablename__ = "bank_account_mappings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    account_identifier = Column(
        String(100), nullable=False
    )  # Masked account number like XX1234
    ledger_account = Column(
        String(255), nullable=False
    )  # Full ledger account path like "Assets:Bank:Axis"
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
        UniqueConstraint(
            "user_id", "book_id", "account_identifier", name="uq_bank_account_mapping"
        ),
    )

    def to_dict(self):
        """Convert bank account mapping to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "account_identifier": self.account_identifier,
            "ledger_account": self.ledger_account,
            "description": self.description,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

    def __repr__(self):
        return (
            f"<BankAccountMapping {self.account_identifier} -> {self.ledger_account}>"
        )


class ExpenseAccountMapping(db.Model):
    """
    ExpenseAccountMapping model represents mappings between merchant/payee names
    and ledger expense accounts. Used for automated transaction categorization from bank emails.
    """

    __tablename__ = "expense_account_mappings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    merchant_name = Column(
        String(255), nullable=False
    )  # Merchant/payee name as it appears in bank emails
    ledger_account = Column(
        String(255), nullable=False
    )  # Full ledger account path like "Expenses:Food:Restaurant"
    description = Column(
        String(255), nullable=True
    )  # Additional description for the mapping
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
        UniqueConstraint(
            "user_id", "book_id", "merchant_name", name="uq_expense_account_mapping"
        ),
    )

    def to_dict(self):
        """Convert expense account mapping to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "merchant_name": self.merchant_name,
            "ledger_account": self.ledger_account,
            "description": self.description,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

    def __repr__(self):
        return f"<ExpenseAccountMapping {self.merchant_name} -> {self.ledger_account}>"


class GlobalConfiguration(db.Model):
    """
    GlobalConfiguration model represents application-wide settings and configurations.
    Used for storing sensitive information like API keys that are used across the application.
    """

    __tablename__ = "global_configurations"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)  # Will be encrypted for sensitive values
    description = Column(String(255), nullable=True)
    is_encrypted = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert global configuration to dictionary for API responses"""
        return {
            "id": self.id,
            "key": self.key,
            "value": "[ENCRYPTED]" if self.is_encrypted else self.value,
            "description": self.description,
            "is_encrypted": self.is_encrypted,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

    def __repr__(self):
        return f"<GlobalConfiguration {self.key}>"


class ProcessedGmailMessage(db.Model):
    """
    ProcessedGmailMessage model stores Gmail Message IDs that have been processed
    to avoid duplicate processing. Each record is associated with a specific user.
    """

    __tablename__ = "processed_gmail_messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    gmail_message_id = Column(String(255), nullable=False)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", backref="processed_gmail_messages", lazy=True)

    # Ensure unique combination of user_id and gmail_message_id
    __table_args__ = (
        UniqueConstraint(
            "user_id", "gmail_message_id", name="uq_processed_gmail_message"
        ),
    )

    def to_dict(self):
        """Convert processed Gmail message to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "gmail_message_id": self.gmail_message_id,
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }

    def __repr__(self):
        return f"<ProcessedGmailMessage {self.gmail_message_id}>"
