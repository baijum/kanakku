from datetime import datetime
from typing import Dict, List, Optional, Tuple

from flask import current_app, g
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Account, Transaction
from app.shared.services import get_active_book_id


class TransactionService:
    """Service layer for transaction operations."""

    @staticmethod
    def validate_transaction_data(data: Dict) -> Tuple[bool, str]:
        """Validate transaction data and return (is_valid, error_message)."""
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
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        # Validate date format
        try:
            datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."

        # Validate that a single transaction doesn't debit and credit the same account
        account_directions = {}
        for posting in data["postings"]:
            account_name = posting.get("account")
            amount_str = posting.get("amount")
            if not account_name or amount_str is None:
                continue
            try:
                amount_float = float(amount_str)
                if amount_float == 0:
                    continue

                direction = "debit" if amount_float > 0 else "credit"

                if account_name not in account_directions:
                    account_directions[account_name] = direction
                elif account_directions[account_name] != direction:
                    return (
                        False,
                        f"Cannot debit and credit the same account '{account_name}' in a single transaction.",
                    )
            except ValueError:
                continue

        return True, ""

    @staticmethod
    def validate_posting_data(posting: Dict) -> Tuple[bool, str, float]:
        """Validate posting data and return (is_valid, error_message, amount)."""
        if "account" not in posting or not posting["account"]:
            return False, "Missing account name in posting", 0.0

        if "amount" not in posting or posting["amount"] == "":
            return False, "Missing amount in posting", 0.0

        try:
            amount_float = float(posting["amount"])
            return True, "", amount_float
        except ValueError:
            return False, "Invalid amount format. Must be a number.", 0.0

    @staticmethod
    def create_transaction(data: Dict) -> Tuple[bool, str, List[Transaction]]:
        """Create a new transaction from the provided data."""
        current_app.logger.info("Processing transaction creation request")

        active_book_id = get_active_book_id()
        user = g.current_user

        # Validate transaction data
        is_valid, error_msg = TransactionService.validate_transaction_data(data)
        if not is_valid:
            current_app.logger.warning(f"Validation error: {error_msg}")
            return False, error_msg, []

        # Parse date
        transaction_date = datetime.strptime(data["date"], "%Y-%m-%d").date()

        # Process each posting
        transaction_responses = []

        try:
            for posting in data["postings"]:
                # Validate posting
                is_valid, error_msg, amount_float = (
                    TransactionService.validate_posting_data(posting)
                )
                if not is_valid:
                    return False, error_msg, []

                # Find the account in the active book
                account_name = posting["account"]
                account = Account.query.filter_by(
                    name=account_name, user_id=user.id, book_id=active_book_id
                ).first()

                if not account:
                    current_app.logger.error(f"Account not found: {account_name}")
                    return False, "Account not found in the active book", []

                # Create transaction object within the active book
                new_transaction = Transaction(
                    user_id=user.id,
                    book_id=active_book_id,
                    account_id=account.id,
                    date=transaction_date,
                    description=data["payee"],
                    payee=data["payee"],
                    amount=amount_float,
                    currency=posting.get("currency", "INR"),
                    status=data.get("status"),
                )

                # Update the account balance
                account.balance += amount_float

                db.session.add(new_transaction)
                transaction_responses.append(new_transaction)

            # Commit all transactions together
            db.session.commit()
            # Refresh the objects to get updated values
            for tx in transaction_responses:
                db.session.refresh(tx)

            current_app.logger.info(
                f"Transaction created successfully: {len(transaction_responses)} entries"
            )
            return True, "Transaction created successfully", transaction_responses

        except SQLAlchemyError as db_error:
            db.session.rollback()
            current_app.logger.error(
                f"Database error during transaction save: {str(db_error)}",
                exc_info=True,
            )
            return False, f"Failed to save transaction: {str(db_error)}", []

    @staticmethod
    def get_transactions(
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search_term: str = "",
        offset: int = 0,
        book_id: Optional[int] = None,
    ) -> Tuple[List[Dict], int]:
        """Get transactions with filtering and pagination."""
        current_app.logger.debug("Entered get_transactions service")

        # Use provided book_id or get active book
        if book_id is None:
            book_id = get_active_book_id()

        # Start with base query
        query = Transaction.query.filter_by(user_id=g.current_user.id, book_id=book_id)

        # Apply search filter if provided
        if search_term:
            query = TransactionService._apply_search_filter(query, search_term)

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

        # Group transactions by date and payee
        formatted_transactions = TransactionService._group_transactions(
            transactions_list
        )

        return formatted_transactions, total_count

    @staticmethod
    def _apply_search_filter(query, search_term: str):
        """Apply search filter to query based on database type."""
        # Check if we're using PostgreSQL (FTS only works with PostgreSQL)
        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "").lower()
        if "postgresql" in db_url:
            # Convert search term to tsquery with prefix matching for last word
            search_words = search_term.split()
            if search_words:
                tsquery_parts = []
                for i, word in enumerate(search_words):
                    # Sanitize word by removing special characters that break tsquery
                    sanitized_word = "".join(
                        c for c in word if c.isalnum() or c in "-_"
                    )
                    if sanitized_word:
                        if i == len(search_words) - 1:  # Last word gets prefix matching
                            tsquery_parts.append(f"{sanitized_word}:*")
                        else:
                            tsquery_parts.append(sanitized_word)

                if tsquery_parts:
                    search_query = " & ".join(tsquery_parts)
                    current_app.logger.debug(f"Search query: {search_query}")

                    try:
                        query = query.filter(
                            Transaction.search_vector.op("@@")(
                                func.to_tsquery("english", search_query)
                            )
                        )
                    except Exception as e:
                        # If tsquery fails, fall back to basic text search
                        current_app.logger.warning(
                            f"FTS query failed, falling back to basic search: {e}"
                        )
                        search_filter = f"%{search_term}%"
                        query = query.filter(
                            or_(
                                Transaction.description.ilike(search_filter),
                                Transaction.payee.ilike(search_filter),
                                Transaction.currency.ilike(search_filter),
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
                    Transaction.currency.ilike(search_filter),
                )
            )
        return query

    @staticmethod
    def _group_transactions(transactions_list: List[Transaction]) -> List[Dict]:
        """Group transactions by date and payee to create the expected structure."""
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
                    "id": tx.id,
                    "date": tx.date.isoformat(),
                    "payee": tx.payee,
                    "status": tx.status or "",
                    "postings": [],
                }

            # Add posting to transaction group
            grouped_transactions[key]["postings"].append(
                {
                    "id": tx.id,
                    "account": account_name,
                    "amount": str(tx.amount),
                    "currency": tx.currency,
                }
            )

        return list(grouped_transactions.values())

    @staticmethod
    def get_transaction_by_id(transaction_id: int) -> Optional[Dict]:
        """Get a single transaction by ID."""
        current_app.logger.debug(f"Getting transaction {transaction_id}")

        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=g.current_user.id
        ).first()

        if not transaction:
            current_app.logger.warning(
                f"Transaction ID {transaction_id} not found for user ID {g.current_user.id}"
            )
            return None

        # Get account name
        if not transaction.account_id:
            current_app.logger.error("Transaction has no account_id")
            return None

        account = db.session.get(Account, transaction.account_id)
        if not account:
            current_app.logger.error("Account not found for transaction")
            return None
        account_name = account.name

        # Format the transaction
        return {
            "id": transaction.id,
            "date": transaction.date.isoformat(),
            "description": transaction.description,
            "payee": transaction.payee,
            "account_id": transaction.account_id,
            "account_name": account_name,
            "amount": float(
                transaction.amount
            ),  # Return as numeric for single transaction
            "currency": transaction.currency,
            "status": transaction.status or "",
            "book_id": transaction.book_id,
        }

    @staticmethod
    def update_transaction(
        transaction_id: int, data: Dict
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """Update a transaction."""
        current_app.logger.debug(f"Updating transaction {transaction_id}")

        try:
            # Find the transaction
            transaction = Transaction.query.filter_by(
                id=transaction_id, user_id=g.current_user.id
            ).first()

            if not transaction:
                return False, "Transaction not found", None

            # Get the account for balance adjustment
            account = db.session.get(Account, transaction.account_id)
            if not account:
                return False, "Associated account not found", None

            # Store old amount for balance adjustment
            old_amount = transaction.amount

            # Update transaction fields
            if "date" in data:
                try:
                    transaction.date = datetime.strptime(
                        data["date"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return False, "Invalid date format. Use YYYY-MM-DD.", None

            if "description" in data:
                transaction.description = data["description"]

            if "payee" in data:
                transaction.payee = data["payee"]
                # For backward compatibility, also update description if payee is updated
                transaction.description = data["payee"]

            if "amount" in data:
                try:
                    new_amount = float(data["amount"])
                    # Adjust account balance
                    account.balance = account.balance - old_amount + new_amount
                    transaction.amount = new_amount
                except ValueError:
                    return False, "Invalid amount format. Must be a number.", None

            if "currency" in data:
                transaction.currency = data["currency"]

            if "status" in data:
                transaction.status = data["status"]

            if "account_id" in data:
                new_account_id = data["account_id"]
                new_account = Account.query.filter_by(
                    id=new_account_id, user_id=g.current_user.id
                ).first()

                if not new_account:
                    return False, "Account not found", None

                # Update account balances when changing account
                if new_account_id != transaction.account_id:
                    # Remove amount from old account
                    old_account = db.session.get(Account, transaction.account_id)
                    if old_account:
                        old_account.balance -= transaction.amount

                    # Add amount to new account
                    new_account.balance += transaction.amount

                    # Update transaction's account_id
                    transaction.account_id = new_account_id

            db.session.commit()
            current_app.logger.info(
                f"Transaction ID {transaction_id} updated successfully"
            )
            return True, "Transaction updated successfully", transaction

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}", exc_info=True)
            return False, "Database error occurred", None

    @staticmethod
    def update_transaction_with_postings(
        transaction_id: int, data: Dict
    ) -> Tuple[bool, str, List[Transaction]]:
        """Update a transaction with multiple postings."""
        current_app.logger.debug(f"Updating transaction with postings {transaction_id}")

        try:
            # Find the original transaction to get date and payee
            original_transaction = Transaction.query.filter_by(
                id=transaction_id, user_id=g.current_user.id
            ).first()

            if not original_transaction:
                return False, "Transaction not found", []

            # Find all related transactions (same date and payee)
            related_transactions = Transaction.query.filter_by(
                user_id=g.current_user.id,
                date=original_transaction.date,
                payee=original_transaction.payee,
            ).all()

            # Reverse the balance effects of all related transactions
            for tx in related_transactions:
                account = db.session.get(Account, tx.account_id)
                if account:
                    account.balance -= tx.amount
                db.session.delete(tx)

            # Validate new transaction data
            is_valid, error_msg = TransactionService.validate_transaction_data(data)
            if not is_valid:
                db.session.rollback()
                return False, error_msg, []

            # Create new transactions
            success, message, new_transactions = TransactionService.create_transaction(
                data
            )
            if not success:
                db.session.rollback()
                return False, message, []

            current_app.logger.info(
                f"Transaction {transaction_id} updated with postings successfully"
            )
            return True, "Transaction updated successfully", new_transactions

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}", exc_info=True)
            return False, "Database error occurred", []

    @staticmethod
    def get_related_transactions(transaction_id: int) -> Optional[Dict]:
        """Get all transactions related to a given transaction (same date and payee)."""
        current_app.logger.debug(f"Getting related transactions for {transaction_id}")

        # Find the transaction to identify related ones
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=g.current_user.id
        ).first()

        if not transaction:
            return None

        # Find all transactions with the same date and payee
        related_transactions = Transaction.query.filter_by(
            user_id=g.current_user.id, date=transaction.date, payee=transaction.payee
        ).all()

        # Format transactions for the expected structure
        transactions_data = []
        for tx in related_transactions:
            # Get account name
            if not tx.account_id:
                current_app.logger.error("Transaction has no account_id")
                continue
            account = db.session.get(Account, tx.account_id)
            if not account:
                current_app.logger.error("Account not found for transaction")
                continue

            transactions_data.append(
                {
                    "id": tx.id,
                    "account": account.name,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "description": tx.description,
                    "payee": tx.payee,
                    "date": tx.date.isoformat(),
                    "status": tx.status or "",
                }
            )

        # Return in the expected format
        return {
            "date": transaction.date.isoformat(),
            "payee": transaction.payee,
            "primary_transaction_id": transaction_id,
            "transactions": transactions_data,
        }

    @staticmethod
    def delete_transaction(transaction_id: int) -> Tuple[bool, str]:
        """Delete a single transaction."""
        current_app.logger.debug(f"Deleting transaction {transaction_id}")

        try:
            transaction = Transaction.query.filter_by(
                id=transaction_id, user_id=g.current_user.id
            ).first()

            if not transaction:
                return False, "Transaction not found"

            # Get the account for balance adjustment
            account = db.session.get(Account, transaction.account_id)
            if account:
                account.balance -= transaction.amount

            db.session.delete(transaction)
            db.session.commit()

            current_app.logger.info(
                f"Transaction ID {transaction_id} deleted successfully"
            )
            return True, "Transaction deleted"

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}", exc_info=True)
            return False, "Database error occurred"

    @staticmethod
    def delete_related_transactions(transaction_id: int) -> Tuple[bool, str, int]:
        """Delete a transaction and all its related transactions (same date and payee)."""
        current_app.logger.debug(f"Deleting related transactions for {transaction_id}")

        try:
            # Find the transaction to identify related ones
            transaction = Transaction.query.filter_by(
                id=transaction_id, user_id=g.current_user.id
            ).first()

            if not transaction:
                return False, "Transaction not found", 0

            # Find all transactions with the same date and payee
            related_transactions = Transaction.query.filter_by(
                user_id=g.current_user.id,
                date=transaction.date,
                payee=transaction.payee,
            ).all()

            if not related_transactions:
                return False, "No transactions found to delete", 0

            deleted_count = 0

            # Undo account balance effects and delete each transaction
            for tx in related_transactions:
                account = db.session.get(Account, tx.account_id)
                if account:
                    account.balance -= tx.amount

                db.session.delete(tx)
                deleted_count += 1

            db.session.commit()
            current_app.logger.info(
                f"Deleted {deleted_count} related transactions for ID {transaction_id}"
            )
            return True, "Related transactions deleted successfully", deleted_count

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}", exc_info=True)
            return False, "Database error occurred", 0

    @staticmethod
    def get_recent_transactions(
        limit: int = 7, book_id: Optional[int] = None
    ) -> List[Dict]:
        """Get recent transactions, grouped by date and payee."""
        current_app.logger.debug("Getting recent transactions")

        # If book_id is not provided, use the active book
        if not book_id:
            book_id = get_active_book_id()

        # Fetch more raw transactions than we need to ensure we have enough after grouping
        fetch_limit = limit * 4

        # Start with base query
        query = Transaction.query.filter_by(user_id=g.current_user.id, book_id=book_id)

        # Apply ordering and limit
        query = query.order_by(Transaction.date.desc()).limit(fetch_limit)

        transactions_list = query.all()

        # Group transactions and limit to exactly the requested number
        formatted_transactions = TransactionService._group_transactions(
            transactions_list
        )
        return formatted_transactions[:limit]
