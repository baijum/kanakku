"""
Base service classes and utilities for unified service layer.

Provides common functionality and patterns for all services across
backend and banktransactions modules.
"""

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..database import get_flask_or_standalone_session

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Base exception for service layer errors."""


class ValidationError(ServiceError):
    """Raised when service input validation fails."""


class NotFoundError(ServiceError):
    """Raised when a requested resource is not found."""


class PermissionError(ServiceError):
    """Raised when user lacks permission for an operation."""


class ServiceResult:
    """Standardized result object for service operations."""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: str = None,
        error_code: str = None,
        metadata: Dict = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)

    @classmethod
    def success_result(cls, data: Any = None, metadata: Dict = None):
        """Create a successful result."""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def error_result(cls, error: str, error_code: str = None, metadata: Dict = None):
        """Create an error result."""
        return cls(success=False, error=error, error_code=error_code, metadata=metadata)

    def to_dict(self) -> Dict:
        """Convert result to dictionary for API responses."""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }

        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
            if self.error_code:
                result["error_code"] = self.error_code

        if self.metadata:
            result["metadata"] = self.metadata

        return result


class BaseService(ABC):
    """Base class for all services with common functionality."""

    def __init__(self, user_id: Optional[int] = None, session=None):
        self.user_id = user_id
        self._session = session
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    @abstractmethod
    def get_service_name(self) -> str:
        """Return the name of the service for logging purposes."""

    @property
    def session(self):
        """Get database session, creating one if needed."""
        if self._session is None:
            self._session = get_flask_or_standalone_session()
        return self._session

    @contextmanager
    def transaction_scope(self):
        """Provide a transactional scope for service operations."""
        try:
            yield self.session
            if hasattr(self.session, "commit"):
                self.session.commit()
        except Exception as e:
            if hasattr(self.session, "rollback"):
                self.session.rollback()
            self.logger.error(f"Transaction rolled back: {e}")
            raise

    def validate_user_access(self, resource_user_id: int) -> bool:
        """Validate that current user can access a resource."""
        if self.user_id is None:
            raise PermissionError("No user context available")

        if self.user_id != resource_user_id:
            raise PermissionError("User does not have access to this resource")

        return True

    def log_operation(self, operation: str, details: Dict = None):
        """Log service operation for auditing."""
        log_data = {
            "service": self.__class__.__name__,
            "operation": operation,
            "user_id": self.user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if details:
            log_data.update(details)

        self.logger.info(f"Service operation: {operation}", extra=log_data)


class StatelessService:
    """Base class for stateless services that don't require user context."""

    def __init__(self):
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    def log_operation(self, operation: str, details: Dict = None):
        """Log service operation for auditing."""
        log_data = {
            "service": self.__class__.__name__,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if details:
            log_data.update(details)

        self.logger.info(f"Service operation: {operation}", extra=log_data)


# Utility decorators for service methods
def require_user_context(func):
    """Decorator to ensure service has user context."""

    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "user_id") or self.user_id is None:
            raise PermissionError("Operation requires user context")
        return func(self, *args, **kwargs)

    return wrapper


def log_service_call(operation_name: str = None):
    """Decorator to automatically log service method calls."""

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            op_name = operation_name or func.__name__
            self.log_operation(
                op_name, {"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
            )
            try:
                result = func(self, *args, **kwargs)
                self.log_operation(f"{op_name}_success")
                return result
            except Exception as e:
                self.log_operation(f"{op_name}_error", {"error": str(e)})
                raise

        return wrapper

    return decorator
