"""
Banktransactions package for email automation and transaction processing.

This package contains modules for:
- Core email processing and transaction extraction (core/)
- Email automation and background processing (automation/)
- Comprehensive testing suite (tests/)
- Development tools and utilities (tools/)
- Documentation and configuration (docs/, config/)

The package is organized into logical groups for better maintainability:
- Use banktransactions.core for library functions
- Use banktransactions.automation for background processing
"""

__version__ = "2.0.0"

# Import key functions for easy access
from .core import (
    APIClient,
    CustomIMAPClient,
    construct_transaction_data,
    extract_transaction_details,
    get_bank_emails,
    send_transaction_to_api,
)

# Conditionally import automation functions (requires Flask context)
try:
    from .automation import EmailScheduler, process_user_emails_standalone

    _automation_available = True
except ImportError:
    _automation_available = False
    process_user_emails_standalone = None
    EmailScheduler = None

__all__ = [
    "extract_transaction_details",
    "get_bank_emails",
    "CustomIMAPClient",
    "construct_transaction_data",
    "send_transaction_to_api",
    "APIClient",
]

# Add automation functions to __all__ if available
if _automation_available:
    __all__.extend(["process_user_emails_standalone", "EmailScheduler"])
