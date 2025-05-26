from typing import Dict, List, Optional, Tuple

from flask import current_app, g
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Account, Transaction
from app.shared.services import get_active_book_id
from app.utils.logging_utils import (
    log_business_logic,
    log_db_error,
    log_debug,
    log_service_entry,
    log_service_exit,
)


class AccountService:
    """Service layer for account operations."""

    @staticmethod
    def get_accounts(include_details: bool = False) -> List[Dict]:
        """Get all accounts for the current user and active book."""
        log_service_entry(
            "AccountService", "get_accounts", include_details=include_details
        )

        active_book_id = get_active_book_id()

        log_debug(
            "Querying accounts for user and active book",
            extra_data={
                "user_id": g.current_user.id,
                "active_book_id": active_book_id,
                "include_details": include_details,
            },
            module_name="AccountService",
        )

        accounts_list = Account.query.filter_by(
            user_id=g.current_user.id, book_id=active_book_id
        ).all()

        log_debug(
            "Retrieved accounts from database",
            extra_data={
                "user_id": g.current_user.id,
                "account_count": len(accounts_list),
                "include_details": include_details,
            },
            module_name="AccountService",
        )

        if include_details:
            # Return full account details
            result = [account.to_dict() for account in accounts_list]
            log_service_exit(
                "AccountService",
                "get_accounts",
                f"returned {len(result)} detailed accounts",
            )
            return result
        else:
            # For Add Transaction dropdown, we just need the account names
            result = [account.name for account in accounts_list]
            log_service_exit(
                "AccountService",
                "get_accounts",
                f"returned {len(result)} account names",
            )
            return result

    @staticmethod
    def get_account_by_id(account_id: int) -> Optional[Account]:
        """Get a specific account by ID."""
        log_service_entry("AccountService", "get_account_by_id", account_id=account_id)

        active_book_id = get_active_book_id()

        log_debug(
            "Querying specific account by ID",
            extra_data={
                "user_id": g.current_user.id,
                "account_id": account_id,
                "active_book_id": active_book_id,
            },
            module_name="AccountService",
        )

        account = Account.query.filter_by(
            id=account_id, user_id=g.current_user.id, book_id=active_book_id
        ).first()

        if account:
            log_debug(
                "Account found",
                extra_data={"account_id": account_id, "account_name": account.name},
                module_name="AccountService",
            )
            log_service_exit("AccountService", "get_account_by_id", "account found")
        else:
            log_debug(
                "Account not found",
                extra_data={"account_id": account_id},
                module_name="AccountService",
            )
            log_service_exit("AccountService", "get_account_by_id", "account not found")

        return account

    @staticmethod
    def create_account(data: Dict) -> Tuple[bool, str, Optional[Account]]:
        """Create a new account in the active book."""
        log_service_entry(
            "AccountService", "create_account", account_name=data.get("name")
        )

        # Validate required fields
        if "name" not in data:
            log_debug(
                "Account creation validation failed: missing name",
                extra_data={"provided_fields": list(data.keys())},
                module_name="AccountService",
            )
            log_service_exit("AccountService", "create_account", "validation failed")
            return False, "Missing required field: name", None

        user_id = g.current_user.id
        active_book_id = get_active_book_id()

        log_debug(
            "Creating new account",
            extra_data={
                "user_id": user_id,
                "active_book_id": active_book_id,
                "account_name": data["name"],
                "currency": data.get("currency", "INR"),
                "balance": data.get("balance", 0.0),
            },
            module_name="AccountService",
        )

        # Check if account with the same name already exists in this book
        existing = Account.query.filter_by(
            user_id=user_id, book_id=active_book_id, name=data["name"]
        ).first()

        if existing:
            log_debug(
                "Account creation failed: name already exists",
                extra_data={
                    "user_id": user_id,
                    "account_name": data["name"],
                    "existing_account_id": existing.id,
                },
                module_name="AccountService",
            )
            log_service_exit("AccountService", "create_account", "name conflict")
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

            log_business_logic(
                "Account created successfully",
                extra_data={
                    "user_id": user_id,
                    "account_id": account.id,
                    "account_name": account.name,
                    "currency": account.currency,
                    "balance": account.balance,
                },
                module_name="AccountService",
            )

            log_service_exit("AccountService", "create_account", "success")
            return True, "Account created successfully", account

        except SQLAlchemyError as e:
            db.session.rollback()
            log_db_error(e, operation="create", model="Account")
            log_service_exit("AccountService", "create_account", "database error")
            return False, "Database error occurred", None

    @staticmethod
    def update_account(
        account_id: int, data: Dict
    ) -> Tuple[bool, str, Optional[Account]]:
        """Update an account."""
        log_service_entry(
            "AccountService",
            "update_account",
            account_id=account_id,
            fields_to_update=list(data.keys()),
        )

        active_book_id = get_active_book_id()
        account = Account.query.filter_by(
            id=account_id, user_id=g.current_user.id, book_id=active_book_id
        ).first()

        if not account:
            log_debug(
                "Account update failed: account not found",
                extra_data={"account_id": account_id, "user_id": g.current_user.id},
                module_name="AccountService",
            )
            log_service_exit("AccountService", "update_account", "account not found")
            return False, "Account not found", None

        log_debug(
            "Updating account",
            extra_data={
                "account_id": account_id,
                "current_name": account.name,
                "fields_to_update": list(data.keys()),
            },
            module_name="AccountService",
        )

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
                    log_debug(
                        "Account update failed: name already exists",
                        extra_data={
                            "account_id": account_id,
                            "new_name": data["name"],
                            "existing_account_id": existing.id,
                        },
                        module_name="AccountService",
                    )
                    log_service_exit(
                        "AccountService", "update_account", "name conflict"
                    )
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

            log_business_logic(
                "Account updated successfully",
                extra_data={
                    "account_id": account_id,
                    "account_name": account.name,
                    "updated_fields": list(data.keys()),
                },
                module_name="AccountService",
            )

            log_service_exit("AccountService", "update_account", "success")
            return True, "Account updated successfully", account

        except SQLAlchemyError as e:
            db.session.rollback()
            log_db_error(e, operation="update", model="Account", record_id=account_id)
            log_service_exit("AccountService", "update_account", "database error")
            return False, "Database error occurred", None

    @staticmethod
    def delete_account(account_id: int) -> Tuple[bool, str]:
        """Delete an account."""
        log_service_entry("AccountService", "delete_account", account_id=account_id)

        active_book_id = get_active_book_id()
        account = Account.query.filter_by(
            id=account_id, user_id=g.current_user.id, book_id=active_book_id
        ).first()

        if not account:
            log_debug(
                "Account deletion failed: account not found",
                extra_data={"account_id": account_id, "user_id": g.current_user.id},
                module_name="AccountService",
            )
            log_service_exit("AccountService", "delete_account", "account not found")
            return False, "Account not found"

        # Check if there are any transactions associated with this account
        transactions_count = Transaction.query.filter_by(account_id=account_id).count()

        log_debug(
            "Checking for associated transactions",
            extra_data={
                "account_id": account_id,
                "account_name": account.name,
                "transactions_count": transactions_count,
            },
            module_name="AccountService",
        )

        if transactions_count > 0:
            log_debug(
                "Account deletion failed: has associated transactions",
                extra_data={
                    "account_id": account_id,
                    "transactions_count": transactions_count,
                },
                module_name="AccountService",
            )
            log_service_exit("AccountService", "delete_account", "has transactions")
            return (
                False,
                "Cannot delete account with existing transactions. Please delete or reassign transactions first.",
            )

        try:
            db.session.delete(account)
            db.session.commit()

            log_business_logic(
                "Account deleted successfully",
                extra_data={"account_id": account_id, "account_name": account.name},
                module_name="AccountService",
            )

            log_service_exit("AccountService", "delete_account", "success")
            return True, "Account deleted successfully"

        except SQLAlchemyError as e:
            db.session.rollback()
            log_db_error(e, operation="delete", model="Account", record_id=account_id)
            log_service_exit("AccountService", "delete_account", "database error")
            return False, "Database error occurred"

    @staticmethod
    def autocomplete_accounts(prefix: str, limit: int = 20) -> Tuple[List[str], str]:
        """Get account names for auto-completion based on a prefix."""
        log_service_entry(
            "AccountService", "autocomplete_accounts", prefix=prefix, limit=limit
        )

        if not prefix:
            log_debug(
                "Empty prefix provided for autocomplete", module_name="AccountService"
            )
            log_service_exit("AccountService", "autocomplete_accounts", "empty prefix")
            return [], prefix

        # Only activate auto-completion if prefix contains at least one colon
        if ":" not in prefix:
            log_debug(
                "Prefix does not contain colon, skipping autocomplete",
                extra_data={"prefix": prefix},
                module_name="AccountService",
            )
            log_service_exit(
                "AccountService", "autocomplete_accounts", "no colon in prefix"
            )
            return [], prefix

        active_book_id = get_active_book_id()

        log_debug(
            "Performing account autocomplete",
            extra_data={
                "user_id": g.current_user.id,
                "active_book_id": active_book_id,
                "prefix": prefix,
                "limit": limit,
            },
            module_name="AccountService",
        )

        accounts_list = Account.query.filter_by(
            user_id=g.current_user.id, book_id=active_book_id
        ).all()

        account_names = [account.name for account in accounts_list]

        # Filter accounts that start with the prefix
        matching_accounts = [
            name for name in account_names if name.lower().startswith(prefix.lower())
        ]

        log_debug(
            "Autocomplete results",
            extra_data={
                "prefix": prefix,
                "total_accounts": len(account_names),
                "matching_accounts": len(matching_accounts),
                "matches": matching_accounts[:5],  # Log first 5 matches
            },
            module_name="AccountService",
        )

        # Generate next segment suggestions
        next_segment_suggestions = set()

        # If prefix ends with colon, suggest next segments
        if prefix.endswith(":"):
            for name in account_names:
                if name.lower().startswith(prefix.lower()):
                    remaining = name[len(prefix) :]
                    if ":" in remaining:
                        next_segment = remaining.split(":")[0]
                        if next_segment:
                            next_segment_suggestions.add(prefix + next_segment + ":")
                    else:
                        if remaining:
                            next_segment_suggestions.add(name)
        else:
            # Find the last colon and suggest completions for the current segment
            last_colon_index = prefix.rfind(":")
            if last_colon_index != -1:
                base_prefix = prefix[: last_colon_index + 1]
                current_segment = prefix[last_colon_index + 1 :]

                for name in account_names:
                    if name.lower().startswith(base_prefix.lower()):
                        remaining = name[len(base_prefix) :]
                        if ":" in remaining:
                            next_segment = remaining.split(":")[0]
                            if next_segment.lower().startswith(current_segment.lower()):
                                next_segment_suggestions.add(
                                    base_prefix + next_segment + ":"
                                )
                        else:
                            if remaining.lower().startswith(current_segment.lower()):
                                next_segment_suggestions.add(name)

        suggestions = list(next_segment_suggestions)[:limit]

        log_debug(
            "Generated autocomplete suggestions",
            extra_data={
                "prefix": prefix,
                "suggestions_count": len(suggestions),
                "suggestions": suggestions[:5],  # Log first 5 suggestions
            },
            module_name="AccountService",
        )

        log_service_exit(
            "AccountService",
            "autocomplete_accounts",
            f"returned {len(suggestions)} suggestions",
        )
        return suggestions, prefix
