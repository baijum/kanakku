from flask import Blueprint, current_app, g, jsonify, request

from app.models import Account, Book, Transaction

from .extensions import api_token_required, db

accounts = Blueprint("accounts", __name__)


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


@accounts.route("/api/v1/accounts", methods=["GET"])
@api_token_required
def get_accounts():
    current_app.logger.debug("Entered get_accounts route")
    """Get all accounts for the current user and active book."""
    active_book_id = get_active_book_id()
    accounts_list = Account.query.filter_by(
        user_id=g.current_user.id, book_id=active_book_id
    ).all()

    # For Add Transaction dropdown, we just need the account names
    account_names = [account.name for account in accounts_list]

    # Return in format expected by AddTransaction.js
    return jsonify({"accounts": account_names})

    # Original return format with full account details - commented out
    # return jsonify([account.to_dict() for account in accounts_list])


@accounts.route("/api/v1/accounts/details", methods=["GET"])
@api_token_required
def get_accounts_details():
    current_app.logger.debug("Entered get_accounts_details route")
    """Get all accounts with full details for the current user and active book."""
    active_book_id = get_active_book_id()
    accounts_list = Account.query.filter_by(
        user_id=g.current_user.id, book_id=active_book_id
    ).all()

    # Return full account details
    return jsonify([account.to_dict() for account in accounts_list])


@accounts.route("/api/v1/accounts", methods=["POST"])
@api_token_required
def create_account():
    current_app.logger.debug("Entered create_account route")
    """Create a new account in the active book."""
    data = request.get_json()

    if "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    # Use g.current_user
    user_id = g.current_user.id
    active_book_id = get_active_book_id()

    # Check if account with the same name already exists in this book
    existing = Account.query.filter_by(
        user_id=user_id, book_id=active_book_id, name=data["name"]
    ).first()

    if existing:
        return (
            jsonify({"error": "Account with this name already exists in this book"}),
            400,
        )

    # Create the account - use g.current_user.id and active book ID
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

    return (
        jsonify(
            {"message": "Account created successfully", "account": account.to_dict()}
        ),
        201,
    )


@accounts.route("/api/v1/accounts/<int:account_id>", methods=["GET"])
@api_token_required
def get_account(account_id):
    current_app.logger.debug(f"Entered get_account route for ID: {account_id}")
    """Get a specific account."""
    active_book_id = get_active_book_id()

    # Use g.current_user and active book
    account = Account.query.filter_by(
        id=account_id, user_id=g.current_user.id, book_id=active_book_id
    ).first_or_404()

    return jsonify(account.to_dict())


@accounts.route("/api/v1/accounts/<int:account_id>", methods=["PUT"])
@api_token_required
def update_account(account_id):
    current_app.logger.debug(f"Entered update_account route for ID: {account_id}")
    """Update an account."""
    data = request.get_json()
    active_book_id = get_active_book_id()

    # Use g.current_user and active book
    account = Account.query.filter_by(
        id=account_id, user_id=g.current_user.id, book_id=active_book_id
    ).first_or_404()

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
                jsonify(
                    {"error": "Account with this name already exists in this book"}
                ),
                400,
            )

        account.name = data["name"]

    if "description" in data:
        account.description = data["description"]
    if "currency" in data:
        account.currency = data["currency"]
    if "balance" in data:
        account.balance = data["balance"]

    db.session.commit()

    return jsonify(
        {"message": "Account updated successfully", "account": account.to_dict()}
    )


@accounts.route("/api/v1/accounts/<int:account_id>", methods=["DELETE"])
@api_token_required
def delete_account(account_id):
    current_app.logger.debug(f"Entered delete_account route for ID: {account_id}")
    """Delete an account."""
    active_book_id = get_active_book_id()

    # Use g.current_user and active book
    account = Account.query.filter_by(
        id=account_id, user_id=g.current_user.id, book_id=active_book_id
    ).first_or_404()

    # Check if there are any transactions associated with this account
    transactions_count = Transaction.query.filter_by(account_id=account_id).count()
    if transactions_count > 0:
        return (
            jsonify(
                {
                    "error": "Cannot delete account with existing transactions. Please delete or reassign transactions first."
                }
            ),
            400,
        )

    db.session.delete(account)
    db.session.commit()

    return jsonify({"message": "Account deleted successfully"})


@accounts.route("/api/v1/accounts/autocomplete", methods=["GET"])
@api_token_required
def autocomplete_accounts():
    """Get account names for auto-completion based on a prefix."""
    current_app.logger.debug("Entered autocomplete_accounts route")

    prefix = request.args.get("prefix", "").strip()
    limit = request.args.get("limit", 20, type=int)

    if not prefix:
        return jsonify({"suggestions": []})

    # Only activate auto-completion if prefix contains at least one colon
    if ":" not in prefix:
        return jsonify({"suggestions": []})

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
                    if next_segment != prefix and next_segment not in matching_accounts:
                        next_segment_suggestions.add(next_segment)

    # Combine all suggestions
    all_suggestions = list(set(matching_accounts + list(next_segment_suggestions)))
    all_suggestions.sort()

    return jsonify({"suggestions": all_suggestions[:limit], "prefix": prefix})
