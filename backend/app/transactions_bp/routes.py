import json
import traceback
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import api_token_required, db

from .services import TransactionService

transactions_bp = Blueprint("transactions", __name__)


def handle_errors(func):
    """Decorator to provide consistent error handling for transaction routes."""

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


@transactions_bp.route("/api/v1/transactions", methods=["POST"])
@api_token_required
@handle_errors
def create_transaction():
    """Create a new transaction from the provided JSON data."""
    current_app.logger.info("Processing transaction creation request")

    try:
        # Parse and validate the request data
        data = request.get_json()
        if data is None:
            current_app.logger.warning(f"Failed to parse JSON data: {request.data}")
            return jsonify({"error": "Request must be valid JSON"}), 400

        # Log sanitized data (remove sensitive info if any)
        log_data = data.copy() if data else {}
        current_app.logger.debug(f"Transaction data: {json.dumps(log_data)}")

        # Use service layer to create transaction
        success, message, transactions = TransactionService.create_transaction(data)

        if not success:
            # Return 404 for account not found errors, 400 for other validation errors
            if "account not found" in message.lower():
                return jsonify({"error": message}), 404
            return jsonify({"error": message}), 400

        # Prepare response
        response_data = {
            "message": message,
            "transactions": [tx.to_dict() for tx in transactions],
        }

        return jsonify(response_data), 201

    except Exception as e:
        current_app.logger.error(
            f"Unhandled error in create_transaction: {str(e)}", exc_info=True
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions_bp.route("/api/v1/transactions", methods=["GET"])
@api_token_required
@handle_errors
def get_transactions():
    """Get transactions with filtering and pagination."""
    current_app.logger.debug("Entered get_transactions route")

    try:
        # Parse query parameters
        limit = request.args.get("limit", type=int)
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")
        search_term = request.args.get("search", "").strip()
        offset = request.args.get("offset", type=int, default=0)

        # Log request
        current_app.logger.debug(
            f"GET /api/v1/transactions request with params: {request.args}"
        )

        # Use service layer to get transactions
        formatted_transactions, total_count = TransactionService.get_transactions(
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term,
            offset=offset,
        )

        # Return in the format expected by the frontend
        response = {"transactions": formatted_transactions, "total": total_count}
        return jsonify(response)

    except Exception as e:
        current_app.logger.error(
            f"Error in get_transactions: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "Failed to retrieve transactions"}), 500


@transactions_bp.route("/api/v1/transactions/<int:transaction_id>", methods=["GET"])
@api_token_required
@handle_errors
def get_transaction(transaction_id):
    """Get a single transaction by ID."""
    current_app.logger.debug(f"GET /api/v1/transactions/{transaction_id}")

    # Use service layer to get transaction
    transaction_data = TransactionService.get_transaction_by_id(transaction_id)

    if not transaction_data:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify(transaction_data), 200


@transactions_bp.route("/api/v1/transactions/<int:transaction_id>", methods=["PUT"])
@api_token_required
@handle_errors
def update_transaction(transaction_id):
    """Update a single transaction."""
    current_app.logger.debug(f"PUT /api/v1/transactions/{transaction_id}")

    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Request must be valid JSON"}), 400

        # Use service layer to update transaction
        success, message, transaction = TransactionService.update_transaction(
            transaction_id, data
        )

        if not success:
            if "not found" in message.lower():
                return jsonify({"error": message}), 404
            return jsonify({"error": message}), 400

        return jsonify({"message": message, "transaction": transaction.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(
            f"Unhandled error in update_transaction: {str(e)}", exc_info=True
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions_bp.route(
    "/api/v1/transactions/<int:transaction_id>/update_with_postings", methods=["PUT"]
)
@api_token_required
@handle_errors
def update_transaction_with_postings(transaction_id):
    """Update a transaction with multiple postings."""
    current_app.logger.debug(
        f"PUT /api/v1/transactions/{transaction_id}/update_with_postings"
    )

    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Request must be valid JSON"}), 400

        # Use service layer to update transaction with postings
        success, message, transactions = (
            TransactionService.update_transaction_with_postings(transaction_id, data)
        )

        if not success:
            if "not found" in message.lower():
                return jsonify({"error": message}), 404
            return jsonify({"error": message}), 400

        return (
            jsonify(
                {
                    "message": message,
                    "transactions": [tx.to_dict() for tx in transactions],
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(
            f"Unhandled error in update_transaction_with_postings: {str(e)}",
            exc_info=True,
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions_bp.route(
    "/api/v1/transactions/<int:transaction_id>/related", methods=["GET"]
)
@api_token_required
@handle_errors
def get_related_transactions(transaction_id):
    """Get all transactions related to a given transaction (same date and payee)."""
    current_app.logger.debug(f"GET /api/v1/transactions/{transaction_id}/related")

    # Use service layer to get related transactions
    related_transactions = TransactionService.get_related_transactions(transaction_id)

    if related_transactions is None:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify(related_transactions), 200


@transactions_bp.route("/api/v1/transactions/<int:transaction_id>", methods=["DELETE"])
@api_token_required
@handle_errors
def delete_transaction(transaction_id):
    """Delete a single transaction."""
    current_app.logger.debug(f"DELETE /api/v1/transactions/{transaction_id}")

    # Use service layer to delete transaction
    success, message = TransactionService.delete_transaction(transaction_id)

    if not success:
        if "not found" in message.lower():
            return jsonify({"error": message}), 404
        return jsonify({"error": message}), 500

    return jsonify({"message": message}), 200


@transactions_bp.route(
    "/api/v1/transactions/<int:transaction_id>/related", methods=["DELETE"]
)
@api_token_required
@handle_errors
def delete_related_transactions(transaction_id):
    """Delete a transaction and all its related transactions (same date and payee)."""
    current_app.logger.debug(f"DELETE /api/v1/transactions/{transaction_id}/related")

    # Use service layer to delete related transactions
    success, message, deleted_count = TransactionService.delete_related_transactions(
        transaction_id
    )

    if not success:
        if "not found" in message.lower():
            return jsonify({"error": message}), 404
        return jsonify({"error": message}), 500

    return jsonify({"message": message, "count": deleted_count}), 200


@transactions_bp.route("/api/v1/transactions/recent", methods=["GET"])
@api_token_required
@handle_errors
def get_recent_transactions():
    """Get recent transactions, grouped by date and payee."""
    current_app.logger.debug("GET /api/v1/transactions/recent")

    try:
        # Parse query parameters
        limit = request.args.get("limit", type=int, default=7)
        book_id = request.args.get("book_id", type=int)

        # Log request
        current_app.logger.debug(
            f"GET /api/v1/transactions/recent request with params: {request.args}"
        )

        # Use service layer to get recent transactions
        formatted_transactions = TransactionService.get_recent_transactions(
            limit=limit, book_id=book_id
        )

        # Return in the format expected by the frontend
        response = {
            "transactions": formatted_transactions,
            "total": len(formatted_transactions),
        }

        return jsonify(response)

    except Exception as e:
        current_app.logger.error(
            f"Error in get_recent_transactions: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "Failed to retrieve recent transactions"}), 500
