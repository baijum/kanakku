# Unified Service Layer

This directory contains the unified service layer implementation for the Kanakku project, providing consistent service patterns across backend and banktransactions modules.

## Overview

The unified service layer consolidates business logic from both the Flask backend and banktransactions processing modules into a single, reusable service framework. This implementation follows the plan outlined in `.plan/unified-service-layer-plan.md`.

## Architecture

### Base Classes

#### `BaseService`
- **Purpose**: Base class for services that require user context
- **Features**: 
  - User ID management and validation
  - Database session handling with transaction scope
  - Standardized logging and operation tracking
  - User access validation

#### `StatelessService`
- **Purpose**: Base class for services that don't require user context
- **Features**:
  - Standardized logging
  - Operation tracking
  - No user context dependencies

#### `ServiceResult`
- **Purpose**: Standardized response format for all service operations
- **Features**:
  - Success/error state management
  - Structured data and metadata
  - Consistent error codes
  - Timestamp tracking
  - API-ready serialization

### Service Decorators

#### `@require_user_context`
Ensures that service methods have valid user context before execution.

#### `@log_service_call(operation_name)`
Automatically logs service method calls with success/error tracking.

## Available Services

### 1. Configuration Services

#### `ConfigurationService` (Stateless)
Manages global and user-specific configurations with encryption support.

**Key Methods:**
- `get_global_config(key, decrypt=True)` - Retrieve global configuration
- `set_global_config(key, value, encrypt=False)` - Set global configuration
- `get_gemini_api_key()` - Get Gemini API key
- `get_exchange_rate_api_key()` - Get Exchange Rate API key

**Usage:**
```python
from shared.services import ConfigurationService

config_service = ConfigurationService()
result = config_service.get_global_config('GEMINI_API_TOKEN')
if result.success:
    api_key = result.data['value']
```

#### `UserConfigurationService` (User Context Required)
Manages user-specific preferences and settings.

### 2. Encryption Service

#### `EncryptionService` (Stateless)
Provides unified encryption/decryption operations.

**Key Methods:**
- `encrypt_value(value)` - Encrypt a value
- `decrypt_value(encrypted_value)` - Decrypt a value
- `encrypt_string(value)` - Convenience method returning string directly
- `decrypt_string(encrypted_value)` - Convenience method returning string directly

**Usage:**
```python
from shared.services import EncryptionService

encryption_service = EncryptionService()
result = encryption_service.encrypt_value("sensitive_data")
if result.success:
    encrypted_value = result.data['encrypted_value']
```

### 3. Email Processing Services

#### `EmailProcessingService` (User Context Required)
Consolidates email automation logic from both backend and banktransactions modules.

**Key Methods:**
- `process_user_emails()` - Process emails for current user
- `get_email_configuration()` - Get user's email config
- `update_email_configuration(config_data)` - Update email config
- `test_email_connection(credentials)` - Test email connection

**Usage:**
```python
from shared.services import EmailProcessingService

email_service = EmailProcessingService(user_id=123)
result = email_service.process_user_emails()
if result.success:
    processed_count = result.metadata['processed_count']
```

#### `EmailParsingService` (Stateless)
Handles transaction detail extraction from email content.

**Key Methods:**
- `extract_transaction_details(email_body)` - Extract transaction details

### 4. Transaction Service

#### `TransactionService` (User Context Required)
Unified service for transaction processing and management.

**Key Methods:**
- `create_transaction(transaction_data)` - Create new transaction
- `get_transaction(transaction_id)` - Get transaction by ID
- `update_transaction(transaction_id, update_data)` - Update transaction
- `delete_transaction(transaction_id)` - Delete transaction
- `list_transactions(filters, page, per_page)` - List transactions with pagination
- `process_email_transaction(email_data)` - Process transaction from email

**Usage:**
```python
from shared.services import TransactionService

transaction_service = TransactionService(user_id=123)
result = transaction_service.create_transaction({
    'amount': '100.50',
    'description': 'Test transaction',
    'account_id': 456
})
if result.success:
    transaction_id = result.metadata['transaction_id']
```

### 5. Authentication Services

#### `AuthService` (Stateless)
Unified authentication and user management.

