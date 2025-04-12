import os
import subprocess
from typing import List, Optional, Union
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import Transaction, Account
import logging

ledger = Blueprint('ledger', __name__)

def run_ledger_command(cmd_args: List[str], ledger_file: Optional[str] = None) -> str:
    """
    Run a ledger-cli command with given arguments.
    
    Args:
        cmd_args: List of command arguments to pass to ledger
        ledger_file: Optional path to the ledger file. If not provided, 
                     will use LEDGER_FILE environment variable.
    
    Returns:
        The stdout output of the ledger command as a string.
    
    Raises:
        Exception: If the ledger command fails to execute or returns an error.
    """
    # Get the ledger file path from env var if not provided
    if not ledger_file:
        ledger_file = os.environ.get('LEDGER_FILE')
        if not ledger_file:
            raise ValueError("LEDGER_FILE environment variable not set and no ledger_file provided")
    
    # Construct the command
    ledger_cmd = ['ledger', '-f', ledger_file]
    ledger_cmd.extend(cmd_args)
    
    try:
        # Execute the command and capture the output
        result = subprocess.run(
            ledger_cmd, 
            check=True,
            capture_output=True,
            text=True  # This automatically decodes output to string
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Log the error details for debugging
        logging.error(f"Ledger command failed: {e}")
        logging.error(f"Command: {' '.join(ledger_cmd)}")
        if e.stderr:
            logging.error(f"Error output: {e.stderr}")
        
        # Re-raise with more details
        raise Exception(f"Ledger command failed with code {e.returncode}: {e.stderr}")
    except Exception as e:
        logging.error(f"Error running ledger command: {e}")
        raise

@ledger.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200

@ledger.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': t.id,
        'date': t.date.isoformat(),
        'description': t.description,
        'amount': t.amount,
        'account_id': t.account_id
    } for t in transactions]), 200

@ledger.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    data = request.get_json()
    
    # Create transaction in database
    transaction = Transaction(
        user_id=current_user.id,
        account_id=data.get('account_id'),
        date=data['date'],
        description=data['description'],
        amount=data['amount'],
        payee=data.get('payee'),
        currency=data.get('currency', 'USD')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Add transaction to Ledger CLI
    ledger_command = f"ledger add {data['date']} {data['description']} {data['amount']}"
    stdout, stderr = run_ledger_command(ledger_command)
    
    if stderr:
        return jsonify({'error': f'Failed to add transaction to ledger: {stderr}'}), 500
        
    return jsonify({
        'message': 'Transaction created successfully',
        'transaction': {
            'id': transaction.id,
            'date': transaction.date.isoformat(),
            'description': transaction.description,
            'amount': transaction.amount,
            'account_id': transaction.account_id
        }
    }), 201

@ledger.route('/accounts', methods=['GET'])
@login_required
def get_accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'type': a.type,
        'balance': a.balance,
        'currency': a.currency
    } for a in accounts]), 200

@ledger.route('/accounts', methods=['POST'])
@login_required
def create_account():
    data = request.get_json()
    
    account = Account(
        user_id=current_user.id,
        name=data['name'],
        type=data['type'],
        balance=data.get('balance', 0),
        currency=data.get('currency', 'USD')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': 'Account created successfully',
        'account': {
            'id': account.id,
            'name': account.name,
            'type': account.type,
            'balance': account.balance,
            'currency': account.currency
        }
    }), 201

@ledger.route('/balance', methods=['GET'])
@login_required
def get_balance():
    cmd_args = ['balance']
    if 'account' in request.args:
        cmd_args.append(request.args['account'])
    if 'depth' in request.args:
        cmd_args.extend(['--depth', request.args['depth']])
        
    output = run_ledger_command(cmd_args)
    return jsonify({'balance': output}), 200

@ledger.route('/reports/balance', methods=['GET'])
@login_required
def get_balance_report():
    cmd_args = ['balance']
    if 'account' in request.args:
        cmd_args.append(request.args['account'])
    if 'depth' in request.args:
        cmd_args.extend(['--depth', request.args['depth']])
        
    output = run_ledger_command(cmd_args)
    return jsonify({'balance': output}), 200

@ledger.route('/reports/register', methods=['GET'])
@login_required
def get_register():
    cmd_args = ['register']
    if 'account' in request.args:
        cmd_args.append(request.args['account'])
    if 'limit' in request.args:
        cmd_args.extend(['--limit', request.args['limit']])
        
    output = run_ledger_command(cmd_args)
    return jsonify({'register': output}), 200
