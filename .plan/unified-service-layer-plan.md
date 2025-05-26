# Unified Service Layer Plan

## Overview

This plan addresses the fifth and final refactoring recommendation: **Create unified service layer**. The goal is to establish a consistent, well-structured service layer pattern across the entire `kanakku` project, consolidating business logic and creating reusable service components that work seamlessly between the `backend` Flask application and `banktransactions` processing modules.

## Current State Analysis

### Existing Service Layer Patterns

The `kanakku` project already has some service layer implementation in the backend:

**Backend Services (Well-Structured)**:
- `backend/app/auth_bp/services.py` - `AuthService` class
- `backend/app/accounts_bp/services.py` - `AccountService` class  
- `backend/app/books_bp/services.py` - `BookService` class
- `backend/app/transactions_bp/services.py` - `TransactionService` class
- `backend/app/reports_bp/services.py` - `ReportsService` class
- `backend/app/services/gmail_message_service.py` - Gmail message functions
- `backend/app/shared/services.py` - `BaseService` class

**Banktransactions Processing (Scattered Logic)**:
- `banktransactions/automation/email_processor.py` - Email processing logic
- `banktransactions/core/email_parser.py` - Email parsing logic
- `banktransactions/core/imap_client.py` - IMAP client logic
- `banktransactions/core/transaction_data.py` - Transaction construction logic
- `banktransactions/core/api_client.py` - API client logic

### Problems Identified

1. **Inconsistent Patterns**: Backend uses class-based services, banktransactions uses function-based modules
2. **Business Logic Scattered**: Email processing logic spread across multiple files
3. **No Cross-Module Reusability**: Backend services can't be easily used by banktransactions
4. **Duplicate Functionality**: Similar operations implemented differently in each module
5. **Testing Complexity**: Different testing approaches for different service patterns
6. **Maintenance Burden**: Changes to business logic require updates in multiple places

### Service Layer Gaps

**Missing Unified Services**:
- Email automation service (spans both modules)
- Configuration management service
- Encryption/decryption service (partially exists)
- Transaction processing service (exists in backend only)
- User management service (exists in backend only)
- Notification/logging service

## Proposed Solution

### 1. Create Unified Service Architecture

**New structure: `shared/services/`**

```
shared/
├── __init__.py
├── imports.py
├── database.py (from previous plan)
└── services/
    ├── __init__.py
    ├── base.py              # Base service classes and utilities
    ├── auth.py              # Authentication and user management
    ├── email.py             # Email processing and automation
    ├── encryption.py        # Encryption/decryption operations
    ├── configuration.py     # Configuration management
    ├── transaction.py       # Transaction processing
    ├── notification.py      # Logging and notifications
    └── integration.py       # Cross-module integration utilities
```

### 2. Base Service Framework

**New file: `shared/services/base.py`**

```python
"""
Base service classes and utilities for unified service layer.

Provides common functionality and patterns for all services across
backend and banktransactions modules.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager
from datetime import datetime

from ..database import get_flask_or_standalone_session

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass

class ValidationError(ServiceError):
    """Raised when service input validation fails."""
    pass

class NotFoundError(ServiceError):
    """Raised when a requested resource is not found."""
    pass

class PermissionError(ServiceError):
    """Raised when user lacks permission for an operation."""
    pass

class ServiceResult:
    """Standardized result object for service operations."""
    
    def __init__(self, success: bool, data: Any = None, error: str = None, 
                 error_code: str = None, metadata: Dict = None):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
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
            'success': self.success,
            'timestamp': self.timestamp.isoformat(),
        }
        
        if self.success:
            result['data'] = self.data
        else:
            result['error'] = self.error
            if self.error_code:
                result['error_code'] = self.error_code
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result

class BaseService(ABC):
    """Base class for all services with common functionality."""
    
    def __init__(self, user_id: Optional[int] = None, session=None):
        self.user_id = user_id
        self._session = session
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
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
            if hasattr(self.session, 'commit'):
                self.session.commit()
        except Exception as e:
            if hasattr(self.session, 'rollback'):
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
            'service': self.__class__.__name__,
            'operation': operation,
            'user_id': self.user_id,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(f"Service operation: {operation}", extra=log_data)

class StatelessService:
    """Base class for stateless services that don't require user context."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_operation(self, operation: str, details: Dict = None):
        """Log service operation for auditing."""
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(f"Service operation: {operation}", extra=log_data)

# Utility decorators for service methods
def require_user_context(func):
    """Decorator to ensure service has user context."""
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'user_id') or self.user_id is None:
            raise PermissionError("Operation requires user context")
        return func(self, *args, **kwargs)
    return wrapper

def log_service_call(operation_name: str = None):
    """Decorator to automatically log service method calls."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            op_name = operation_name or func.__name__
            self.log_operation(op_name, {'args_count': len(args), 'kwargs_keys': list(kwargs.keys())})
            try:
                result = func(self, *args, **kwargs)
                self.log_operation(f"{op_name}_success")
                return result
            except Exception as e:
                self.log_operation(f"{op_name}_error", {'error': str(e)})
                raise
        return wrapper
    return decorator
```

