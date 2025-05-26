"""
Unified service layer for kanakku project.

This package provides a consistent service layer pattern across
backend and banktransactions modules.
"""

from .base import (
    BaseService,
    StatelessService,
    ServiceResult,
    ServiceError,
    ValidationError,
    NotFoundError,
    PermissionError,
    require_user_context,
    log_service_call,
)
from .email import EmailProcessingService, EmailParsingService
from .transaction import TransactionService
from .auth import AuthService, UserManagementService

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
