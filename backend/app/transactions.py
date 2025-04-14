from flask import Blueprint, request, jsonify, current_app
from app.models import db, Transaction, Account
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
import traceback
import json

transactions = Blueprint("transactions", __name__)


@transactions.route("/api/transactions", methods=["POST"])
@jwt_required()
def create_transaction():
    current_app.logger.debug("Entered create_transaction route")
    try:
        # Log the request for debugging
        current_app.logger.debug(f"Transaction request: {request.data}")

        try:
            data = request.get_json()
            if data is None:
                current_app.logger.error(f"Failed to parse JSON: {request.data}")
                return jsonify({"error": "Request must be valid JSON"}), 400
        except Exception as json_error:
            current_app.logger.error(
                f"JSON parsing error: {str(json_error)}: {request.data}"
            )
            return jsonify({"error": "Invalid JSON format"}), 400

        # Validate required top-level fields
        if "date" not in data:
            return jsonify({"error": "Missing required field: date"}), 400

        if "payee" not in data or not data["payee"]:
            return jsonify({"error": "Missing required field: payee"}), 400

        if (
            "postings" not in data
            or not isinstance(data["postings"], list)
            or len(data["postings"]) < 1
        ):
            return jsonify({"error": "Missing or invalid postings"}), 400

        # Validate date format
        try:
            transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": f"Invalid date format. Use YYYY-MM-DD."}), 400

        # Access current_user
        user = current_user
        if not user:
            # Should not happen if @jwt_required() works
            return jsonify({"error": "Authentication error: User not found"}), 401

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

            # Find the account
            account_name = posting["account"]
            account = Account.query.filter_by(
                name=account_name, user_id=user.id
            ).first()

            if not account:
                return jsonify({"error": f"Account '{account_name}' not found"}), 404

            # Create transaction object
            new_transaction = Transaction(
                user_id=user.id,
                account_id=account.id,
                date=transaction_date,
                description=data["payee"],  # Use payee as description
                payee=data["payee"],
                amount=amount_float,
                currency=posting.get("currency", "INR"),
            )

            # Update the account balance based on account type
            # For Asset and Expense accounts, positive amounts increase the balance
            # For Liability, Equity, and Income accounts, positive amounts decrease the balance
            if account.type.lower() in ["liability", "equity", "income"]:
                # Invert the sign for these account types
                account.balance -= amount_float
            else:
                # Default behavior for Asset and Expense accounts
                account.balance += amount_float

            db.session.add(new_transaction)
            transaction_responses.append(new_transaction)

        # Commit all transactions together
        try:
            db.session.commit()
            # Refresh the objects to get updated values
            for tx in transaction_responses:
                db.session.refresh(tx)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({"error": "Failed to save transaction"}), 500

        # Prepare response
        response_data = {
            "message": "Transaction created successfully",
            "transactions": [tx.to_dict() for tx in transaction_responses],
        }

        current_app.logger.debug(f"Transaction response: {json.dumps(response_data)}")
        return jsonify(response_data), 201

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            f"Unhandled error in create_transaction: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route("/api/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    current_app.logger.debug("Entered get_transactions route")
    try:
        # Log request
        current_app.logger.debug(
            f"GET /api/transactions request with params: {request.args}"
        )

        limit = request.args.get("limit", type=int)
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")
        offset = request.args.get("offset", type=int, default=0)

        # Start with base query
        query = Transaction.query.filter_by(user_id=current_user.id)

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
            account = db.session.get(Account, tx.account_id)
            account_name = account.name if account else "Unknown Account"

            # Create a unique key for grouping
            key = f"{tx.date.isoformat()}|{tx.payee}"

            # Create or update transaction group
            if key not in grouped_transactions:
                grouped_transactions[key] = {
                    "id": tx.id,  # Include the ID of the first transaction in the group
                    "date": tx.date.isoformat(),
                    "payee": tx.payee,
                    "status": "",  # Status not stored in database, using empty string
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


@transactions.route("/api/transactions/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction(transaction_id):
    """Get a single transaction by ID"""
    try:
        # Log request
        current_app.logger.debug(f"GET /api/transactions/{transaction_id}")

        # Get the transaction
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Get account name
        account = db.session.get(Account, transaction.account_id)
        account_name = account.name if account else "Unknown Account"

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


@transactions.route("/api/transactions/<int:transaction_id>", methods=["PUT"])
@jwt_required()
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
                current_app.logger.error(f"Failed to parse JSON: {request.data}")
                return jsonify({"error": "Request must be valid JSON"}), 400
        except Exception as json_error:
            current_app.logger.error(
                f"JSON parsing error: {str(json_error)}: {request.data}"
            )
            return jsonify({"error": "Invalid JSON format"}), 400

        # Find the transaction
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=current_user.id
        ).first()

        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Store original values to update account balance correctly
        original_amount = transaction.amount
        original_account_id = transaction.account_id

        # Validate required fields
        if "date" in data:
            try:
                transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
                transaction.date = transaction_date
            except ValueError:
                return jsonify({"error": f"Invalid date format. Use YYYY-MM-DD."}), 400

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

        if "account_id" in data:
            new_account_id = data["account_id"]
            account = db.session.get(Account, new_account_id, user_id=current_user.id)

            if not account:
                return (
                    jsonify({"error": f"Account with ID '{new_account_id}' not found"}),
                    404,
                )

            transaction.account_id = new_account_id

        # Update account balances
        if "amount" in data or "account_id" in data:
            # Calculate the difference between the new and old amounts
            amount_difference = transaction.amount - original_amount
            current_app.logger.debug(
                f"Original amount: {original_amount}, New amount: {transaction.amount}, Difference: {amount_difference}"
            )

            # Apply the difference to the account balance
            account = db.session.get(Account, transaction.account_id)
            if account:
                current_app.logger.debug(f"Current balance: {account.balance}")
                if account.type.lower() in ["liability", "equity", "income"]:
                    # For these types, positive amounts decrease balance
                    account.balance -= amount_difference
                else:
                    # For asset and expense, positive amounts increase balance
                    account.balance += amount_difference
                current_app.logger.debug(f"New balance: {account.balance}")

        # Commit changes
        try:
            db.session.commit()
            # Refresh transaction to get updated values
            db.session.refresh(transaction)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({"error": "Failed to update transaction"}), 500

        # Prepare response
        response_data = {
            "message": "Transaction updated successfully",
            "transaction": transaction.to_dict(),
        }

        current_app.logger.debug(
            f"Transaction update response: {json.dumps(response_data)}"
        )
        return jsonify(response_data), 200

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            f"Unhandled error in update_transaction: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route(
    "/api/transactions/<int:transaction_id>/update_with_postings", methods=["PUT"]
)
@jwt_required()
def update_transaction_with_postings(transaction_id):
    """Update a transaction with multiple postings"""
    current_app.logger.debug(
        f"Entered update_transaction_with_postings route for id: {transaction_id}"
    )
    try:
        # Log the request for debugging
        current_app.logger.debug(f"Update transaction request: {request.data}")

        try:
            data = request.get_json()
            if data is None:
                current_app.logger.error(f"Failed to parse JSON: {request.data}")
                return jsonify({"error": "Request must be valid JSON"}), 400
        except Exception as json_error:
            current_app.logger.error(
                f"JSON parsing error: {str(json_error)}: {request.data}"
            )
            return jsonify({"error": "Invalid JSON format"}), 400

        # Validate required fields
        if "date" not in data:
            return jsonify({"error": "Missing required field: date"}), 400

        if "payee" not in data or not data["payee"]:
            return jsonify({"error": "Missing required field: payee"}), 400

        if (
            "postings" not in data
            or not isinstance(data["postings"], list)
            or len(data["postings"]) < 1
        ):
            return jsonify({"error": "Missing or invalid postings"}), 400

        # Validate date format
        try:
            transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": f"Invalid date format. Use YYYY-MM-DD."}), 400

        # Get all original transaction IDs to be replaced
        original_transaction_ids = data.get(
            "original_transaction_ids", [transaction_id]
        )
        if not isinstance(original_transaction_ids, list):
            original_transaction_ids = [original_transaction_ids]

        current_app.logger.debug(
            f"Original transaction IDs to replace: {original_transaction_ids}"
        )

        # Find all original transactions
        original_transactions = []
        for orig_id in original_transaction_ids:
            tx = Transaction.query.filter_by(
                id=orig_id, user_id=current_user.id
            ).first()
            if tx:
                original_transactions.append(tx)
            else:
                current_app.logger.warning(
                    f"Original transaction ID {orig_id} not found"
                )

        if not original_transactions:
            return jsonify({"error": "None of the original transactions found"}), 404

        # Start by reversing the effect of original transactions on their accounts
        for original_transaction in original_transactions:
            # Store original account info to reverse its effect
            original_account_id = original_transaction.account_id
            original_amount = original_transaction.amount

            # Reverse the effect on the original account
            original_account = db.session.get(Account, original_account_id)
            if original_account:
                if original_account.type.lower() in ["liability", "equity", "income"]:
                    original_account.balance += original_amount
                else:
                    original_account.balance -= original_amount

            # Delete the original transaction
            db.session.delete(original_transaction)

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

            # Find the account
            account_name = posting["account"]
            account = Account.query.filter_by(
                name=account_name, user_id=current_user.id
            ).first()

            if not account:
                db.session.rollback()
                return jsonify({"error": f"Account '{account_name}' not found"}), 404

            # Create transaction object
            new_transaction = Transaction(
                user_id=current_user.id,
                account_id=account.id,
                date=transaction_date,
                description=data["payee"],  # Use payee as description
                payee=data["payee"],
                amount=amount_float,
                currency=posting.get("currency", "INR"),
            )

            # Update the account balance based on account type
            if account.type.lower() in ["liability", "equity", "income"]:
                account.balance -= amount_float
            else:
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


