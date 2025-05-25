from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def not_found_error(error):
    current_app.logger.info(
        f"Not found error: {request.method} {request.path} - {error}"
    )
    return jsonify({"error": "Not Found"}), 404


@errors.app_errorhandler(500)
def internal_error(error):
    # Log the full traceback for internal errors
    current_app.logger.error(
        f"Internal server error: {request.method} {request.path} - {error}",
        exc_info=True,
    )

    # Rollback any failed database transactions
    db.session.rollback()

    # Return a generic error to avoid exposing sensitive information
    return jsonify({"error": "Internal Server Error"}), 500


@errors.app_errorhandler(405)
def method_not_allowed_error(error):
    current_app.logger.warning(
        f"Method not allowed: {request.method} {request.path} - Allowed methods: {error.valid_methods}"
    )
    return jsonify({"error": "Method Not Allowed"}), 405


@errors.app_errorhandler(SQLAlchemyError)
def database_error(error):
    # Log database errors with full traceback
    current_app.logger.error(
        f"Database error: {request.method} {request.path} - {str(error)}", exc_info=True
    )

    # Rollback the session
    db.session.rollback()

    return (
        jsonify({"error": "Database Error", "message": "A database error occurred"}),
        500,
    )


@errors.app_errorhandler(ValueError)
def value_error(error):
    # Log validation errors
    current_app.logger.warning(
        f"Value error: {request.method} {request.path} - {str(error)}"
    )

    return jsonify({"error": "Invalid Input", "message": str(error)}), 400


@errors.app_errorhandler(Exception)
def unhandled_exception(error):
    # Catch-all handler for all other exceptions
    # This should be the last error handler
    current_app.logger.critical(
        f"Unhandled exception: {request.method} {request.path} - {error.__class__.__name__}: {str(error)}",
        exc_info=True,
    )

    # Rollback any failed database transactions
    try:
        db.session.rollback()
    except Exception:
        pass

    return jsonify({"error": "Internal Server Error"}), 500


# Add a test route to trigger an error
@errors.route("/api/test/error")
def trigger_error():
    current_app.logger.info("Test error endpoint called")
    raise Exception("This is a test exception")


# Add a test route to trigger a database error
@errors.route("/api/test/db-error")
def trigger_db_error():
    current_app.logger.info("Test database error endpoint called")
    raise SQLAlchemyError("This is a test database error")
