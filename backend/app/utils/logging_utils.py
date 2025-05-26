"""
Logging utilities for the Kanakku application.
Provides helper functions for consistent, structured logging across the application.
"""

import json
import time
from functools import wraps
from typing import Any, Dict, Optional

from flask import current_app, g, request


def get_logger():
    """Get the current app logger with fallback."""
    try:
        return current_app.logger
    except RuntimeError:
        # Fallback for when we're outside application context
        import logging

        return logging.getLogger(__name__)


def log_debug(
    message: str, extra_data: Optional[Dict] = None, module_name: Optional[str] = None
):
    """
    Log a debug message with optional structured data.

    Args:
        message (str): The debug message
        extra_data (dict): Additional structured data to include
        module_name (str): Name of the module/service for context
    """
    logger = get_logger()

    # Build the log message
    log_msg = message
    if module_name:
        log_msg = f"[{module_name}] {log_msg}"

    # Add extra data if provided
    if extra_data:
        try:
            log_msg += f" | Data: {json.dumps(extra_data, default=str)}"
        except Exception:
            log_msg += f" | Data: {str(extra_data)}"

    logger.debug(log_msg)


def log_service_entry(service_name: str, method_name: str, **kwargs):
    """
    Log entry into a service method with parameters.

    Args:
        service_name (str): Name of the service
        method_name (str): Name of the method
        **kwargs: Method parameters to log (sensitive data will be redacted)
    """
    # Sanitize sensitive parameters
    safe_kwargs = {}
    sensitive_keys = ["password", "token", "secret", "key", "auth"]

    for key, value in kwargs.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_kwargs[key] = "[REDACTED]"
        else:
            safe_kwargs[key] = value

    log_debug(f"ENTER {method_name}", extra_data=safe_kwargs, module_name=service_name)


def log_service_exit(
    service_name: str, method_name: str, result_summary: Optional[str] = None
):
    """
    Log exit from a service method with optional result summary.

    Args:
        service_name (str): Name of the service
        method_name (str): Name of the method
        result_summary (str): Brief summary of the result
    """
    message = f"EXIT {method_name}"
    if result_summary:
        message += f" | Result: {result_summary}"

    log_debug(message, module_name=service_name)


def log_database_operation(
    operation: str,
    model: str,
    record_id: Optional[Any] = None,
    extra_data: Optional[Dict] = None,
):
    """
    Log database operations for debugging.

    Args:
        operation (str): The database operation (CREATE, READ, UPDATE, DELETE)
        model (str): The model/table name
        record_id: The ID of the record being operated on
        extra_data (dict): Additional data about the operation
    """
    message = f"DB {operation} on {model}"
    if record_id:
        message += f" (ID: {record_id})"

    log_debug(message, extra_data=extra_data, module_name="DatabaseOp")


def log_api_call(
    endpoint: str,
    method: str,
    user_id: Optional[int] = None,
    extra_data: Optional[Dict] = None,
):
    """
    Log API endpoint calls for debugging.

    Args:
        endpoint (str): The API endpoint
        method (str): HTTP method
        user_id (int): ID of the user making the call
        extra_data (dict): Additional request data
    """
    message = f"API {method} {endpoint}"
    if user_id:
        message += f" (User: {user_id})"

    log_debug(message, extra_data=extra_data, module_name="API")


def log_business_logic(
    operation: str,
    details: Optional[str] = None,
    extra_data: Optional[Dict] = None,
    module_name: Optional[str] = None,
):
    """
    Log business logic operations for debugging.

    Args:
        operation (str): The business operation being performed
        details (str): Additional details about the operation
        extra_data (dict): Structured data related to the operation
        module_name (str): Name of the module/service
    """
    message = f"BUSINESS: {operation}"
    if details:
        message += f" - {details}"

    log_debug(message, extra_data=extra_data, module_name=module_name)


def log_request(include_headers=False, include_body=False, sanitize_fields=None):
    """
    Log details about an incoming request.

    Args:
        include_headers (bool): Whether to include headers in the log
        include_body (bool): Whether to include the request body
        sanitize_fields (list): List of fields to remove from body before logging
    """
    logger = get_logger()

    log_data = {
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
    }

    # Add query parameters if present
    if request.args:
        log_data["query_params"] = dict(request.args)

    # Add headers if requested
    if include_headers:
        # Convert headers to dict and filter sensitive headers
        headers = dict(request.headers)
        for sensitive_header in ["Authorization", "Cookie", "X-Auth-Token"]:
            if sensitive_header in headers:
                headers[sensitive_header] = "[REDACTED]"
        log_data["headers"] = headers

    # Add body if requested
    if include_body and request.is_json:
        try:
            body = request.get_json(silent=True) or {}
            # Sanitize sensitive fields
            if sanitize_fields and isinstance(body, dict):
                for field in sanitize_fields:
                    if field in body:
                        body[field] = "[REDACTED]"
            log_data["body"] = body
        except Exception:
            log_data["body"] = "[Error parsing JSON body]"

    logger.info(f"Request: {json.dumps(log_data)}")