@transactions.route("/api/transactions/<int:transaction_id>/related", methods=["GET"])
@jwt_required()
def get_related_transactions(transaction_id):
    """Get a transaction and all its related transactions (by date and payee)"""
    try:
        # Log request
        current_app.logger.debug(f"GET /api/transactions/{transaction_id}/related")

        # Get the transaction to find its date and payee
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Get all transactions with the same date and payee
        related_transactions = Transaction.query.filter_by(
            user_id=current_user.id, date=transaction.date, payee=transaction.payee
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
            account = db.session.get(Account, tx.account_id)
            account_name = account.name if account else "Unknown Account"

            formatted_transaction = {
                "id": tx.id,
                "date": tx.date.isoformat(),
                "description": tx.description,
                "payee": tx.payee,
                "account_id": tx.account_id,
                "account_name": account_name,
                "account_type": account.type if account else "",
                "amount": tx.amount,
                "currency": tx.currency,
            }
            formatted_transactions.append(formatted_transaction)

        # Prepare the response
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


@transactions.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction by ID"""
    current_app.logger.debug(
        f"Entered delete_transaction route for ID: {transaction_id}"
    )
    try:
        # Find the transaction to delete
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Undo the effect on the account balance before deleting
        account = db.session.get(Account, transaction.account_id)
        if account:
            # Reverse the effect based on account type
            if account.type.lower() in ["liability", "equity", "income"]:
                account.balance += transaction.amount
            else:
                account.balance -= transaction.amount

        # Delete the transaction
        db.session.delete(transaction)

        # Commit changes
        try:
            db.session.commit()
            current_app.logger.info(
                f"Transaction ID {transaction_id} deleted successfully"
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({"error": "Failed to delete transaction"}), 500

        return jsonify({"message": "Transaction deleted successfully"}), 200

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(
            f"Unhandled error in delete_transaction: {str(e)} - Traceback: {traceback.format_exc()}"
        )
        return jsonify({"error": "An unexpected server error occurred"}), 500


@transactions.route(
    "/api/transactions/<int:transaction_id>/related", methods=["DELETE"]
)
@jwt_required()
def delete_related_transactions(transaction_id):
    """Delete a transaction and all its related transactions (same date and payee)"""
    current_app.logger.debug(
        f"Entered delete_related_transactions route for ID: {transaction_id}"
    )
    try:
        # Find the transaction to identify related ones
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {current_user.id}"
            )
            return jsonify({"error": "Transaction not found"}), 404

        # Find all transactions with the same date and payee
        related_transactions = Transaction.query.filter_by(
            user_id=current_user.id, date=transaction.date, payee=transaction.payee
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
            account = db.session.get(Account, tx.account_id)

            if account:
                # Reverse the effect based on account type
                if account.type.lower() in ["liability", "equity", "income"]:
                    account.balance += tx.amount
                else:
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