### 3. Email Processing Service

**New file: `shared/services/email.py`**

```python
"""
Unified email processing service.

Consolidates email automation logic from both backend and banktransactions
modules into a single, reusable service.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from .base import BaseService, ServiceResult, require_user_context, log_service_call
from ..database import database_session

class EmailProcessingService(BaseService):
    """Unified service for email processing and automation."""
    
    @require_user_context
    @log_service_call("process_user_emails")
    def process_user_emails(self) -> ServiceResult:
        """
        Process emails for the current user.
        Consolidates logic from banktransactions/automation/email_processor.py
        """
        try:
            # Get user's email configuration
            config = self._get_user_email_config()
            if not config or not config.is_enabled:
                return ServiceResult.error_result(
                    "Email configuration not found or disabled",
                    error_code="CONFIG_DISABLED"
                )
            
            # Decrypt credentials
            credentials = self._decrypt_email_credentials(config)
            if not credentials:
                return ServiceResult.error_result(
                    "Failed to decrypt email credentials",
                    error_code="DECRYPT_FAILED"
                )
            
            # Load processed message IDs
            processed_msgids = self._load_processed_message_ids()
            
            # Get bank emails from configuration
            bank_emails = self._extract_bank_emails(config)
            
            # Process emails
            result = self._process_emails_with_imap(
                credentials, bank_emails, processed_msgids
            )
            
            # Update last check time
            self._update_last_check_time(config)
            
            return ServiceResult.success_result(
                data=result,
                metadata={
                    'processed_count': result.get('processed_count', 0),
                    'bank_emails': bank_emails,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Email processing failed: {e}")
            return ServiceResult.error_result(
                f"Email processing failed: {str(e)}",
                error_code="PROCESSING_FAILED"
            )
    
    @require_user_context
    def get_email_configuration(self) -> ServiceResult:
        """Get user's email automation configuration."""
        try:
            from shared.imports import EmailConfiguration
            
            config = self.session.query(EmailConfiguration).filter_by(
                user_id=self.user_id
            ).first()
            
            if not config:
                return ServiceResult.success_result(data=None)
            
            # Return config without sensitive data
            config_dict = config.to_dict()
            config_dict.pop('app_password', None)
            
            return ServiceResult.success_result(data=config_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to get email configuration: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve email configuration",
                error_code="CONFIG_RETRIEVAL_FAILED"
            )
    
    @require_user_context
    def update_email_configuration(self, config_data: Dict) -> ServiceResult:
        """Update user's email automation configuration."""
        try:
            # Validate configuration data
            validation_result = self._validate_email_config(config_data)
            if not validation_result.success:
                return validation_result
            
            # Update or create configuration
            with self.transaction_scope():
                config = self._update_or_create_config(config_data)
                
                return ServiceResult.success_result(
                    data=config.to_dict(),
                    metadata={'operation': 'updated' if config.id else 'created'}
                )
                
        except Exception as e:
            self.logger.error(f"Failed to update email configuration: {e}")
            return ServiceResult.error_result(
                "Failed to update email configuration",
                error_code="CONFIG_UPDATE_FAILED"
            )
    
    @require_user_context
    def test_email_connection(self, credentials: Dict) -> ServiceResult:
        """Test email connection with provided credentials."""
        try:
            from shared.imports import CustomIMAPClient
            
            imap_client = CustomIMAPClient(
                server=credentials.get('imap_server', 'imap.gmail.com'),
                port=credentials.get('imap_port', 993),
                username=credentials['email_address'],
                password=credentials['app_password'],
            )
            
            # Test connection
            imap_client.connect()
            imap_client.disconnect()
            
            return ServiceResult.success_result(
                data={'connection_test': 'successful'},
                metadata={'server': credentials.get('imap_server', 'imap.gmail.com')}
            )
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return ServiceResult.error_result(
                f"Connection test failed: {str(e)}",
                error_code="CONNECTION_TEST_FAILED"
            )
    
    # Private helper methods
    def _get_user_email_config(self):
        """Get user's email configuration from database."""
        from shared.imports import EmailConfiguration
        return self.session.query(EmailConfiguration).filter_by(
            user_id=self.user_id
        ).first()
    
    def _decrypt_email_credentials(self, config) -> Optional[Dict]:
        """Decrypt email credentials from configuration."""
        try:
            from shared.imports import decrypt_value_standalone
            
            decrypted_password = decrypt_value_standalone(config.app_password)
            if not decrypted_password:
                return None
            
            return {
                'email_address': config.email_address,
                'app_password': decrypted_password,
                'imap_server': config.imap_server,
                'imap_port': config.imap_port,
            }
        except Exception as e:
            self.logger.error(f"Failed to decrypt credentials: {e}")
            return None
    
    def _load_processed_message_ids(self) -> Set[str]:
        """Load processed Gmail message IDs for user."""
        try:
            from shared.imports import load_processed_gmail_msgids
            return load_processed_gmail_msgids(user_id=self.user_id)
        except Exception as e:
            self.logger.error(f"Failed to load processed message IDs: {e}")
            return set()
    
    def _extract_bank_emails(self, config) -> List[str]:
        """Extract bank email addresses from configuration."""
        bank_emails = ["alerts@axisbank.com"]  # Default
        
        if config.sample_emails:
            try:
                sample_emails = json.loads(config.sample_emails)
                bank_emails_from_samples = []
                for sample in sample_emails:
                    if isinstance(sample, dict) and "from" in sample:
                        bank_emails_from_samples.append(sample["from"])
                if bank_emails_from_samples:
                    bank_emails = list(set(bank_emails_from_samples))
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse sample emails for user {self.user_id}")
        
        return bank_emails
    
    def _process_emails_with_imap(self, credentials: Dict, bank_emails: List[str], 
                                  processed_msgids: Set[str]) -> Dict:
        """Process emails using IMAP client."""
        try:
            from shared.imports import get_bank_emails, save_processed_gmail_msgid
            
            # Create callback for saving message IDs
            def save_msgid_callback(gmail_message_id):
                return save_processed_gmail_msgid(gmail_message_id, user_id=self.user_id)
            
            # Process emails
            updated_msgids, newly_processed_count = get_bank_emails(
                username=credentials['email_address'],
                password=credentials['app_password'],
                bank_email_list=bank_emails,
                processed_gmail_msgids=processed_msgids,
                save_msgid_callback=save_msgid_callback,
            )
            
            return {
                'processed_count': newly_processed_count,
                'total_processed': len(updated_msgids),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"IMAP processing failed: {e}")
            raise
    
    def _update_last_check_time(self, config):
        """Update the last check time for email configuration."""
        try:
            config.last_check_time = datetime.now(timezone.utc)
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to update last check time: {e}")
    
    def _validate_email_config(self, config_data: Dict) -> ServiceResult:
        """Validate email configuration data."""
        required_fields = ['email_address', 'app_password']
        missing_fields = [field for field in required_fields if not config_data.get(field)]
        
        if missing_fields:
            return ServiceResult.error_result(
                f"Missing required fields: {', '.join(missing_fields)}",
                error_code="VALIDATION_FAILED"
            )
        
        return ServiceResult.success_result()
    
    def _update_or_create_config(self, config_data: Dict):
        """Update existing or create new email configuration."""
        from shared.imports import EmailConfiguration, encrypt_value
        
        config = self.session.query(EmailConfiguration).filter_by(
            user_id=self.user_id
        ).first()
        
        if config:
            # Update existing
            config.is_enabled = config_data.get('is_enabled', False)
            config.imap_server = config_data.get('imap_server', 'imap.gmail.com')
            config.imap_port = config_data.get('imap_port', 993)
            config.email_address = config_data['email_address']
            config.app_password = encrypt_value(config_data['app_password'])
            config.polling_interval = config_data.get('polling_interval', 'hourly')
            config.sample_emails = json.dumps(config_data.get('sample_emails', []))
            config.updated_at = datetime.now(timezone.utc)
        else:
            # Create new
            config = EmailConfiguration(
                user_id=self.user_id,
                is_enabled=config_data.get('is_enabled', False),
                imap_server=config_data.get('imap_server', 'imap.gmail.com'),
                imap_port=config_data.get('imap_port', 993),
                email_address=config_data['email_address'],
                app_password=encrypt_value(config_data['app_password']),
                polling_interval=config_data.get('polling_interval', 'hourly'),
                sample_emails=json.dumps(config_data.get('sample_emails', [])),
            )
            self.session.add(config)
        
        return config

class EmailParsingService(StatelessService):
    """Service for parsing email content and extracting transaction details."""
    
    @log_service_call("extract_transaction_details")
    def extract_transaction_details(self, email_body: str) -> ServiceResult:
        """
        Extract transaction details from email body.
        Consolidates logic from banktransactions/core/email_parser.py
        """
        try:
            from shared.imports import extract_transaction_details
            
            details = extract_transaction_details(email_body)
            
            return ServiceResult.success_result(
                data=details,
                metadata={'extraction_method': 'llm_with_fallback'}
            )
            
        except Exception as e:
            self.logger.error(f"Transaction extraction failed: {e}")
            return ServiceResult.error_result(
                f"Failed to extract transaction details: {str(e)}",
                error_code="EXTRACTION_FAILED"
            )
```

