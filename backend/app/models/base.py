from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer

from ..extensions import db


class BaseModel(db.Model):
    """Base model class with common fields and functionality"""

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
