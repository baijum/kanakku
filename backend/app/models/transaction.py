from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from ..extensions import db


class SearchVectorType(TypeDecorator):
    """Custom type that uses TSVECTOR for PostgreSQL and TEXT for other databases"""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(TSVECTOR())
        else:
            return dialect.type_descriptor(Text())


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
    search_vector = Column(SearchVectorType, nullable=True)  # Full-text search vector
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    book = relationship("Book", back_populates="transactions")
    account = relationship("Account", backref="transactions")

    @staticmethod
    def from_dict(data):
        """Create transaction from dictionary data"""
        return Transaction(
            date=data.get("date"),
            description=data.get("description"),
            amount=data.get("amount"),
            currency=data.get("currency", "INR"),
        )

    def to_dict(self):
        """Convert transaction to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "account_id": self.account_id,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "payee": self.payee,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_ledger_string(self):
        """Convert transaction to ledger format string"""
        date_str = self.date.strftime("%Y-%m-%d") if self.date else ""
        status_str = self.status if self.status else ""
        payee_str = f" {self.payee}" if self.payee else ""

        return f"{date_str}{status_str}{payee_str}\n    {self.description}    {self.currency} {self.amount}"

    def __repr__(self):
        return f"<Transaction {self.description}: {self.amount}>"
