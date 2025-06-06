# Import all models from the new modular structure
from .models import (
    Account,
    ApiToken,
    BankAccountMapping,
    BaseModel,
    Book,
    EmailConfiguration,
    ExpenseAccountMapping,
    GlobalConfiguration,
    Preamble,
    ProcessedGmailMessage,
    SearchVectorType,
    Transaction,
    User,
)

# Re-export all models for backward compatibility
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
