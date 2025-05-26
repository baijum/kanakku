# Debug Logging Improvements for Kanakku Backend

## Overview

This document summarizes the comprehensive debug logging improvements made to the Kanakku backend application. The enhancements provide detailed visibility into application operations when `LOG_LEVEL=DEBUG` is set.

## Enhanced Logging Utilities

### New Functions Added to `app/utils/logging_utils.py`

1. **`log_debug(message, extra_data=None, module_name=None)`**
   - Structured debug logging with optional JSON data
   - Module name context for better traceability

2. **`log_service_entry(service_name, method_name, **kwargs)`**
   - Logs service method entry with sanitized parameters
   - Automatically redacts sensitive data (passwords, tokens, etc.)

3. **`log_service_exit(service_name, method_name, result_summary=None)`**
   - Logs service method exit with optional result summary

4. **`log_database_operation(operation, model, record_id=None, extra_data=None)`**
   - Specialized logging for database operations (CREATE, READ, UPDATE, DELETE)

5. **`log_api_call(endpoint, method, user_id=None, extra_data=None)`**
   - Logs API endpoint calls with user context

6. **`log_business_logic(operation, details=None, extra_data=None, module_name=None)`**
   - Logs business logic operations and decisions

7. **`debug_timer(name)`**
   - Context manager for timing operations
   - Usage: `with debug_timer("operation_name"): ...`

### Enhanced Existing Functions

- **`log_function_call()`**: Added timing and result logging
- **`log_error()`**: Added module name context
- **`log_db_error()`**: Added record ID parameter
- **`get_logger()`**: Added fallback for outside application context

## Enhanced Base Service Class

### `app/shared/services.py` - BaseService Class

Added comprehensive logging methods:

- **`get_service_name()`**: Returns service class name for logging
- **`log_entry()`**: Wrapper for service entry logging
- **`log_exit()`**: Wrapper for service exit logging
- **`log_debug()`**: Service-specific debug logging

Enhanced existing methods with debug logging:
- `commit_or_rollback()`: Database commit/rollback operations
- `safe_get_by_id()`: Model retrieval with ownership checks
- `safe_delete()`: Model deletion operations
- `paginate_query()`: Query pagination

## Modules Enhanced with Debug Logging

### 1. User Model (`app/models/user.py`)

Added debug logging to all user operations:
- Password setting and verification
- Account activation/deactivation
- Password reset token generation and verification
- JWT token generation
- User dictionary conversion

### 2. Gmail Message Service (`app/services/gmail_message_service.py`)

Comprehensive logging for:
- Loading processed message IDs
- Saving single/multiple message IDs
- Checking message processing status
- Getting message counts
- Clearing processed messages

### 3. Email Automation (`app/email_automation.py`)

Added logging for:
- Configuration retrieval and management
- Email configuration CRUD operations
- Service layer vs. fallback logic decisions
- Validation failures and successes

### 4. Settings Management (`app/settings.py`)

Enhanced logging for:
- Global configuration operations
- Admin access control checks
- Encryption/decryption operations
- Configuration validation

### 5. Account Service (`app/accounts_bp/services.py`)

Comprehensive service logging for:
- Account retrieval (list and by ID)
- Account creation with validation
- Account updates with conflict checking
- Account deletion with transaction checks
- Account autocomplete functionality

## Shared Service Enhancements

### `app/shared/services.py` Utility Functions

Enhanced with debug logging:
- `validate_date_range()`: Date validation operations
- `sanitize_search_term()`: Search term processing
- `calculate_pagination_metadata()`: Pagination calculations
- `get_active_book_id()`: Active book determination

## Log Output Examples

### Service Entry/Exit Logging
```
[2024-01-15 10:30:45] [DEBUG] [req-12345] AccountService: ENTER get_accounts | Data: {"include_details": true}
[2024-01-15 10:30:45] [DEBUG] [req-12345] AccountService: Querying accounts for user and active book | Data: {"user_id": 1, "active_book_id": 1}
[2024-01-15 10:30:45] [DEBUG] [req-12345] AccountService: EXIT get_accounts | Result: returned 5 detailed accounts
```

### Database Operations
```
[2024-01-15 10:30:46] [DEBUG] [req-12345] DatabaseOp: DB CREATE on Account (ID: 123) | Data: {"name": "Checking Account", "currency": "USD"}
[2024-01-15 10:30:46] [DEBUG] [req-12345] BaseService: Database commit successful
```

### API Calls
```
[2024-01-15 10:30:47] [DEBUG] [req-12345] API: API POST /api/v1/accounts (User: 1) | Data: {"operation": "create_account"}
```

### Business Logic
```
[2024-01-15 10:30:48] [DEBUG] [req-12345] AccountService: BUSINESS: Account created successfully | Data: {"account_id": 123, "account_name": "Checking Account"}
```

## Configuration

### Environment Variables

Set `LOG_LEVEL=DEBUG` to enable debug logging:

```bash
# In .env file
LOG_LEVEL=DEBUG

# Or as environment variable
export LOG_LEVEL=DEBUG
```

### Log Files

Debug logs are written to:
- **Console**: Respects LOG_LEVEL setting
- **logs/kanakku.log**: All application logs (INFO and above)
- **logs/error.log**: Error logs only (ERROR and above)

## Testing Debug Logging

### Test Script

Run the provided test script to verify debug logging:

```bash
python test_debug_logging.py
```

### Manual Testing

1. Set `LOG_LEVEL=DEBUG` in your environment
2. Start the Flask application
3. Make API calls to see debug output
4. Check log files for persistent logging

## Benefits

### For Development
- **Detailed Traceability**: Track request flow through services
- **Parameter Visibility**: See method inputs and outputs
- **Performance Monitoring**: Timing information for operations
- **Error Context**: Rich error information with context

### For Debugging
- **Service Boundaries**: Clear entry/exit points
- **Data Flow**: See how data transforms through the system
- **Database Operations**: Track all database interactions
- **Business Logic**: Understand decision points

### For Monitoring
- **Structured Data**: JSON-formatted extra data for parsing
- **Module Context**: Know which component generated each log
- **Request Correlation**: Request IDs tie related log entries together
- **Security Auditing**: Track authentication and authorization events

## Security Considerations

- **Sensitive Data Redaction**: Passwords, tokens, and secrets are automatically redacted
- **Production Use**: Only enable DEBUG logging temporarily in production
- **Log Rotation**: Logs are automatically rotated to prevent disk space issues
- **Access Control**: Log files should have appropriate file permissions

## Future Enhancements

Potential areas for further logging improvements:
1. **Transaction Processing**: Enhanced logging for financial operations
2. **Report Generation**: Detailed logging for report creation
3. **Email Processing**: More granular email automation logging
4. **Performance Metrics**: Additional timing and performance data
5. **Integration Points**: Enhanced logging for external service calls

## Conclusion

The debug logging improvements provide comprehensive visibility into the Kanakku backend operations. When `LOG_LEVEL=DEBUG` is enabled, developers and operators can:

- Track request flows through the entire application
- Debug issues with detailed context and timing information
- Monitor application performance and identify bottlenecks
- Audit security-related operations
- Understand business logic execution paths

The structured logging format makes it easy to parse logs programmatically for monitoring and alerting systems. 