### 4. Configuration Management Service

**New file: `shared/services/configuration.py`**

```python
"""
Unified configuration management service.

Provides centralized access to global and user-specific configurations
with encryption support.
"""

from typing import Any, Dict, Optional
from .base import BaseService, StatelessService, ServiceResult, log_service_call

class ConfigurationService(StatelessService):
    """Service for managing global and user configurations."""
    
    @log_service_call("get_global_config")
    def get_global_config(self, key: str, decrypt: bool = True) -> ServiceResult:
        """Get a global configuration value."""
        try:
            from shared.imports import GlobalConfiguration, decrypt_value_standalone
            from ..database import get_database_session
            
            with get_database_session() as session:
                config = session.query(GlobalConfiguration).filter_by(key=key).first()
                
                if not config:
                    return ServiceResult.error_result(
                        f"Configuration key '{key}' not found",
                        error_code="CONFIG_NOT_FOUND"
                    )
                
                value = config.value
                if decrypt and config.is_encrypted:
                    value = decrypt_value_standalone(value)
                    if value is None:
                        return ServiceResult.error_result(
                            f"Failed to decrypt configuration key '{key}'",
                            error_code="DECRYPT_FAILED"
                        )
                
                return ServiceResult.success_result(
                    data={'key': key, 'value': value, 'is_encrypted': config.is_encrypted}
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get global config '{key}': {e}")
            return ServiceResult.error_result(
                f"Failed to retrieve configuration",
                error_code="CONFIG_RETRIEVAL_FAILED"
            )
    
    @log_service_call("set_global_config")
    def set_global_config(self, key: str, value: str, encrypt: bool = False) -> ServiceResult:
        """Set a global configuration value."""
        try:
            from shared.imports import GlobalConfiguration, encrypt_value
            from ..database import database_session
            
            with database_session() as session:
                config = session.query(GlobalConfiguration).filter_by(key=key).first()
                
                # Encrypt value if requested
                stored_value = encrypt_value(value) if encrypt else value
                
                if config:
                    # Update existing
                    config.value = stored_value
                    config.is_encrypted = encrypt
                    operation = 'updated'
                else:
                    # Create new
                    config = GlobalConfiguration(
                        key=key,
                        value=stored_value,
                        is_encrypted=encrypt
                    )
                    session.add(config)
                    operation = 'created'
                
                return ServiceResult.success_result(
                    data={'key': key, 'operation': operation},
                    metadata={'is_encrypted': encrypt}
                )
                
        except Exception as e:
            self.logger.error(f"Failed to set global config '{key}': {e}")
            return ServiceResult.error_result(
                "Failed to save configuration",
                error_code="CONFIG_SAVE_FAILED"
            )
    
    def get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from configuration."""
        result = self.get_global_config('GEMINI_API_TOKEN', decrypt=True)
        if result.success:
            return result.data['value']
        return None
    
    def get_exchange_rate_api_key(self) -> Optional[str]:
        """Get Exchange Rate API key from configuration."""
        result = self.get_global_config('EXCHANGE_RATE_API_KEY', decrypt=True)
        if result.success:
            return result.data['value']
        return None

class UserConfigurationService(BaseService):
    """Service for managing user-specific configurations."""
    
    def __init__(self, user_id: int, session=None):
        super().__init__(user_id=user_id, session=session)
    
    @log_service_call("get_user_preference")
    def get_user_preference(self, key: str, default: Any = None) -> ServiceResult:
        """Get a user preference value."""
        # Implementation would depend on user preferences model
        # This is a placeholder for future user preference system
        return ServiceResult.success_result(data=default)
    
    @log_service_call("set_user_preference")
    def set_user_preference(self, key: str, value: Any) -> ServiceResult:
        """Set a user preference value."""
        # Implementation would depend on user preferences model
        # This is a placeholder for future user preference system
        return ServiceResult.success_result(data={'key': key, 'value': value})
```

