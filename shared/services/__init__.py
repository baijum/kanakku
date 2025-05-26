"""
Unified service layer for kanakku project.

This package provides a consistent service layer pattern across
backend and banktransactions modules.
"""

from .auth import AuthService, UserManagementService
from .base import (
    BaseService,
    NotFoundError,
    PermissionError,
    ServiceError,
    ServiceResult,
    StatelessService,
    ValidationError,
    log_service_call,
    require_user_context,
)
from .email import EmailParsingService, EmailProcessingService
from .transaction import TransactionService

__all__ = [
    "BaseService",
    "StatelessService",
    "ServiceResult",
    "ServiceError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    "require_user_context",
    "log_service_call",
    "EmailProcessingService",
    "EmailParsingService",
    "TransactionService",
    "AuthService",
    "UserManagementService",
]
