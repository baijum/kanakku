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
)
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
import secrets


class Book(db.Model):
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
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    name = Column(String(100))
    active_book_id = Column(
        Integer,
        ForeignKey("book.id", use_alter=True, name="fk_user_active_book"),
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
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def activate(self):
        self.is_active = True
        db.session.commit()

    def deactivate(self):
        self.is_active = False
        db.session.commit()

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
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
        self.reset_token = None
        self.reset_token_expires_at = None
        db.session.commit()

    def get_token(self):
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
        data = {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
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

    @staticmethod
    def from_dict(data):
        if isinstance(data["date"], str):
            data = data.copy()
            data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        return Transaction(**data)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "account_id": self.account_id,
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class Account(db.Model):
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


class Preamble(db.Model):
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
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "content": self.content,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ApiToken(db.Model):
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
        return secrets.token_hex(32)

    def is_expired(self):
        if not self.expires_at:
            return False
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            self.expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        return self.expires_at <= now

    def is_valid(self):
        return self.is_active and not self.is_expired()

    def update_last_used(self):
        self.last_used_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
            "is_active": self.is_active,
            # Don't include the actual token in the dict for security
        }
