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

# If these routes are API endpoints, they should likely use @jwt_required()
# and current_user from flask_jwt_extended instead of flask_login
# @ledger.route('/transactions', methods=['GET'])
# @login_required
# def get_transactions():
#     transactions = Transaction.query.filter_by(user_id=current_user.id).all()
#     return jsonify([{...} for t in transactions]), 200

# @ledger.route('/transactions', methods=['POST'])
# @login_required
# def create_transaction():
#     data = request.get_json()
#     transaction = Transaction(user_id=current_user.id, ...)
#     db.session.add(transaction)
#     db.session.commit()
#     return jsonify({...}), 201

# @ledger.route('/accounts', methods=['GET'])
# @login_required
# def get_accounts():
#     accounts = Account.query.filter_by(user_id=current_user.id).all()
#     return jsonify([{...} for a in accounts]), 200

# @ledger.route('/accounts', methods=['POST'])
# @login_required
# def create_account():
#     data = request.get_json()
#     account = Account(user_id=current_user.id, ...)
#     db.session.add(account)
#     db.session.commit()
#     return jsonify({...}), 201

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
            
            posting = f"    {account_name}    {amt_str} {transaction.currency}"
            
            # Create a single entry with a line break between transactions
            entry = f"{header}\n{posting}\n"
            ledger_output.append(entry)

        # Join with an empty string (not newline) as entries already have trailing newlines
        return Response("".join(ledger_output), mimetype='text/plain')

    except Exception as e:
        logging.error(f"Error generating ledger format: {e}")
        return jsonify({'error': 'Failed to generate ledger format'}), 500

# @ledger.route('/balance', methods=['GET'])
# @login_required
# def get_balance():
#     cmd_args = ['balance']
#     if 'account' in request.args:
#         cmd_args.append(request.args['account'])
#     if 'depth' in request.args:
#         cmd_args.extend(['--depth', request.args['depth']])
#         
#     output = run_ledger_command(cmd_args)
#     return jsonify({'balance': output}), 200

# @ledger.route('/reports/balance', methods=['GET'])
# @login_required
# def get_balance_report():
#     cmd_args = ['balance']
#     if 'account' in request.args:
#         cmd_args.append(request.args['account'])
#     if 'depth' in request.args:
#         cmd_args.extend(['--depth', request.args['depth']])
#         
#     output = run_ledger_command(cmd_args)
#     return jsonify({'balance': output}), 200

# @ledger.route('/reports/register', methods=['GET'])
# @login_required
# def get_register():
#     cmd_args = ['register']
#     if 'account' in request.args:
#         cmd_args.append(request.args['account'])
#     if 'limit' in request.args:
#         cmd_args.extend(['--limit', request.args['limit']])
#         
#     output = run_ledger_command(cmd_args)
#     return jsonify({'register': output}), 200
