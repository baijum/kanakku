"""Shared service functions used across different modules"""

from datetime import datetime
from typing import Any, Dict, Optional

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..utils.logging_utils import (
    log_db_error,
    log_debug,
    log_service_entry,
    log_service_exit,
)


class BaseService:
    """Base service class with common functionality"""

    def get_service_name(self) -> str:
        """Return the name of the service for logging purposes."""
        return self.__class__.__name__

    def log_entry(self, method_name: str, **kwargs):
        """Log entry into a service method."""
        log_service_entry(self.get_service_name(), method_name, **kwargs)

    def log_exit(self, method_name: str, result_summary: Optional[str] = None):
        """Log exit from a service method."""
        log_service_exit(self.get_service_name(), method_name, result_summary)

    def log_debug(self, message: str, extra_data: Optional[Dict] = None):
        """Log a debug message with service context."""
        log_debug(message, extra_data=extra_data, module_name=self.get_service_name())

    @staticmethod
    def commit_or_rollback():
        """Safely commit database changes or rollback on error"""
        try:
            log_debug("Attempting database commit", module_name="BaseService")
            db.session.commit()
            log_debug("Database commit successful", module_name="BaseService")
            return True
        except SQLAlchemyError as e:
            log_debug("Database commit failed, rolling back", module_name="BaseService")
            db.session.rollback()
            log_db_error(e, operation="commit")
            return False

    @staticmethod
    def safe_get_by_id(model_class, id: int, user_id: Optional[int] = None):
        """Safely get a model instance by ID with optional user ownership check"""
        try:
            model_name = model_class.__name__
            log_debug(
                f"Fetching {model_name} by ID",
                extra_data={"id": id, "user_id": user_id},
                module_name="BaseService",
            )

            query = model_class.query.filter_by(id=id)
            if user_id is not None:
                query = query.filter_by(user_id=user_id)

            result = query.first()

            if result:
                log_debug(
                    f"{model_name} found",
                    extra_data={"id": id},
                    module_name="BaseService",
                )
            else:
                log_debug(
                    f"{model_name} not found",
                    extra_data={"id": id},
                    module_name="BaseService",
                )

            return result
        except SQLAlchemyError as e:
            log_db_error(
                e, operation="get_by_id", model=model_class.__name__, record_id=id
            )
            return None

    @staticmethod
    def safe_delete(instance):
        """Safely delete a model instance"""
        try:
            model_name = instance.__class__.__name__
            instance_id = getattr(instance, "id", "unknown")

            log_debug(
                f"Deleting {model_name}",
                extra_data={"id": instance_id},
                module_name="BaseService",
            )

            db.session.delete(instance)
            db.session.commit()

            log_debug(
                f"{model_name} deleted successfully",
                extra_data={"id": instance_id},
                module_name="BaseService",
            )
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            log_db_error(e, operation="delete", model=instance.__class__.__name__)
            return False

    @staticmethod
    def paginate_query(query, page: int = 1, per_page: int = 20):
        """Paginate a SQLAlchemy query"""
        try:
            log_debug(
                "Paginating query",
                extra_data={"page": page, "per_page": per_page},
                module_name="BaseService",
            )

            result = query.paginate(page=page, per_page=per_page, error_out=False)

            log_debug(
                "Pagination successful",
                extra_data={
                    "total_items": result.total,
                    "total_pages": result.pages,
                    "current_page": result.page,
                },
                module_name="BaseService",
            )

            return result
        except Exception as e:
            current_app.logger.error(f"Pagination error: {str(e)}")
            return None


def format_api_response(
    data: Any, message: str = None, status: str = "success"
) -> Dict:
    """Format consistent API responses"""
    response = {"status": status, "data": data}
    if message:
        response["message"] = message
    return response


def format_error_response(
    message: str, details: Dict = None, status: str = "error"
) -> Dict:
    """Format consistent error responses"""
    response = {"status": status, "error": message}
    if details:
        response["details"] = details
    return response


def validate_date_range(
    start_date: str, end_date: str
) -> tuple[Optional[datetime], Optional[datetime], Optional[str]]:
    """Validate and parse date range strings"""
    try:
        log_debug(
            "Validating date range",
            extra_data={"start_date": start_date, "end_date": end_date},
            module_name="DateValidator",
        )

        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        if start_dt and end_dt and start_dt > end_dt:
            log_debug(
                "Date range validation failed: start date after end date",
                module_name="DateValidator",
            )
            return None, None, "Start date must be before end date"

        log_debug("Date range validation successful", module_name="DateValidator")
        return start_dt, end_dt, None
    except ValueError as e:
        log_debug(
            f"Date range validation failed: {str(e)}", module_name="DateValidator"
        )
        return None, None, f"Invalid date format: {str(e)}"


def sanitize_search_term(term: str) -> str:
    """Sanitize search terms for database queries"""
    if not term:
        return ""

    log_debug(
        "Sanitizing search term",
        extra_data={"original_length": len(term)},
        module_name="SearchSanitizer",
    )

    # Remove special characters that could cause issues
    import re

    sanitized = re.sub(r"[^\w\s-]", "", term.strip())
    sanitized = sanitized[:100]  # Limit length

    log_debug(
        "Search term sanitized",
        extra_data={"sanitized_length": len(sanitized)},
        module_name="SearchSanitizer",
    )

    return sanitized


def calculate_pagination_metadata(pagination) -> Dict:
    """Calculate pagination metadata for API responses"""
    if not pagination:
        return {}

    metadata = {
        "total_items": pagination.total,
        "total_pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "next_page": pagination.next_num if pagination.has_next else None,
        "prev_page": pagination.prev_num if pagination.has_prev else None,
    }

    log_debug(
        "Calculated pagination metadata",
        extra_data=metadata,
        module_name="PaginationHelper",
    )

    return metadata


def get_active_book_id() -> int:
    """Get the active book ID for the current user or create a default book if not set."""
    from flask import g

    from ..models import Book

    user = g.current_user

    log_debug(
        "Getting active book ID",
        extra_data={"user_id": user.id, "current_active_book_id": user.active_book_id},
        module_name="BookHelper",
    )

    if not user.active_book_id:
        log_debug(
            "No active book set, searching for first book", module_name="BookHelper"
        )

        # Try to find first book ordered by ID
        first_book = Book.query.filter_by(user_id=user.id).order_by(Book.id).first()
        if first_book:
            log_debug(
                "Found existing book, setting as active",
                extra_data={"book_id": first_book.id, "book_name": first_book.name},
                module_name="BookHelper",
            )
            user.active_book_id = first_book.id
            db.session.commit()
        else:
            log_debug("No books found, creating default book", module_name="BookHelper")
            # Create a default book
            default_book = Book(user_id=user.id, name="Book 1")
            db.session.add(default_book)
            db.session.flush()
            user.active_book_id = default_book.id
            db.session.commit()
            log_debug(
                "Default book created and set as active",
                extra_data={"book_id": default_book.id},
                module_name="BookHelper",
            )

    log_debug(
        "Active book ID determined",
        extra_data={"active_book_id": user.active_book_id},
        module_name="BookHelper",
    )
    return user.active_book_id
