from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import api_token_required, db

from .services import AccountService

accounts_bp = Blueprint("accounts", __name__)


def handle_errors(func):
    """Decorator to provide consistent error handling for account routes."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error in {func.__name__}: {str(e)}", exc_info=True
            )
            return jsonify({"error": "Database error occurred"}), 500
        except Exception as e:
            current_app.logger.error(
                f"Unhandled exception in {func.__name__}: {str(e)}", exc_info=True
            )
            return jsonify({"error": "An unexpected error occurred"}), 500

    return wrapper


@accounts_bp.route("/api/v1/accounts", methods=["GET"])
@api_token_required
@handle_errors
def get_accounts():
    """Get all accounts for the current user and active book."""
    current_app.logger.debug("Entered get_accounts route")

    # Use service layer to get accounts
    account_names = AccountService.get_accounts(include_details=False)

    # Return in format expected by AddTransaction.js
    return jsonify({"accounts": account_names})


@accounts_bp.route("/api/v1/accounts/details", methods=["GET"])
@api_token_required
@handle_errors
def get_accounts_details():
    """Get all accounts with full details for the current user and active book."""
    current_app.logger.debug("Entered get_accounts_details route")

    # Use service layer to get account details
    account_details = AccountService.get_accounts(include_details=True)

    return jsonify(account_details)


@accounts_bp.route("/api/v1/accounts", methods=["POST"])
@api_token_required
@handle_errors
def create_account():
    """Create a new account in the active book."""
    current_app.logger.debug("Entered create_account route")

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request must be valid JSON"}), 400

    # Use service layer to create account
    success, message, account = AccountService.create_account(data)

    if not success:
        return jsonify({"error": message}), 400

    return jsonify({"message": message, "account": account.to_dict()}), 201


@accounts_bp.route("/api/v1/accounts/<int:account_id>", methods=["GET"])
@api_token_required
@handle_errors
def get_account(account_id):
    """Get a specific account."""
    current_app.logger.debug(f"Entered get_account route for ID: {account_id}")

    # Use service layer to get account
    account = AccountService.get_account_by_id(account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account.to_dict())


@accounts_bp.route("/api/v1/accounts/<int:account_id>", methods=["PUT"])
@api_token_required
@handle_errors
def update_account(account_id):
    """Update an account."""
    current_app.logger.debug(f"Entered update_account route for ID: {account_id}")

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request must be valid JSON"}), 400

    # Use service layer to update account
    success, message, account = AccountService.update_account(account_id, data)

    if not success:
        if "not found" in message.lower():
            return jsonify({"error": message}), 404
        return jsonify({"error": message}), 400

    return jsonify({"message": message, "account": account.to_dict()})


@accounts_bp.route("/api/v1/accounts/<int:account_id>", methods=["DELETE"])
@api_token_required
@handle_errors
def delete_account(account_id):
    """Delete an account."""
    current_app.logger.debug(f"Entered delete_account route for ID: {account_id}")

    # Use service layer to delete account
    success, message = AccountService.delete_account(account_id)

    if not success:
        if "not found" in message.lower():
            return jsonify({"error": message}), 404
        return jsonify({"error": message}), 400

    return jsonify({"message": message})


@accounts_bp.route("/api/v1/accounts/autocomplete", methods=["GET"])
@api_token_required
@handle_errors
def autocomplete_accounts():
    """Get account names for auto-completion based on a prefix."""
    current_app.logger.debug("Entered autocomplete_accounts route")

    prefix = request.args.get("prefix", "").strip()
    limit = request.args.get("limit", 20, type=int)

    # Use service layer to get autocomplete suggestions
    suggestions, prefix = AccountService.autocomplete_accounts(prefix, limit)

    return jsonify({"suggestions": suggestions, "prefix": prefix})
