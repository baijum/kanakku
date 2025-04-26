"""
Utils package for the Kanakku application.
This package contains various utility functions that are used throughout the application.
"""

# Import the email utility function to maintain backward compatibility
from .email_utils import send_password_reset_email as send_password_reset_email

# Import logging utilities for easy access
from .logging_utils import (
    log_request as log_request,
    log_response as log_response,
    log_function_call as log_function_call,
    log_error as log_error,
    log_db_error as log_db_error,
)
