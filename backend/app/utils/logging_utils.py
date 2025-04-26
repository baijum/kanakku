"""
Logging utilities for the Kanakku application.
Provides helper functions for consistent, structured logging across the application.
"""

from flask import current_app, request
import json
from functools import wraps


def log_request(include_headers=False, include_body=False, sanitize_fields=None):
    """
    Log details about an incoming request.

    Args:
        include_headers (bool): Whether to include headers in the log
        include_body (bool): Whether to include the request body
        sanitize_fields (list): List of fields to remove from body before logging
    """
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

    current_app.logger.info(f"Request: {json.dumps(log_data)}")


def log_response(response, include_body=False):
    """
    Log details about an outgoing response.

    Args:
        response: The Flask response object
        include_body (bool): Whether to include the response body
    """
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

    current_app.logger.info(f"Response: {json.dumps(log_data)}")
    return response


def log_function_call(func=None, log_args=False):
    """
    Decorator to log function entry and exit with optional argument logging.

    Args:
        func: The function to decorate
        log_args (bool): Whether to log function arguments
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
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
            current_app.logger.debug(entry_msg)

            try:
                # Execute function
                result = f(*args, **kwargs)
                # Log function exit
                current_app.logger.debug(f"EXIT {module_name}.{function_name}")
                return result
            except Exception as e:
                # Log exception
                current_app.logger.error(
                    f"ERROR in {module_name}.{function_name}: {str(e)}", exc_info=True
                )
                raise

        return wrapper

    # Allow decorator to be used with or without arguments
    if func:
        return decorator(func)
    return decorator


def log_error(error, level="error", include_traceback=True):
    """
    Log an error with optional traceback.

    Args:
        error (Exception): The error to log
        level (str): The log level to use ('error', 'critical', 'warning')
        include_traceback (bool): Whether to include the traceback
    """
    error_type = error.__class__.__name__
    error_msg = str(error)

    # Get the appropriate logger method based on level
    log_method = getattr(current_app.logger, level, current_app.logger.error)

    # Include request info if available
    req_info = ""
    try:
        if request:
            req_info = f" - {request.method} {request.path}"
    except Exception:
        pass

    # Log with or without traceback
    if include_traceback:
        log_method(f"{error_type}: {error_msg}{req_info}", exc_info=True)
    else:
        log_method(f"{error_type}: {error_msg}{req_info}")


def log_db_error(error, operation=None, model=None):
    """
    Log database-related errors with context information.

    Args:
        error (Exception): The database error
        operation (str): The operation being performed (e.g., 'create', 'update')
        model (str): The model/table being operated on
    """
    context = []
    if operation:
        context.append(operation)
    if model:
        context.append(f"on {model}")

    context_str = " ".join(context)
    if context_str:
        context_str = f" during {context_str}"

    current_app.logger.error(
        f"Database error{context_str}: {str(error)}", exc_info=True
    )
