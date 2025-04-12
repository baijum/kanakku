from flask import Blueprint, request, jsonify, g
from app.models import Account, db
from app.auth import jwt_required

accounts = Blueprint('accounts', __name__)

@accounts.route('/api/accounts', methods=['GET'])
@jwt_required
def get_accounts():
    """Get all accounts for the current user."""
    current_user = g.current_user
    accounts_list = Account.query.filter_by(user_id=current_user.id).all()
    
    return jsonify([
        {
            'id': account.id,
            'name': account.name,
            'type': account.type,
            'currency': account.currency,
            'balance': account.balance
        }
        for account in accounts_list
    ])

@accounts.route('/api/accounts', methods=['POST'])
@jwt_required
def create_account():
    """Create a new account."""
    data = request.get_json()
    
    if not all(key in data for key in ['name', 'type']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    current_user = g.current_user
    
    # Check if account with the same name already exists
    existing = Account.query.filter_by(user_id=current_user.id, name=data['name']).first()
    if existing:
        return jsonify({'error': 'Account with this name already exists'}), 400
    
    # Create the account
    account = Account(
        user_id=current_user.id,
        name=data['name'],
        type=data['type'],
        currency=data.get('currency', 'USD'),
        balance=data.get('balance', 0.0)
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': 'Account created successfully',
        'account': {
            'id': account.id,
            'name': account.name,
            'type': account.type,
            'currency': account.currency,
            'balance': account.balance
        }
    }), 201

@accounts.route('/api/accounts/<int:account_id>', methods=['GET'])
@jwt_required
def get_account(account_id):
    """Get a specific account."""
    current_user = g.current_user
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    return jsonify({
        'id': account.id,
        'name': account.name,
        'type': account.type,
        'currency': account.currency,
        'balance': account.balance
    })

@accounts.route('/api/accounts/<int:account_id>', methods=['PUT'])
@jwt_required
def update_account(account_id):
    """Update an account."""
    data = request.get_json()
    current_user = g.current_user
    
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    if 'name' in data:
        account.name = data['name']
    if 'type' in data:
        account.type = data['type']
    if 'currency' in data:
        account.currency = data['currency']
    if 'balance' in data:
        account.balance = data['balance']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Account updated successfully',
        'account': {
            'id': account.id,
            'name': account.name,
            'type': account.type,
            'currency': account.currency,
            'balance': account.balance
        }
    })

@accounts.route('/api/accounts/<int:account_id>', methods=['DELETE'])
@jwt_required
def delete_account(account_id):
    """Delete an account."""
    current_user = g.current_user
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'message': 'Account deleted successfully'}) 