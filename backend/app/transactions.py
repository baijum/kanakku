from flask import Blueprint, request, jsonify, current_app, g
from app.models import db, Transaction, Account, Book
from .extensions import api_token_required
from datetime import datetime
import traceback
import json
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func, or_

transactions = Blueprint("transactions", __name__)


def get_active_book_id():
    """Get the active book ID for the current user or raise an error if not set."""
    user = g.current_user

    if not user.active_book_id:
        # Try to find first book ordered by ID
        first_book = Book.query.filter_by(user_id=user.id).order_by(Book.id).first()
        if first_book:
            user.active_book_id = first_book.id
            db.session.commit()
        else:
            # Create a default book
            default_book = Book(user_id=user.id, name="Book 1")
            db.session.add(default_book)
            db.session.flush()
            user.active_book_id = default_book.id
            db.session.commit()

    return user.active_book_id


@transactions.route("/api/v1/transactions", methods=["POST"])
@api_token_required
def create_transaction():
    """Create a new transaction from the provided JSON data."""
    # request_id = getattr(request, "request_id", "unknown") # Removed unused variable
    current_app.logger.info("Processing transaction creation request")

    active_book_id = get_active_book_id()

    try:
        # Parse and validate the request data
        try:
            data = request.get_json()
            if data is None:
                current_app.logger.warning(f"Failed to parse JSON data: {request.data}")
                return jsonify({"error": "Request must be valid JSON"}), 400
        except Exception as json_error:
            current_app.logger.error(
                f"JSON parsing error: {str(json_error)}", exc_info=True
            )
            return jsonify({"error": "Invalid JSON format"}), 400

        # Log sanitized data (remove sensitive info if any)
        log_data = data.copy() if data else {}
        current_app.logger.debug(f"Transaction data: {json.dumps(log_data)}")

        # Validate required top-level fields
        missing_fields = []
        if "date" not in data:
            missing_fields.append("date")
        if "payee" not in data or not data["payee"]:
            missing_fields.append("payee")
        if (
            "postings" not in data
            or not isinstance(data["postings"], list)
            or len(data["postings"]) < 1
        ):
            missing_fields.append("postings")

        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            current_app.logger.warning(f"Validation error: {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Validate date format
        try:
            transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            current_app.logger.warning(f"Invalid date format: {data['date']}")
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Validate that a single transaction doesn't debit and credit the same account
        account_directions = {}
        for posting in data["postings"]:
            account_name = posting.get("account")
            amount_str = posting.get("amount")
            if not account_name or amount_str is None:
                # Basic validation handled later, skip here
                continue
            try:
                amount_float = float(amount_str)
                if amount_float == 0:
                    continue  # Ignore zero amounts for this validation

                direction = "debit" if amount_float > 0 else "credit"

                if account_name not in account_directions:
                    account_directions[account_name] = direction
                elif account_directions[account_name] != direction:
                    error_msg = f"Cannot debit and credit the same account '{account_name}' in a single transaction."
                    current_app.logger.warning(f"Validation error: {error_msg}")
                    return jsonify({"error": error_msg}), 400
            except ValueError:
                # Invalid amount format handled later, skip here
                continue

        # Access current_user via g
        user = g.current_user

        # Process each posting
        transaction_responses = []

        for posting in data["postings"]:
            # Validate posting fields
            if "account" not in posting or not posting["account"]:
                return jsonify({"error": "Missing account name in posting"}), 400

            if "amount" not in posting or posting["amount"] == "":
                return jsonify({"error": "Missing amount in posting"}), 400

            try:
                amount_float = float(posting["amount"])
            except ValueError:
                return (
                    jsonify({"error": "Invalid amount format. Must be a number."}),
                    400,
                )

            # Find the account in the active book
            account_name = posting["account"]
            account = Account.query.filter_by(
                name=account_name, user_id=user.id, book_id=active_book_id
            ).first()

            if not account:
                current_app.logger.error("Account not found: {}".format(account_name))
                return jsonify({"error": "Account not found in the active book"}), 404

            # Create transaction object within the active book
            new_transaction = Transaction(
                user_id=user.id,
                book_id=active_book_id,
                account_id=account.id,
                date=transaction_date,
                description=data["payee"],  # Use payee as description
                payee=data["payee"],
                amount=amount_float,
                currency=posting.get("currency", "INR"),
                status=data.get("status"),  # Save the status if provided
            )

            # Update the account balance - no longer using account type
            account.balance += amount_float

            db.session.add(new_transaction)
            transaction_responses.append(new_transaction)

        # Commit all transactions together
        try:
            db.session.commit()
            # Refresh the objects to get updated values
            for tx in transaction_responses:
                db.session.refresh(tx)
        except SQLAlchemyError as db_error:
            db.session.rollback()
            current_app.logger.error(
                f"Database error during transaction save: {str(db_error)}",
                exc_info=True,
            )
            return (
                jsonify(
                    {"error": "Failed to save transaction", "details": str(db_error)}
                ),
                500,
            )

        # Prepare response
        response_data = {
            "message": "Transaction created successfully",
            "transactions": [tx.to_dict() for tx in transaction_responses],
        }

        current_app.logger.info(
            f"Transaction created successfully: {len(transaction_responses)} entries"
        )
        return jsonify(response_data), 201

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            f"Unhandled error in create_transaction: {str(e)}", exc_info=True
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route("/api/v1/transactions", methods=["GET"])
@api_token_required
def get_transactions():
    current_app.logger.debug("Entered get_transactions route")
    try:
        # Log request
        current_app.logger.debug(
            f"GET /api/v1/transactions request with params: {request.args}"
        )

        active_book_id = get_active_book_id()
        limit = request.args.get("limit", type=int)
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")
        search_term = request.args.get("search", "").strip()
        offset = request.args.get("offset", type=int, default=0)

        # Start with base query - filter by user and active book
        query = Transaction.query.filter_by(
            user_id=g.current_user.id, book_id=active_book_id
        )

        # Apply search filter if provided
        if search_term:
            # Check if we're using PostgreSQL (FTS only works with PostgreSQL)
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').lower()
            if 'postgresql' in db_url:
                # Convert search term to tsquery with prefix matching for last word
                search_words = search_term.split()
                if search_words:
                    # Add prefix matching to the last word, exact matching for others
                    tsquery_parts = []
                    for i, word in enumerate(search_words):
                        # Sanitize word by removing special characters that break tsquery
                        # Keep alphanumeric characters and basic punctuation
                        sanitized_word = ''.join(c for c in word if c.isalnum() or c in '-_')
                        if sanitized_word:  # Only add non-empty words
                            if i == len(search_words) - 1:  # Last word gets prefix matching
                                tsquery_parts.append(f"{sanitized_word}:*")
                            else:
                                tsquery_parts.append(sanitized_word)
                    
                    if tsquery_parts:  # Only proceed if we have valid search terms
                        search_query = ' & '.join(tsquery_parts)
                        current_app.logger.debug(f"Search query: {search_query}")
                        
                        try:
                            query = query.filter(
                                Transaction.search_vector.op('@@')(
                                    func.to_tsquery('english', search_query)
                                )
                            )
                        except Exception as e:
                            # If tsquery fails, fall back to basic text search
                            current_app.logger.warning(f"FTS query failed, falling back to basic search: {e}")
                            search_filter = f"%{search_term}%"
                            query = query.filter(
                                or_(
                                    Transaction.description.ilike(search_filter),
                                    Transaction.payee.ilike(search_filter),
                                    Transaction.currency.ilike(search_filter)
                                )
                            )
            else:
                # Fallback to basic text search for non-PostgreSQL databases
                current_app.logger.debug(f"Using fallback search for: {search_term}")
                search_filter = f"%{search_term}%"
                query = query.filter(
                    or_(
                        Transaction.description.ilike(search_filter),
                        Transaction.payee.ilike(search_filter),
                        Transaction.currency.ilike(search_filter)
                    )
                )

        # Apply date filters if provided
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(Transaction.date >= start_date_obj)
            except ValueError:
                current_app.logger.error(f"Invalid start date format: {start_date}")

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(Transaction.date <= end_date_obj)
            except ValueError:
                current_app.logger.error(f"Invalid end date format: {end_date}")

        # Get total count for pagination
        total_count = query.count()

        # Apply ordering, offset and limit
        query = query.order_by(Transaction.date.desc())

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        transactions_list = query.all()

        # Group transactions by date and payee to create the expected structure
        grouped_transactions = {}

        for tx in transactions_list:
            # Get account name
            if not tx.account_id:
                current_app.logger.error("Transaction has no account_id")
                continue
            account = db.session.get(Account, tx.account_id)
            if not account:
                current_app.logger.error("Account not found for transaction")
                continue
            account_name = account.name

            # Create a unique key for grouping
            key = f"{tx.date.isoformat()}|{tx.payee}"

            # Create or update transaction group
            if key not in grouped_transactions:
                grouped_transactions[key] = {
                    "id": tx.id,  # Include the ID of the first transaction in the group
                    "date": tx.date.isoformat(),
                    "payee": tx.payee,
                    "status": tx.status or "",  # Use the status from database
                    "postings": [],
                }

            # Add posting to transaction group
            grouped_transactions[key]["postings"].append(
                {
                    "id": tx.id,  # Include the transaction ID with each posting
                    "account": account_name,
                    "amount": str(tx.amount),
                    "currency": tx.currency,
                }
            )

        # Convert grouped transactions to a list
        formatted_transactions = list(grouped_transactions.values())

        # Return in the format expected by the frontend
        response = {"transactions": formatted_transactions, "total": total_count}

        return jsonify(response)
    except Exception as e:
        current_app.logger.error(
            f"Error in get_transactions: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "Failed to retrieve transactions"}), 500


@transactions.route("/api/v1/transactions/<int:transaction_id>", methods=["GET"])
@api_token_required
def get_transaction(transaction_id):
    """Get a single transaction by ID"""
    try:
        # Log request
        current_app.logger.debug(f"GET /api/v1/transactions/{transaction_id}")

        # Get the transaction
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=g.current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {g.current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Get account name
        if not transaction.account_id:
            current_app.logger.error("Transaction has no account_id")
            return jsonify({"error": "Transaction has no associated account"}), 400

        account = db.session.get(Account, transaction.account_id)
        if not account:
            current_app.logger.error("Account not found for transaction")
            return jsonify({"error": "Associated account not found"}), 404
        account_name = account.name

        # Format the transaction
        formatted_transaction = {
            "id": transaction.id,
            "date": transaction.date.isoformat(),
            "description": transaction.description,
            "payee": transaction.payee,
            "account_id": transaction.account_id,
            "account_name": account_name,
            "amount": transaction.amount,
            "currency": transaction.currency,
        }

        current_app.logger.debug(f"Returning transaction: {formatted_transaction}")
        return jsonify(formatted_transaction)
    except Exception as e:
        current_app.logger.error(
            f"Error in get_transaction: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "Failed to retrieve transaction"}), 500


@transactions.route("/api/v1/transactions/<int:transaction_id>", methods=["PUT"])
@api_token_required
def update_transaction(transaction_id):
    """Update a transaction"""
    current_app.logger.debug(
        f"Entered update_transaction route for id: {transaction_id}"
    )
    try:
        # Log the request for debugging
        current_app.logger.debug(f"Update transaction request: {request.data}")

        try:
            data = request.get_json()
            if data is None:
                current_app.logger.error(
                    "Failed to parse JSON: {}".format(request.data)
                )
                return jsonify({"error": "Request must be valid JSON"}), 400
        except Exception as json_error:
            current_app.logger.error(
                "JSON parsing error: {}: {}".format(str(json_error), request.data)
            )
            return jsonify({"error": "Invalid JSON format"}), 400

        # Find the transaction
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=g.current_user.id
        ).first()

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Store original values to update account balance correctly
        original_amount = transaction.amount

        # Validate required fields
        if "date" in data:
            try:
                transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
                transaction.date = transaction_date
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if "payee" in data and data["payee"]:
            transaction.payee = data["payee"]
            transaction.description = data["payee"]  # Update description to match payee

        if "amount" in data:
            try:
                amount_float = float(data["amount"])
                transaction.amount = amount_float
            except ValueError:
                return (
                    jsonify({"error": "Invalid amount format. Must be a number."}),
                    400,
                )

        if "currency" in data:
            transaction.currency = data["currency"]

        if "status" in data:
            transaction.status = data["status"]

        if "account_id" in data:
            new_account_id = data["account_id"]
            account = Account.query.filter_by(
                id=new_account_id, user_id=g.current_user.id
            ).first()

            if not account:
                return jsonify({"error": "Account not found"}), 404

            transaction.account_id = new_account_id

        # Update account balances
        if "amount" in data or "account_id" in data:
            # Calculate the difference between the new and old amounts
            amount_difference = transaction.amount - original_amount
            current_app.logger.debug(
                "Original amount: {}, New amount: {}, Difference: {}".format(
                    original_amount, transaction.amount, amount_difference
                )
            )

            # Apply the difference to the account balance
            account = Account.query.filter_by(
                id=transaction.account_id, user_id=g.current_user.id
            ).first()
            if account:
                current_app.logger.debug("Current balance: {}".format(account.balance))
                # No longer checking account type, simply add the difference
                account.balance += amount_difference
                current_app.logger.debug("New balance: {}".format(account.balance))

        # Commit changes
        try:
            db.session.commit()
            # Refresh transaction to get updated values
            db.session.refresh(transaction)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Database commit error: {}".format(str(e)))
            return jsonify({"error": "Failed to update transaction"}), 500

        # Prepare response
        response_data = {
            "message": "Transaction updated successfully",
            "transaction": transaction.to_dict(),
        }

        current_app.logger.debug(
            "Transaction update response: {}".format(json.dumps(response_data))
        )
        return jsonify(response_data), 200

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            "Unhandled error in update_transaction: {} - Traceback: {}".format(
                str(e), traceback.format_exc()
            )
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route(
    "/api/v1/transactions/<int:transaction_id>/update_with_postings", methods=["PUT"]
)
@api_token_required
def update_transaction_with_postings(transaction_id):
    """Update a transaction with multiple postings."""
    try:
        # Log request
        current_app.logger.debug(
            f"PUT /api/v1/transactions/{transaction_id}/update_with_postings"
        )

        # Get active book ID for the current user
        active_book_id = get_active_book_id()

        # Parse and validate the request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request must be valid JSON"}), 400

        # Validate required fields
        missing_fields = []
        if "date" not in data:
            missing_fields.append("date")
        if "payee" not in data or not data["payee"]:
            missing_fields.append("payee")
        if (
            "postings" not in data
            or not isinstance(data["postings"], list)
            or len(data["postings"]) < 1
        ):
            missing_fields.append("postings")

        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            return jsonify({"error": error_msg}), 400

        # Validate date format
        try:
            transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Get original transaction IDs, with default being the single ID in the URL
        original_transaction_ids = data.get(
            "original_transaction_ids", [transaction_id]
        )
        if not isinstance(original_transaction_ids, list):
            original_transaction_ids = [original_transaction_ids]

        current_app.logger.debug(
            "Original transaction IDs to replace: {}".format(original_transaction_ids)
        )

        # Find all original transactions
        original_transactions = []
        for orig_id in original_transaction_ids:
            tx = Transaction.query.filter_by(
                id=orig_id, user_id=g.current_user.id
            ).first()
            if tx:
                original_transactions.append(tx)
            else:
                current_app.logger.warning(
                    "Original transaction ID {} not found".format(orig_id)
                )

        if not original_transactions:
            return jsonify({"error": "None of the original transactions found"}), 404

        # Start by reversing the effect of original transactions on their accounts
        original_transaction_ids_to_delete = [tx.id for tx in original_transactions]

        for original_transaction in original_transactions:
            # Reverse the effect on the original account
            original_account = db.session.get(Account, original_transaction.account_id)
            if original_account:
                # No longer checking account type, simply add the amount back
                original_account.balance += original_transaction.amount

            # Delete the original transaction
            db.session.delete(original_transaction)

        # Commit the deletion of original transactions first
        try:
            db.session.commit()

            # Double-check that transactions are actually deleted by using raw SQL
            # This is to ensure the transactions are truly gone from the database
            for tx_id in original_transaction_ids_to_delete:
                stmt = text('DELETE FROM "transaction" WHERE id = :id')
                db.session.execute(stmt, {"id": tx_id})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Failed to delete original transactions: {str(e)}"
            )
            return jsonify({"error": "Failed to delete original transactions"}), 500

        # Validate that a single transaction doesn't debit and credit the same account
        account_directions = {}
        for posting in data["postings"]:
            account_name = posting.get("account")
            amount_str = posting.get("amount")
            if not account_name or amount_str is None:
                # Basic validation handled later, skip here
                continue
            try:
                amount_float = float(amount_str)
                if amount_float == 0:
                    continue  # Ignore zero amounts for this validation

                direction = "debit" if amount_float > 0 else "credit"

                if account_name not in account_directions:
                    account_directions[account_name] = direction
                elif account_directions[account_name] != direction:
                    # Rollback changes made before this validation (deleting original transactions)
                    db.session.rollback()
                    error_msg = f"Cannot debit and credit the same account '{account_name}' in a single transaction."
                    current_app.logger.warning(f"Validation error: {error_msg}")
                    return jsonify({"error": error_msg}), 400
            except ValueError:
                # Invalid amount format handled later, skip here
                continue

        # Process each new posting
        new_transactions = []

        for posting in data["postings"]:
            # Validate posting fields
            if "account" not in posting or not posting["account"]:
                db.session.rollback()
                return jsonify({"error": "Missing account name in posting"}), 400

            if "amount" not in posting or posting["amount"] == "":
                db.session.rollback()
                return jsonify({"error": "Missing amount in posting"}), 400

            try:
                amount_float = float(posting["amount"])
            except ValueError:
                db.session.rollback()
                return (
                    jsonify({"error": "Invalid amount format. Must be a number."}),
                    400,
                )

            # Find the account in the active book
            account_name = posting["account"]
            account = Account.query.filter_by(
                name=account_name, user_id=g.current_user.id, book_id=active_book_id
            ).first()

            if not account:
                current_app.logger.error("Account not found: {}".format(account_name))
                db.session.rollback()
                return jsonify({"error": "Account not found in active book"}), 404

            # Create transaction object with book_id
            new_transaction = Transaction(
                user_id=g.current_user.id,
                book_id=active_book_id,
                account_id=account.id,
                date=transaction_date,
                description=data["payee"],  # Use payee as description
                payee=data["payee"],
                amount=amount_float,
                currency=posting.get("currency", "INR"),
                status=data.get("status"),  # Include status if provided
            )

            # Update the account balance - no longer using account type
            account.balance += amount_float

            db.session.add(new_transaction)
            new_transactions.append(new_transaction)

        # Commit all transactions together
        try:
            db.session.commit()
            # Refresh the objects to get updated values
            for tx in new_transactions:
                db.session.refresh(tx)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({"error": "Failed to update transaction"}), 500

        # Prepare response
        response_data = {
            "message": "Transaction updated successfully",
            "transactions": [tx.to_dict() for tx in new_transactions],
        }

        current_app.logger.debug(
            f"Transaction update response: {json.dumps(response_data)}"
        )
        return jsonify(response_data), 200

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            f"Unhandled error in update_transaction_with_postings: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route(
    "/api/v1/transactions/<int:transaction_id>/related", methods=["GET"]
)
@api_token_required
def get_related_transactions(transaction_id):
    """Get a transaction and all its related transactions (by date and payee)"""
    try:
        # Log request
        current_app.logger.debug(f"GET /api/v1/transactions/{transaction_id}/related")

        # Get the transaction to find its date and payee
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=g.current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {g.current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Get all transactions with the same date and payee
        related_transactions = Transaction.query.filter_by(
            user_id=g.current_user.id, date=transaction.date, payee=transaction.payee
        ).all()

        if not related_transactions:
            current_app.logger.warning(
                f"No related transactions found for transaction ID {transaction_id}"
            )
            # If no related transactions found, just return the original transaction
            related_transactions = [transaction]

        # Format the transactions with account information
        formatted_transactions = []
        for tx in related_transactions:
            # Get account name
            if not tx.account_id:
                current_app.logger.error("Transaction has no account_id")
                continue
            account = db.session.get(Account, tx.account_id)
            if not account:
                current_app.logger.error("Account not found for transaction")
                continue
            account_name = account.name

            formatted_transaction = {
                "id": tx.id,
                "date": tx.date.isoformat(),
                "description": tx.description,
                "payee": tx.payee,
                "account_id": tx.account_id,
                "account_name": account_name,
                "amount": tx.amount,
                "currency": tx.currency,
                "status": tx.status or "",
            }
            formatted_transactions.append(formatted_transaction)

        # Prepare the response - format it to match test expectations
        response = {
            "transactions": formatted_transactions,
            "date": transaction.date.isoformat(),
            "payee": transaction.payee,
            "primary_transaction_id": transaction_id,
        }

        current_app.logger.debug(f"Returning related transactions: {response}")
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(
            f"Error in get_related_transactions: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "Failed to retrieve related transactions"}), 500


@transactions.route("/api/v1/transactions/<int:transaction_id>", methods=["DELETE"])
@api_token_required
def delete_transaction(transaction_id):
    """Delete a specific transaction."""
    current_app.logger.info(
        f"Processing transaction deletion request for ID: {transaction_id}"
    )

    # Find the transaction
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=g.current_user.id
    ).first()

    if not transaction:
        current_app.logger.warning(
            f"Attempted to delete non-existent transaction ID: {transaction_id}"
        )
        return jsonify({"error": "Transaction not found"}), 404

    # Delete the transaction
    db.session.delete(transaction)
    db.session.commit()

    current_app.logger.info(f"Transaction ID {transaction_id} deleted successfully")
    return jsonify({"message": "Transaction deleted"}), 200


@transactions.route(
    "/api/v1/transactions/<int:transaction_id>/related", methods=["DELETE"]
)
@api_token_required
def delete_related_transactions(transaction_id):
    """Delete a transaction and all its related transactions (same date and payee)"""
    current_app.logger.debug(
        f"Entered delete_related_transactions route for ID: {transaction_id}"
    )
    try:
        # Find the transaction to identify related ones
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=g.current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {g.current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Find all transactions with the same date and payee
        related_transactions = Transaction.query.filter_by(
            user_id=g.current_user.id, date=transaction.date, payee=transaction.payee
        ).all()

        if not related_transactions:
            current_app.logger.warning(
                f"No related transactions found for transaction ID {transaction_id}"
            )
            return jsonify({"error": "No transactions found to delete"}), 404

        # Track how many were deleted
        deleted_count = 0

        # Undo account balance effects and delete each transaction
        for tx in related_transactions:
            # Get the account
            if not tx.account_id:
                current_app.logger.error("Transaction has no account_id")
                continue
            account = db.session.get(Account, tx.account_id)
            if not account:
                current_app.logger.error("Account not found for transaction")
                continue

            # Simply reverse the transaction amount
            account.balance -= tx.amount

            # Delete the transaction
            db.session.delete(tx)
            deleted_count += 1

        # Commit all changes
        try:
            db.session.commit()
            current_app.logger.info(
                f"Deleted {deleted_count} related transactions for ID {transaction_id}"
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({"error": "Failed to delete related transactions"}), 500

        return (
            jsonify(
                {
                    "message": "Related transactions deleted successfully",
                    "count": deleted_count,
                }
            ),
            200,
        )

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            f"Unhandled error in delete_related_transactions: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route("/api/v1/transactions/recent", methods=["GET"])
@api_token_required
def get_recent_transactions():
    """Get recent transactions, grouped by date and payee, but ensuring we return the requested number of groups"""
    current_app.logger.debug("Entered get_recent_transactions route")
    try:
        # Log request
        current_app.logger.debug(
            f"GET /api/v1/transactions/recent request with params: {request.args}"
        )

        limit = request.args.get("limit", type=int, default=7)
        book_id = request.args.get("book_id", type=int)

        # If book_id is not provided, use the active book
        if not book_id:
            book_id = get_active_book_id()

        # Fetch more raw transactions than we need to ensure we have enough after grouping
        fetch_limit = (
            limit * 4
        )  # Fetch 4x the requested limit to ensure we have enough groups

        # Start with base query
        query = Transaction.query.filter_by(user_id=g.current_user.id, book_id=book_id)

        # Apply ordering
        query = query.order_by(Transaction.date.desc())

        # Fetch more transactions than needed to ensure we have enough groups
        query = query.limit(fetch_limit)

        transactions_list = query.all()

        # Group transactions by date and payee to create the expected structure
        grouped_transactions = {}

        for tx in transactions_list:
            # Get account name
            if not tx.account_id:
                current_app.logger.error("Transaction has no account_id")
                continue
            account = db.session.get(Account, tx.account_id)
            if not account:
                current_app.logger.error("Account not found for transaction")
                continue
            account_name = account.name

            # Create a unique key for grouping
            key = f"{tx.date.isoformat()}|{tx.payee}"

            # Create or update transaction group
            if key not in grouped_transactions:
                grouped_transactions[key] = {
                    "id": tx.id,  # Include the ID of the first transaction in the group
                    "date": tx.date.isoformat(),
                    "payee": tx.payee,
                    "status": tx.status or "",  # Use the status from database
                    "postings": [],
                }

            # Add posting to transaction group
            grouped_transactions[key]["postings"].append(
                {
                    "id": tx.id,  # Include the transaction ID with each posting
                    "account": account_name,
                    "amount": str(tx.amount),
                    "currency": tx.currency,
                }
            )

        # Convert grouped transactions to a list and limit to exactly the requested number
        formatted_transactions = list(grouped_transactions.values())[:limit]

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


# Add a decorator function for consistent error handling
def handle_errors(func):
    """Decorator to provide consistent error handling for transaction routes."""
    from functools import wraps

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