## Implementation Plan

### Phase 1: Create Service Framework (Week 1)

#### Step 1.1: Create Base Service Infrastructure
- [ ] Create `shared/services/` directory structure
- [ ] Implement `shared/services/base.py` with base classes and utilities
- [ ] Create `ServiceResult` standardized response format
- [ ] Add service decorators and error handling

#### Step 1.2: Create Core Services
- [ ] Implement `shared/services/configuration.py` for config management
- [ ] Create `shared/services/encryption.py` wrapper service
- [ ] Add logging and monitoring utilities

#### Step 1.3: Update Shared Imports
- [ ] Add service imports to `shared/imports.py`
- [ ] Ensure graceful fallbacks for missing dependencies
- [ ] Update `__all__` exports

#### Step 1.4: Create Unit Tests
- [ ] Test base service functionality
- [ ] Test service result objects
- [ ] Test error handling and logging
- [ ] Test Flask context integration

### Phase 2: Migrate Email Processing Logic (Week 2)

#### Step 2.1: Create Email Processing Service
- [ ] Implement `shared/services/email.py` with `EmailProcessingService`
- [ ] Consolidate logic from `banktransactions/automation/email_processor.py`
- [ ] Add email parsing service for transaction extraction
- [ ] Include email configuration management

#### Step 2.2: Update Backend Email Routes
- [ ] **`backend/app/email_automation.py`**:
  ```python
  # OLD
  from banktransactions.automation.email_processor import process_user_emails_standalone
  
  # NEW
  from shared.services.email import EmailProcessingService
  
  @email_automation.route("/api/v1/email-automation/trigger", methods=["POST"])
  @api_token_required
  def trigger_email_processing():
      service = EmailProcessingService(user_id=g.current_user.id)
      result = service.process_user_emails()
      
      if result.success:
          return jsonify(result.to_dict()), 200
      else:
          return jsonify(result.to_dict()), 400
  ```

