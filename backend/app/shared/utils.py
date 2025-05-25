"""Shared utility functions used across different modules"""

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from flask import current_app


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def generate_api_key(length: int = 64) -> str:
    """Generate a secure API key"""
    return secrets.token_hex(length // 2)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r"[^\w\s-.]", "", filename)
    # Replace spaces with underscores
    filename = re.sub(r"\s+", "_", filename)
    # Remove multiple consecutive dots
    filename = re.sub(r"\.+", ".", filename)
    return filename.strip("._")


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format currency amount for display"""
    currency_symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = currency_symbols.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"


def parse_amount_string(amount_str: str) -> Optional[float]:
    """Parse amount string to float, handling various formats"""
    if not amount_str:
        return None

    # Remove currency symbols and spaces
    cleaned = re.sub(r"[₹$€£,\s]", "", str(amount_str))

    try:
        return float(cleaned)
    except ValueError:
        return None


def validate_date_string(date_str: str) -> Optional[datetime]:
    """Validate and parse date string in various formats"""
    if not date_str:
        return None

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def get_date_range_for_period(period: str) -> tuple[datetime, datetime]:
    """Get start and end dates for common periods"""
    now = datetime.now(timezone.utc)

    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "this_week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(
            days=6, hours=23, minutes=59, seconds=59, microseconds=999999
        )
    elif period == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(
                microseconds=1
            )
        else:
            end = now.replace(month=now.month + 1, day=1) - timedelta(microseconds=1)
    elif period == "this_year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(
            month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
        )
    else:
        # Default to last 30 days
        start = now - timedelta(days=30)
        end = now

    return start, end


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like account numbers, keeping only last few characters visible"""
    if not data or len(data) <= visible_chars:
        return data

    masked_length = len(data) - visible_chars
    return mask_char * masked_length + data[-visible_chars:]


def extract_account_number_from_text(text: str) -> Optional[str]:
    """Extract account number patterns from text"""
    # Common patterns for account numbers
    patterns = [
        r"\b\d{4,20}\b",  # Basic numeric pattern
        r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,20}\b",  # IBAN-like pattern
        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Card-like pattern
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]

    return None


def clean_text_for_search(text: str) -> str:
    """Clean text for full-text search"""
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove special characters except spaces and hyphens
    text = re.sub(r"[^\w\s-]", " ", text)

    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def build_search_query(search_term: str) -> str:
    """Build PostgreSQL full-text search query"""
    if not search_term:
        return ""

    # Clean the search term
    cleaned = clean_text_for_search(search_term)

    # Split into words and join with & for AND search
    words = cleaned.split()
    if not words:
        return ""

    # Add prefix matching for partial word search
    query_parts = [f"{word}:*" for word in words if len(word) > 2]

    return " & ".join(query_parts)


def calculate_percentage_change(old_value: float, new_value: float) -> Optional[float]:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return None if new_value == 0 else float("inf")

    return ((new_value - old_value) / old_value) * 100


def round_currency(amount: float, currency: str = "INR") -> float:
    """Round currency amount to appropriate decimal places"""
    # Most currencies use 2 decimal places
    return round(amount, 2)


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def get_client_ip(request) -> str:
    """Get client IP address from request, considering proxies"""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.remote_addr or "unknown"


def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None):
    """Log user actions for audit trail"""
    log_data = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {},
    }

    current_app.logger.info(f"User action: {log_data}")

    # In a production system, you might want to store this in a separate audit log table
    # or send to an external logging service
