from flask import Blueprint, request, jsonify, current_app, g
from app.models import Account, Transaction, db
from .extensions import api_token_required

accounts = Blueprint("accounts", __name__)


@accounts.route("/api/accounts", methods=["GET"])
@api_token_required
def get_accounts():
    current_app.logger.debug("Entered get_accounts route")
    """Get all accounts for the current user."""
    accounts_list = Account.query.filter_by(user_id=g.current_user.id).all()

    # For Add Transaction dropdown, we just need the account names
    account_names = [account.name for account in accounts_list]

    # Return in format expected by AddTransaction.js
    return jsonify({"accounts": account_names})

    # Original return format with full account details - commented out
    # return jsonify([account.to_dict() for account in accounts_list])


@accounts.route("/api/accounts/details", methods=["GET"])
@api_token_required
def get_accounts_details():
    current_app.logger.debug("Entered get_accounts_details route")
    """Get all accounts with full details for the current user."""
    accounts_list = Account.query.filter_by(user_id=g.current_user.id).all()

    # Return full account details
    return jsonify([account.to_dict() for account in accounts_list])


@accounts.route("/api/accounts", methods=["POST"])
@api_token_required
def create_account():
    current_app.logger.debug("Entered create_account route")
    """Create a new account."""
    data = request.get_json()

    if "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    # Use g.current_user
    user_id = g.current_user.id

    # Check if account with the same name already exists
    existing = Account.query.filter_by(user_id=user_id, name=data["name"]).first()
    if existing:
        return jsonify({"error": "Account with this name already exists"}), 400

    # Create the account - use g.current_user.id
    account = Account(
        user_id=user_id,
        name=data["name"],
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


@accounts.route("/api/accounts/<int:account_id>", methods=["GET"])
@api_token_required
def get_account(account_id):
    current_app.logger.debug(f"Entered get_account route for ID: {account_id}")
    """Get a specific account."""
    # Use g.current_user
    account = Account.query.filter_by(
        id=account_id, user_id=g.current_user.id
    ).first_or_404()

    return jsonify(account.to_dict())


@accounts.route("/api/accounts/<int:account_id>", methods=["PUT"])
@api_token_required
def update_account(account_id):
    current_app.logger.debug(f"Entered update_account route for ID: {account_id}")
    """Update an account."""
    data = request.get_json()

    # Use g.current_user
    account = Account.query.filter_by(
        id=account_id, user_id=g.current_user.id
    ).first_or_404()

    if "name" in data:
        account.name = data["name"]
    if "currency" in data:
        account.currency = data["currency"]
    if "balance" in data:
        account.balance = data["balance"]

    db.session.commit()

    return jsonify(
        {"message": "Account updated successfully", "account": account.to_dict()}
    )


@accounts.route("/api/accounts/<int:account_id>", methods=["DELETE"])
@api_token_required
def delete_account(account_id):
    current_app.logger.debug(f"Entered delete_account route for ID: {account_id}")
    """Delete an account."""
    # Use g.current_user
    account = Account.query.filter_by(
        id=account_id, user_id=g.current_user.id
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
