"""Models package - imports all models for easy access"""

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
