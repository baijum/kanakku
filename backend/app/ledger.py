from flask import Blueprint, request, jsonify, Response, g
from .models import db, Account, Transaction, Preamble
from .extensions import api_token_required
import logging
from datetime import datetime

# from flask_login import login_required, current_user # Keep if used elsewhere

ledger = Blueprint("ledger", __name__)


@ledger.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@ledger.route("/api/v1/ledgertransactions", methods=["GET"])
@api_token_required
def get_transactions_ledger_format():
    """Return all transactions for the logged-in user in ledger format."""
    try:
        # Use g.current_user populated by the decorator
        user = g.current_user
        if not user:
            # This check is technically redundant if decorator works, but safe
            return jsonify({"error": "Authentication required"}), 401

        # Get preamble id if provided in query params
        preamble_id = request.args.get("preamble_id")
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")

        # Get preamble content
        preamble_content = ""
        if preamble_id:
            # Get specific preamble if ID provided - use g.current_user.id
            preamble = Preamble.query.filter_by(id=preamble_id, user_id=user.id).first()
            if preamble:
                preamble_content = preamble.content + "\n\n"
        else:
            # Get first preamble instead of default - use g.current_user.id
            first_preamble = Preamble.query.filter_by(user_id=user.id).first()
            if first_preamble:
                preamble_content = first_preamble.content + "\n\n"

        # Start building the query
        query = (
            db.session.query(Transaction, Account.name)
            .join(Account, Transaction.account_id == Account.id)
            .filter(Transaction.user_id == user.id)
        )

        # Apply date filters if provided
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(Transaction.date >= start_date_obj)
            except ValueError:
                logging.error(f"Invalid start date format: {start_date}")

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(Transaction.date <= end_date_obj)
            except ValueError:
                logging.error(f"Invalid end date format: {end_date}")

        # Complete the query with ordering
        transactions = query.order_by(Transaction.date.asc()).all()

        if not transactions and not preamble_content:
            return Response(
                "", mimetype="text/plain"
            )  # Return empty if no transactions and no preamble

        # Group transactions by date and description
        transaction_groups = {}
        for transaction, account_name in transactions:
            key = (transaction.date.strftime("%Y-%m-%d"), transaction.description)
            if key not in transaction_groups:
                transaction_groups[key] = []

            # Format amount with currency
            amt_str = f"{transaction.amount:.2f}"
            if transaction.currency in ("INR", "₹"):
                posting = f"    {account_name}    ₹{amt_str}"
            else:
                posting = f"    {account_name}    {amt_str} {transaction.currency}"

            transaction_groups[key].append(posting)

        # Format output with grouped transactions
        ledger_output = []
        for (date, description), postings in transaction_groups.items():
            # Get the transaction to access its status
            # We need to get the first transaction in the group to determine the status
            first_transaction = next(
                (
                    t
                    for t, a in transactions
                    if t.date.strftime("%Y-%m-%d") == date
                    and t.description == description
                ),
                None,
            )

            # Create header with the correct status
            if first_transaction and first_transaction.status:
                header = f"{date} {first_transaction.status} {description}"
            else:
                header = f"{date} {description}"

            # Add all postings under this header
            entry = f"{header}\n{chr(10).join(postings)}\n"
            ledger_output.append(entry)

        # Join with an empty string (not newline) as entries already have trailing newlines
        # Add preamble at the beginning
        return Response(
            preamble_content + "".join(ledger_output), mimetype="text/plain"
        )

    except Exception as e:
        logging.error(f"Error generating ledger format: {e}")
        return jsonify({"error": "Failed to generate ledger format"}), 500
