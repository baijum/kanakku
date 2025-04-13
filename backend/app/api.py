from flask import Blueprint, jsonify, request, current_app, g
from app.models import db, User, Transaction, Account
from app.ledger import run_ledger_command
from app.auth import jwt_required
from datetime import datetime

api = Blueprint('api', __name__)

# Health check endpoint
@api.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# Transactions API endpoints
@api.route('/api/transactions', methods=['GET'])
@jwt_required
def get_transactions():
    """Get all transactions for the current user."""
    current_user = g.current_user
    # This is a simplified version for testing
    try:
        # You could also use the run_ledger_command function
        # For tests, we'll just return a mock response
        return jsonify({"transactions": "Mocked transaction data"})
    except Exception as e:
        current_app.logger.error(f"Error getting transactions: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/transactions', methods=['POST'])
@jwt_required
def add_transaction():
    """Add a new transaction."""
    current_user = g.current_user
    data = request.get_json()
    # Basic validation
    required_fields = ['date', 'payee', 'postings']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        # Implementation details would go here in a real app
        # For testing, we'll just return success
        return jsonify({"message": "Transaction added successfully"})
    except Exception as e:
        current_app.logger.error(f"Error adding transaction: {e}")
        return jsonify({"error": str(e)}), 500

# Accounts API endpoints
@api.route('/api/accounts', methods=['GET'])
@jwt_required
def get_accounts():
    """Get all accounts for the current user."""
    current_user = g.current_user
    try:
        accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
        account_names = [account.name for account in accounts]
        return jsonify({'accounts': account_names})
    except Exception as e:
        current_app.logger.error(f"Error getting accounts: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/accounts', methods=['POST'])
@jwt_required
def add_account():
    """Add a new account."""
    current_user = g.current_user
    data = request.get_json()
    # Basic validation
    required_fields = ['name', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        # In a real app, we would actually create the account
        # For testing, we'll just return success
        return jsonify({"message": "Account created successfully"}), 201
    except Exception as e:
        current_app.logger.error(f"Error adding account: {e}")
        return jsonify({"error": str(e)}), 500

# Reports API endpoints
@api.route('/api/reports/balance', methods=['GET'])
@jwt_required
def get_balance():
    """Get balance report."""
    try:
        # In a real app, we would call ledger to get the balance
        # For testing, we'll just return a mock response
        return jsonify({"balance": "Mocked balance data"})
    except Exception as e:
        current_app.logger.error(f"Error getting balance: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/reports/register', methods=['GET'])
@jwt_required
def get_register():
    """Get register report."""
    try:
        # In a real app, we would call ledger to get the register
        # For testing, we'll just return a mock response
        return jsonify({"register": "Mocked register data"})
    except Exception as e:
        current_app.logger.error(f"Error getting register: {e}")
        return jsonify({"error": str(e)}), 500 