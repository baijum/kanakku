# Kanakku Backend Logging System

This document describes the logging system implemented in the Kanakku backend application.

## Overview

The logging system provides structured logs with the following features:
- Request ID tracking for correlating log entries across a request lifecycle
- Different log levels for various severity of events
- Rotating file logs to avoid excessive disk usage
- Separate error logs for easier debugging
- Console logging for development
- Structured logging format with timestamps and context

## Log Files

Logs are stored in the `logs/` directory:
- `kanakku.log` - Contains all logs (INFO level and above)
- `error.log` - Contains only error logs (ERROR level and above)

Both files use a rotating file handler that keeps the files at a maximum size of 10MB with 5 backup files.

## Log Format

Each log entry follows this format:
```
[timestamp] [level] [request_id] module: message
```

Example:
```
[2025-04-15 12:34:56] [INFO] [b0d51c8a-f3e8-4e2c-9c19-c8e4cd0ed3a1] auth: Login successful for user: user@example.com
```

## Request ID Tracking

Each HTTP request is assigned a unique request ID (UUID) that is included in all log entries generated during that request's lifecycle. This makes it easy to trace all actions related to a single request.

## Utils Package Structure

The utilities for the application are organized in the `app/utils` package:

```
app/utils/
├── __init__.py           # Package initialization, imports utilities for easy access
├── email_utils.py        # Email-related utility functions
└── logging_utils.py      # Logging utility functions
```

The `__init__.py` file imports key utilities to provide backward compatibility and easy access from `app.utils` directly.

## Utility Functions

The `app/utils/logging_utils.py` module provides helper functions for common logging patterns:

### `log_request(include_headers=False, include_body=False, sanitize_fields=None)`
Logs details about an incoming request, with options to include headers and body.

### `log_response(response, include_body=False)`
Logs details about an outgoing response, with option to include the response body.

### `log_function_call(func=None, log_args=False)`
Decorator to log function entry and exit, with option to include arguments.

### `log_error(error, level='error', include_traceback=True)`
Logs an error with optional traceback and configurable log level.

### `log_db_error(error, operation=None, model=None)`
Specialized function to log database errors with context about the operation and model.

## Usage Examples

### Basic Logging
```python
from flask import current_app

# Informational logs
current_app.logger.info("User profile updated successfully")

# Warning logs
current_app.logger.warning("Rate limit approaching for user")

# Error logs
current_app.logger.error("Database connection failed", exc_info=True)
```

### Using Utilities
```python
# Import directly from the utils package
from app.utils import log_function_call, log_error

# Or import from specific modules
from app.utils.logging_utils import log_function_call

# Log a function call with arguments
@log_function_call(log_args=True)
def process_payment(user_id, amount):
    # function code here
    pass

# Log an error with context
try:
    # Some code that might fail
    pass
except Exception as e:
    log_error(e, level='critical')
```

### Error Handling Decorator
```python
from app.utils.logging_utils import handle_errors
from flask import Blueprint

bp = Blueprint('example', __name__)

@bp.route('/example')
@handle_errors
def example_route():
    # This route is automatically wrapped with error handling and logging
    pass
```

## Best Practices

1. Always include context in log messages (e.g., user ID, transaction ID)
2. Use appropriate log levels:
   - DEBUG: Detailed information for debugging
   - INFO: Confirmation that things are working as expected
   - WARNING: Something unexpected happened, but the application continues
   - ERROR: Something failed, but the application can recover
   - CRITICAL: A serious error that may prevent the application from continuing

3. Never log sensitive information (passwords, tokens, etc.)
4. For exceptions, include the traceback with `exc_info=True`
5. Wrap complex operations in try/except blocks with appropriate logging

## Configuration

The logging configuration is defined in `app/__init__.py` in the `setup_logging()` function. This can be adjusted to change log levels, formats, or add additional handlers as needed. 