#### Step 2.3: Update Banktransactions Automation
- [ ] **`banktransactions/automation/email_processor.py`**: Use service layer
- [ ] **`banktransactions/core/email_parser.py`**: Migrate to service
- [ ] Update job processing to use unified services

### Phase 3: Create Transaction and User Services (Week 3)

#### Step 3.1: Create Transaction Service
- [ ] **`shared/services/transaction.py`**: Consolidate transaction logic
- [ ] Move logic from `backend/app/transactions_bp/services.py`
- [ ] Add banktransactions-specific transaction processing
- [ ] Include transaction validation and formatting

#### Step 3.2: Create User Management Service
- [ ] **`shared/services/auth.py`**: Consolidate auth logic
- [ ] Move logic from `backend/app/auth_bp/services.py`
- [ ] Add user context management for banktransactions
- [ ] Include API token management

#### Step 3.3: Update Backend Services
- [ ] Update backend service classes to inherit from shared base
- [ ] Migrate to standardized `ServiceResult` responses
- [ ] Add consistent error handling and logging

### Phase 4: Integration and Optimization (Week 4)

#### Step 4.1: Create Integration Utilities
- [ ] **`shared/services/integration.py`**: Cross-module utilities
- [ ] Add job queue management service
- [ ] Create notification and alerting service
- [ ] Add performance monitoring utilities

