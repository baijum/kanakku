from typing import Dict, List, Optional, Tuple

from flask import current_app, g
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Account, Transaction
from app.shared.services import get_active_book_id


class AccountService:
    """Service layer for account operations."""

    @staticmethod
    def get_accounts(include_details: bool = False) -> List[Dict]:
        """Get all accounts for the current user and active book."""
        current_app.logger.debug("Getting accounts from service layer")

        active_book_id = get_active_book_id()
        accounts_list = Account.query.filter_by(
            user_id=g.current_user.id, book_id=active_book_id
        ).all()

        if include_details:
            # Return full account details
            return [account.to_dict() for account in accounts_list]
        else:
            # For Add Transaction dropdown, we just need the account names
            return [account.name for account in accounts_list]

    @staticmethod
    def get_account_by_id(account_id: int) -> Optional[Account]:
        """Get a specific account by ID."""
        current_app.logger.debug(f"Getting account {account_id} from service layer")

        active_book_id = get_active_book_id()
        return Account.query.filter_by(
            id=account_id, user_id=g.current_user.id, book_id=active_book_id
        ).first()

    @staticmethod
    def create_account(data: Dict) -> Tuple[bool, str, Optional[Account]]:
        """Create a new account in the active book."""
        current_app.logger.debug("Creating account from service layer")

        # Validate required fields
        if "name" not in data:
            return False, "Missing required field: name", None

        user_id = g.current_user.id
        active_book_id = get_active_book_id()

        # Check if account with the same name already exists in this book
        existing = Account.query.filter_by(
            user_id=user_id, book_id=active_book_id, name=data["name"]
        ).first()

        if existing:
            return False, "Account with this name already exists in this book", None

        try:
            # Create the account
            account = Account(
                user_id=user_id,
                book_id=active_book_id,
                name=data["name"],
                description=data.get("description", ""),
                currency=data.get("currency", "INR"),
                balance=data.get("balance", 0.0),
            )

            db.session.add(account)
            db.session.commit()

            current_app.logger.info(f"Account '{data['name']}' created successfully")
            return True, "Account created successfully", account

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error creating account: {str(e)}", exc_info=True
            )
            return False, "Database error occurred", None

    @staticmethod
    def update_account(
        account_id: int, data: Dict
    ) -> Tuple[bool, str, Optional[Account]]:
        """Update an account."""
        current_app.logger.debug(f"Updating account {account_id} from service layer")

        active_book_id = get_active_book_id()
        account = Account.query.filter_by(
            id=account_id, user_id=g.current_user.id, book_id=active_book_id
        ).first()

        if not account:
            return False, "Account not found", None

        try:
            if "name" in data:
                # Ensure name is unique in this book
                existing = Account.query.filter(
                    Account.user_id == g.current_user.id,
                    Account.book_id == active_book_id,
                    Account.name == data["name"],
                    Account.id != account_id,
                ).first()

                if existing:
                    return (
                        False,
                        "Account with this name already exists in this book",
                        None,
                    )

                account.name = data["name"]

            if "description" in data:
                account.description = data["description"]
            if "currency" in data:
                account.currency = data["currency"]
            if "balance" in data:
                account.balance = data["balance"]

            db.session.commit()

            current_app.logger.info(f"Account ID {account_id} updated successfully")
            return True, "Account updated successfully", account

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error updating account: {str(e)}", exc_info=True
            )
            return False, "Database error occurred", None

    @staticmethod
    def delete_account(account_id: int) -> Tuple[bool, str]:
        """Delete an account."""
        current_app.logger.debug(f"Deleting account {account_id} from service layer")

        active_book_id = get_active_book_id()
        account = Account.query.filter_by(
            id=account_id, user_id=g.current_user.id, book_id=active_book_id
        ).first()

        if not account:
            return False, "Account not found"

        # Check if there are any transactions associated with this account
        transactions_count = Transaction.query.filter_by(account_id=account_id).count()
        if transactions_count > 0:
            return (
                False,
                "Cannot delete account with existing transactions. Please delete or reassign transactions first.",
            )

        try:
            db.session.delete(account)
            db.session.commit()

            current_app.logger.info(f"Account ID {account_id} deleted successfully")
            return True, "Account deleted successfully"

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error deleting account: {str(e)}", exc_info=True
            )
            return False, "Database error occurred"

    @staticmethod
    def autocomplete_accounts(prefix: str, limit: int = 20) -> Tuple[List[str], str]:
        """Get account names for auto-completion based on a prefix."""
        current_app.logger.debug(f"Autocompleting accounts with prefix: {prefix}")

        if not prefix:
            return [], prefix

        # Only activate auto-completion if prefix contains at least one colon
        if ":" not in prefix:
            return [], prefix

        active_book_id = get_active_book_id()
        accounts_list = Account.query.filter_by(
            user_id=g.current_user.id, book_id=active_book_id
        ).all()

        account_names = [account.name for account in accounts_list]

        # Filter accounts that start with the prefix
        matching_accounts = [
            name for name in account_names if name.lower().startswith(prefix.lower())
        ]

        # Generate next segment suggestions
        next_segment_suggestions = set()

        # If prefix ends with colon, suggest next segments
        if prefix.endswith(":"):
            for name in account_names:
                if name.lower().startswith(prefix.lower()):
                    # Find the next segment after the prefix
                    remaining = name[len(prefix) :]
                    if ":" in remaining:
                        next_segment = remaining.split(":")[0]
                        next_segment_suggestion = prefix + next_segment
                        if next_segment_suggestion not in matching_accounts:
                            next_segment_suggestions.add(next_segment_suggestion)
        else:
            # If prefix doesn't end with colon, suggest partial segments
            prefix_parts = prefix.split(":")
            current_depth = len(prefix_parts)

            for name in account_names:
                name_parts = name.split(":")
                if len(name_parts) >= current_depth and name.lower().startswith(
                    prefix.lower()
                ):
                    # Suggest the segment at current depth
                    if len(name_parts) > current_depth:
                        next_segment = ":".join(name_parts[: current_depth + 1])
                        if (
                            next_segment != prefix
                            and next_segment not in matching_accounts
                        ):
                            next_segment_suggestions.add(next_segment)

        # Combine all suggestions
        all_suggestions = list(set(matching_accounts + list(next_segment_suggestions)))
        all_suggestions.sort()

        return all_suggestions[:limit], prefix
