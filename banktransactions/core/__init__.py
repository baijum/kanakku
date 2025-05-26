"""
Core modules for bank transaction processing.

This package contains the core functionality for:
- Email parsing and transaction extraction
- IMAP client for email retrieval
- Transaction data processing
- API client for transaction submission
- Email deduplication
"""

# Export main functions for easy access
from .api_client import APIClient, send_transaction_to_api
from .email_parser import decode_str, extract_transaction_details
from .imap_client import CustomIMAPClient, get_bank_emails
from .processed_ids_db import load_processed_gmail_msgids, save_processed_gmail_msgid
from .transaction_data import construct_transaction_data, get_mappings_from_api

__all__ = [
    "extract_transaction_details",
    "decode_str",
    "get_bank_emails",
    "CustomIMAPClient",
    "construct_transaction_data",
    "get_mappings_from_api",
    "send_transaction_to_api",
    "APIClient",
    "load_processed_gmail_msgids",
    "save_processed_gmail_msgid",
]
