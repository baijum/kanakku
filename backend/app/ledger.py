import os
import subprocess
from typing import List, Optional, Union
from flask import Blueprint, request, jsonify, current_app, Response
# from flask_login import login_required, current_user # Keep if used elsewhere
from . import db
from .models import Transaction, Account
import logging
# Use standard flask_jwt_extended imports
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user

ledger = Blueprint('ledger', __name__)

@ledger.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200

@ledger.route('/api/v1/ledgertransactions', methods=['GET'])
@jwt_required() # Correct usage
def get_transactions_ledger_format():
    """Return all transactions for the logged-in user in ledger format."""
    try:
        # Use current_user proxy populated by user_lookup_loader
        # user_id = get_jwt_identity() <-- No longer needed directly
        user = current_user
        if not user:
            # This check might be redundant if @jwt_required() works correctly
            return jsonify({"error": "Authentication required"}), 401

        # Fetch transactions joined with account names for the user
        transactions = db.session.query(
            Transaction,
            Account.name
        ).join(Account, Transaction.account_id == Account.id) \
         .filter(Transaction.user_id == user.id) \
         .order_by(Transaction.date.asc()) \
         .all()

        if not transactions:
            return Response("", mimetype='text/plain') # Return empty if no transactions

        ledger_output = []
        for transaction, account_name in transactions:
            # Format: YYYY-MM-DD * Description [; Payee: <payee>]
            #          AccountName    Amount Currency
            header = f"{transaction.date.strftime('%Y-%m-%d')} * {transaction.description}"
            if transaction.payee:
                header += f" ; Payee: {transaction.payee}"
            
            # Ensure we use the negative sign to match test expectations
            amt_str = f"{transaction.amount:.2f}"

            # Format for currency - add rupee symbol for INR
            if transaction.currency in ('INR', '₹'):
                posting = f"    {account_name}    ₹{amt_str}"
            else:
                posting = f"    {account_name}    {amt_str} {transaction.currency}"
            
            # Create a single entry with a line break between transactions
            entry = f"{header}\n{posting}\n"
            ledger_output.append(entry)

        # Join with an empty string (not newline) as entries already have trailing newlines
        return Response("".join(ledger_output), mimetype='text/plain')

    except Exception as e:
        logging.error(f"Error generating ledger format: {e}")
        return jsonify({'error': 'Failed to generate ledger format'}), 500