**Key Methods:**
- `authenticate_user(email, password, remote_ip)` - Authenticate user
- `create_user(email, password, name)` - Create new user
- `get_user_by_id(user_id)` - Get user by ID
- `get_user_by_email(email)` - Get user by email
- `update_user_password(user_id, new_password)` - Update password
- `generate_access_token(user_id)` - Generate JWT token

**Usage:**
```python
from shared.services import AuthService

auth_service = AuthService()
result = auth_service.authenticate_user('user@example.com', 'password123')
if result.success:
    user_data = result.data
```

#### `UserManagementService` (User Context Required)
User management operations requiring user context.

**Key Methods:**
- `update_profile(profile_data)` - Update user profile
- `get_user_tokens()` - Get user's API tokens
- `create_api_token(name, description, expires_at)` - Create API token
- `revoke_api_token(token_id)` - Revoke API token

## Usage Patterns

### 1. Service Instantiation

**With User Context:**
```python
from shared.services import TransactionService, UserManagementService

# For operations requiring user context
transaction_service = TransactionService(user_id=123)
user_service = UserManagementService(user_id=123)
```

**Without User Context:**
```python
from shared.services import AuthService, ConfigurationService

# For stateless operations
auth_service = AuthService()
config_service = ConfigurationService()
```

### 2. Error Handling

All services return `ServiceResult` objects with consistent error handling:

```python
result = service.some_operation(data)

if result.success:
    # Handle success
    data = result.data
    metadata = result.metadata
else:
    # Handle error
    error_message = result.error
    error_code = result.error_code
    timestamp = result.timestamp
```

### 3. API Integration

Services are designed to work seamlessly with Flask routes:

```python
@app.route('/api/v1/transactions', methods=['POST'])
@api_token_required
def create_transaction():
    service = TransactionService(user_id=g.current_user.id)
    result = service.create_transaction(request.get_json())
    
    if result.success:
        return jsonify(result.to_dict()), 201
    else:
        return jsonify(result.to_dict()), 400
```

### 4. Standalone Usage

Services can also be used in standalone contexts (like banktransactions):

```python
from shared.services import EmailProcessingService

def process_user_emails_job(user_id):
    service = EmailProcessingService(user_id=user_id)
    result = service.process_user_emails()
    
    if result.success:
        return result.data
    else:
        raise Exception(f"Email processing failed: {result.error}")
```

## Benefits

### 1. Consistency
- Unified patterns across all modules
- Standardized error handling and logging
- Consistent API response formats

### 2. Reusability
- Services can be used in both Flask and standalone contexts
- Shared business logic between modules
- Reduced code duplication

### 3. Maintainability
- Single source of truth for business logic
- Easier debugging with standardized logging
- Clear separation of concerns

### 4. Testing
- Services can be easily mocked and tested in isolation
- Comprehensive test coverage with consistent patterns
- Better unit testing capabilities

### 5. Scalability
- Modular architecture supports growth
- Easy to add new services following established patterns
- Better performance monitoring and optimization

## Migration Strategy

The unified service layer is designed for gradual migration:

1. **Backward Compatibility**: Existing code continues to work
2. **Incremental Adoption**: Services can be adopted one at a time
3. **Fallback Support**: Services gracefully handle missing dependencies

## Testing

The service layer includes comprehensive tests in `shared/test_services.py`:

- Base service functionality tests
- Service result object tests
- Error handling and logging tests
- Individual service tests for all major operations

Run tests with:
```bash
python -m pytest shared/test_services.py -v
```

## Future Enhancements

Potential areas for future development:

1. **Caching Layer**: Add Redis-based caching for frequently accessed data
2. **Async Support**: Add async/await support for I/O operations
3. **Dependency Injection**: Implement DI container for better service management
4. **Performance Monitoring**: Add built-in performance metrics and tracing
5. **Service Health Checks**: Implement health check endpoints for services

## Contributing

When adding new services:

1. Follow the established patterns using `BaseService` or `StatelessService`
2. Use `ServiceResult` for all return values
3. Add appropriate decorators (`@require_user_context`, `@log_service_call`)
4. Include comprehensive tests
5. Update this README with new service documentation
6. Add imports to `shared/services/__init__.py` and `shared/imports.py`

## Dependencies

The service layer depends on:

- `shared.database` - Database session management
- `shared.imports` - Centralized imports for models and utilities
- Backend models and utilities (graceful fallback if not available)
- Banktransactions modules (graceful fallback if not available) 