def log_response(response, include_body=False):
    """
    Log details about an outgoing response.

    Args:
        response: The Flask response object
        include_body (bool): Whether to include the response body
    """
    logger = get_logger()

    log_data = {
        "status_code": response.status_code,
        "path": request.path,
        "method": request.method,
    }

    # Add response body for non-binary content if requested
    if include_body and response.is_json:
        try:
            data = json.loads(response.get_data(as_text=True))
            log_data["body"] = data
        except Exception:
            log_data["body"] = "[Error parsing JSON response]"

    logger.info(f"Response: {json.dumps(log_data)}")
    return response


def log_function_call(func=None, log_args=False, log_result=False):
    """
    Decorator to log function entry and exit with optional argument and result logging.

    Args:
        func: The function to decorate
        log_args (bool): Whether to log function arguments
        log_result (bool): Whether to log function result
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            function_name = f.__name__
            module_name = f.__module__

            # Log function entry
            entry_msg = f"ENTER {module_name}.{function_name}"
            if log_args:
                # Filter out any sensitive arguments
                safe_kwargs = {
                    k: (v if k not in ["password", "token", "secret"] else "[REDACTED]")
                    for k, v in kwargs.items()
                }
                entry_msg += f" args={args}, kwargs={safe_kwargs}"
            logger.debug(entry_msg)

            start_time = time.time()
            try:
                # Execute function
                result = f(*args, **kwargs)

                # Log function exit with timing
                duration = time.time() - start_time
                exit_msg = f"EXIT {module_name}.{function_name} (took {duration:.3f}s)"
                if log_result and result is not None:
                    # Safely convert result to string, truncating if too long
                    result_str = str(result)
                    if len(result_str) > 200:
                        result_str = result_str[:200] + "..."
                    exit_msg += f" result={result_str}"
                logger.debug(exit_msg)

                return result
            except Exception as e:
                # Log exception with timing
                duration = time.time() - start_time
                logger.error(
                    f"ERROR in {module_name}.{function_name} (after {duration:.3f}s): {str(e)}",
                    exc_info=True,
                )
                raise

        return wrapper

    # Allow decorator to be used with or without arguments
    if func:
        return decorator(func)
    return decorator


def log_error(error, level="error", include_traceback=True, module_name=None):
    """
    Log an error with optional traceback.

    Args:
        error (Exception): The error to log
        level (str): The log level to use ('error', 'critical', 'warning')
        include_traceback (bool): Whether to include the traceback
        module_name (str): Name of the module where error occurred
    """
    logger = get_logger()
    error_type = error.__class__.__name__
    error_msg = str(error)

    # Get the appropriate logger method based on level
    log_method = getattr(logger, level, logger.error)

    # Include request info if available
    req_info = ""
    try:
        if request:
            req_info = f" - {request.method} {request.path}"
    except Exception:
        pass

    # Include module info if provided
    module_info = f"[{module_name}] " if module_name else ""

    # Log with or without traceback
    if include_traceback:
        log_method(f"{module_info}{error_type}: {error_msg}{req_info}", exc_info=True)
    else:
        log_method(f"{module_info}{error_type}: {error_msg}{req_info}")


def log_db_error(error, operation=None, model=None, record_id=None):
    """
    Log database-related errors with context information.

    Args:
        error (Exception): The database error
        operation (str): The operation being performed (e.g., 'create', 'update')
        model (str): The model/table being operated on
        record_id: The ID of the record being operated on
    """
    logger = get_logger()
    context = []
    if operation:
        context.append(operation)
    if model:
        context.append(f"on {model}")
    if record_id:
        context.append(f"(ID: {record_id})")

    context_str = " ".join(context)
    if context_str:
        context_str = f" during {context_str}"

    logger.error(f"Database error{context_str}: {str(error)}", exc_info=True)


def debug_timer(name: str):
    """
    Context manager for timing operations and logging the duration.

    Usage:
        with debug_timer("expensive_operation"):
            # do something expensive
            pass
    """

    class DebugTimer:
        def __init__(self, operation_name):
            self.name = operation_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            log_debug(f"TIMER START: {self.name}")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            log_debug(f"TIMER END: {self.name} (took {duration:.3f}s)")

    return DebugTimer(name)
