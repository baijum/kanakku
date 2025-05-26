"""
Centralized imports for Kanakku project.

This module provides clean, consistent imports for backend models and utilities
that can be used across the project without complex path manipulation.
"""

# Ensure paths are set up
from . import setup_project_paths

setup_project_paths()

# Backend model imports
try:
    from app.models import (
        Account,
        ApiToken,
        BankAccountMapping,
        Book,
        EmailConfiguration,
        ExpenseAccountMapping,
        GlobalConfiguration,
        Preamble,
        ProcessedGmailMessage,
        Transaction,
        User,
    )
except ImportError as e:
    # Fallback for when backend is not available
    print(f"Warning: Could not import backend models: {e}")
    EmailConfiguration = None
    GlobalConfiguration = None
    ProcessedGmailMessage = None
    User = None
    Account = None
    Transaction = None
    Book = None
    BankAccountMapping = None
    ExpenseAccountMapping = None
    ApiToken = None
    Preamble = None

# Backend utility imports
try:
    from app.utils.encryption import (
        decrypt_value,
        decrypt_value_standalone,
        encrypt_value,
        get_encryption_key,
        get_encryption_key_standalone,
    )
except ImportError as e:
    print(f"Warning: Could not import backend encryption utilities: {e}")
    encrypt_value = None
    decrypt_value = None
    decrypt_value_standalone = None
    get_encryption_key = None
    get_encryption_key_standalone = None

# Backend service imports
try:
    from app.services.gmail_message_service import (
        clear_processed_gmail_msgids,
        get_processed_message_count,
        is_gmail_message_processed,
        load_processed_gmail_msgids,
        save_processed_gmail_msgid,
        save_processed_gmail_msgids,
    )
except ImportError as e:
    print(f"Warning: Could not import backend services: {e}")
    load_processed_gmail_msgids = None
    save_processed_gmail_msgid = None
    save_processed_gmail_msgids = None
    is_gmail_message_processed = None
    get_processed_message_count = None
    clear_processed_gmail_msgids = None

# Banktransactions core imports
try:
    from banktransactions.core.api_client import APIClient, send_transaction_to_api
    from banktransactions.core.email_parser import extract_transaction_details
    from banktransactions.core.imap_client import CustomIMAPClient, get_bank_emails
    from banktransactions.core.transaction_data import construct_transaction_data
except ImportError as e:
    print(f"Warning: Could not import banktransactions core modules: {e}")
    extract_transaction_details = None
    get_bank_emails = None
    CustomIMAPClient = None
    construct_transaction_data = None
    send_transaction_to_api = None
    APIClient = None

# Banktransactions automation imports
try:
    from banktransactions.automation.email_processor import (
        process_user_emails_standalone,
    )
    from banktransactions.automation.job_utils import (
        generate_job_id,
        get_user_job_status,
        has_user_job_pending,
    )
except ImportError as e:
    print(f"Warning: Could not import banktransactions automation modules: {e}")
    generate_job_id = None
    get_user_job_status = None
    has_user_job_pending = None
    process_user_emails_standalone = None

# Backend config manager imports
try:
    from app.utils.config_manager import get_gemini_api_token
except ImportError as e:
    print(f"Warning: Could not import backend config manager: {e}")
    get_gemini_api_token = None

# Database utilities
try:
    from .database import (
        DatabaseManager,
        TestDatabaseManager,
        database_session,
        get_database_session,
        get_flask_or_standalone_session,
    )
except ImportError as e:
    print(f"Warning: Could not import database utilities: {e}")
    DatabaseManager = None
    get_database_session = None
    database_session = None
    get_flask_or_standalone_session = None
    TestDatabaseManager = None

# Unified service layer imports
try:
    from .services import (
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
    from .services.auth import AuthService, UserManagementService
    from .services.configuration import ConfigurationService, UserConfigurationService
    from .services.email import EmailParsingService, EmailProcessingService
    from .services.encryption import EncryptionService
    from .services.transaction import TransactionService
except ImportError as e:
    print(f"Warning: Could not import unified services: {e}")
    BaseService = None
    StatelessService = None
    ServiceResult = None
    ServiceError = None
    ValidationError = None
    NotFoundError = None
    PermissionError = None
    require_user_context = None
    log_service_call = None
    ConfigurationService = None
    UserConfigurationService = None
    EncryptionService = None
    EmailProcessingService = None
    EmailParsingService = None
    TransactionService = None
    AuthService = None
    UserManagementService = None

# Export all available imports
__all__ = [
    # Models
    "EmailConfiguration",
    "GlobalConfiguration",
    "ProcessedGmailMessage",
    "User",
    "Account",
    "Transaction",
    "Book",
    "BankAccountMapping",
    "ExpenseAccountMapping",
    "ApiToken",
    "Preamble",
    # Encryption utilities
    "encrypt_value",
    "decrypt_value",
    "decrypt_value_standalone",
    "get_encryption_key",
    "get_encryption_key_standalone",
    # Services
    "load_processed_gmail_msgids",
    "save_processed_gmail_msgid",
    "save_processed_gmail_msgids",
    "is_gmail_message_processed",
    "get_processed_message_count",
    "clear_processed_gmail_msgids",
    # Core functions
    "extract_transaction_details",
    "get_bank_emails",
    "CustomIMAPClient",
    "construct_transaction_data",
    "send_transaction_to_api",
    "APIClient",
    # Automation functions
    "generate_job_id",
    "get_user_job_status",
    "has_user_job_pending",
    "process_user_emails_standalone",
    # Config functions
    "get_gemini_api_token",
    # Database utilities
    "DatabaseManager",
    "get_database_session",
    "database_session",
    "get_flask_or_standalone_session",
    "TestDatabaseManager",
    # Unified services
    "BaseService",
    "StatelessService",
    "ServiceResult",
    "ServiceError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    "require_user_context",
    "log_service_call",
    "ConfigurationService",
    "UserConfigurationService",
    "EncryptionService",
    "EmailProcessingService",
    "EmailParsingService",
    "TransactionService",
    "AuthService",
    "UserManagementService",
]
