"""Models package - imports all models for easy access"""

# Import database instance
from ..extensions import db

# Import base model
from .account import Account
from .base import BaseModel
from .book import Book

# Import other models
from .other import (
    ApiToken,
    BankAccountMapping,
    EmailConfiguration,
    ExpenseAccountMapping,
    GlobalConfiguration,
    Preamble,
    ProcessedGmailMessage,
)
from .transaction import SearchVectorType, Transaction

# Import core models
from .user import User

# Export all models for easy importing
__all__ = [
    "db",
    "BaseModel",
    "User",
    "Book",
    "Account",
    "Transaction",
    "SearchVectorType",
    "Preamble",
    "ApiToken",
    "EmailConfiguration",
    "BankAccountMapping",
    "ExpenseAccountMapping",
    "GlobalConfiguration",
    "ProcessedGmailMessage",
]
