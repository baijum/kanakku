from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..extensions import db


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

    def __repr__(self):
        return f"<Book {self.name}>"
