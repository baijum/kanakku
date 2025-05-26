from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..extensions import db


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
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }

    def __repr__(self):
        return f"<Account {self.name}>"