#### Step 4.2: Update All Route Handlers
- [ ] Update backend routes to use unified services
- [ ] Standardize API response formats using `ServiceResult`
- [ ] Add consistent error handling across all endpoints

#### Step 4.3: Performance and Monitoring
- [ ] Add service performance metrics
- [ ] Implement service health checks
- [ ] Add distributed tracing for cross-service calls
- [ ] Create service dependency mapping

## Migration Strategy

### 1. Backward Compatibility
- Keep existing service classes working during transition
- Add adapter layers for old service interfaces
- Provide migration guides for each service type

### 2. Gradual Migration
- Start with stateless services (configuration, encryption)
- Move to user-context services (email, transactions)
- Finish with complex integration services

### 3. Testing Strategy
- Create comprehensive service layer tests
- Test both Flask and standalone contexts
- Validate API contract compatibility
- Performance testing for service overhead

### 4. Documentation
- Create service layer architecture documentation
- Add usage examples for each service
- Document migration patterns
- Create troubleshooting guides

## Expected Benefits

### 1. Code Quality Improvements
- **Unified Patterns**: Consistent service layer across all modules
- **Better Separation**: Clear separation between business logic and presentation
- **Improved Testing**: Easier to test business logic in isolation
- **Reduced Duplication**: Shared business logic between modules

### 2. Maintenance Benefits
- **Single Source of Truth**: Business logic centralized in services
- **Easier Debugging**: Standardized logging and error handling
- **Simplified Updates**: Changes in one place affect all consumers
- **Better Documentation**: Clear service contracts and interfaces

### 3. Developer Experience
- **Consistent APIs**: Same patterns for all business operations
- **Better Error Messages**: Standardized error handling and reporting
- **Easier Testing**: Mock services for unit testing
- **Clear Architecture**: Well-defined service boundaries

### 4. Performance Benefits
- **Optimized Database Access**: Centralized session management
- **Better Caching**: Service-level caching strategies
- **Reduced Overhead**: Shared service instances
- **Monitoring**: Built-in performance tracking

## Risk Assessment

### Low Risk
- **Gradual Migration**: Can be done incrementally without breaking changes
- **Proven Patterns**: Using established service layer patterns
- **Backward Compatibility**: Old interfaces continue working

### Medium Risk
- **Complex Integration**: Cross-module service calls need careful design
- **Performance Impact**: Service layer adds small overhead
- **Testing Complexity**: Need to test both Flask and standalone contexts

### Mitigation Strategies
- Extensive testing at each migration phase
- Performance benchmarking before and after
- Keep old service implementations as fallback
- Document all changes and provide migration guides

## Success Metrics

### Quantitative Metrics
- [ ] Consolidate 8+ service patterns into unified framework
- [ ] Reduce business logic duplication by 80%
- [ ] Maintain 100% API compatibility during migration
- [ ] Zero performance regression (< 5ms overhead per service call)

### Qualitative Metrics
- [ ] Improved code maintainability and readability
- [ ] Consistent error handling across all modules
- [ ] Simplified testing and debugging
- [ ] Better separation of concerns

## Timeline

- **Week 1**: Service framework and base infrastructure
- **Week 2**: Email processing service migration
- **Week 3**: Transaction and user service migration
- **Week 4**: Integration, optimization, and documentation

**Total Estimated Time**: 4 weeks

## Dependencies

- Completion of shared database utilities (previous plan)
- Coordination with ongoing development work
- Access to test environment for validation

## Documentation Updates

- [ ] Create service layer architecture guide
- [ ] Add service usage examples and patterns
- [ ] Update API documentation with service layer details
- [ ] Create migration guide for developers 