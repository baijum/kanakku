"""Shared service functions used across different modules"""

from datetime import datetime
from typing import Any, Dict, Optional

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db


class BaseService:
    """Base service class with common functionality"""

    @staticmethod
    def commit_or_rollback():
        """Safely commit database changes or rollback on error"""
        try:
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return False

    @staticmethod
    def safe_get_by_id(model_class, id: int, user_id: Optional[int] = None):
        """Safely get a model instance by ID with optional user ownership check"""
        try:
            query = model_class.query.filter_by(id=id)
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            return query.first()
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in safe_get_by_id: {str(e)}")
            return None

    @staticmethod
    def safe_delete(instance):
        """Safely delete a model instance"""
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error in safe_delete: {str(e)}")
            return False

    @staticmethod
    def paginate_query(query, page: int = 1, per_page: int = 20):
        """Paginate a SQLAlchemy query"""
        try:
            return query.paginate(page=page, per_page=per_page, error_out=False)
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
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        if start_dt and end_dt and start_dt > end_dt:
            return None, None, "Start date must be before end date"

        return start_dt, end_dt, None
    except ValueError as e:
        return None, None, f"Invalid date format: {str(e)}"


def sanitize_search_term(term: str) -> str:
    """Sanitize search terms for database queries"""
    if not term:
        return ""

    # Remove special characters that could cause issues
    import re

    sanitized = re.sub(r"[^\w\s-]", "", term.strip())
    return sanitized[:100]  # Limit length


def calculate_pagination_metadata(pagination) -> Dict:
    """Calculate pagination metadata for API responses"""
    if not pagination:
        return {}

    return {
        "total_items": pagination.total,
        "total_pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "next_page": pagination.next_num if pagination.has_next else None,
        "prev_page": pagination.prev_num if pagination.has_prev else None,
    }
