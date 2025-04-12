from flask import Blueprint, request, jsonify, current_app, g
from app.models import db, Transaction, Account
from app.ledger import run_ledger_command
from app.auth import jwt_required
from datetime import datetime

transactions = Blueprint('transactions', __name__)

@transactions.route('/api/transactions', methods=['POST'])
@jwt_required
def create_transaction():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        current_user = g.current_user
        
        required_fields = ['date', 'description', 'amount', 'account_name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find the account
        account = Account.query.filter_by(name=data['account_name'], user_id=current_user.id).first()
        if not account:
            return jsonify({'error': f"Account '{data['account_name']}' not found"}), 404
                
        # Convert date string to date object
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({'error': f"Invalid date format. Use YYYY-MM-DD: {str(e)}"}), 400
            
        # Create the transaction in the database
        new_transaction = Transaction(
            user_id=current_user.id,
            account_id=account.id, # Link transaction to account
            date=transaction_date,
            description=data['description'],
            payee=data.get('payee', ''),  # Default to empty string if not provided
            amount=float(data['amount']),
            currency=data.get('currency', 'USD')
        )
        
        db.session.add(new_transaction)
        
        # Build ledger entry format
        try:
            ledger_entry = (
                f"{transaction_date.strftime('%Y/%m/%d')} * {data.get('payee', '')} | {data['description']}\n"
                f"    {account.name}    {float(data['amount']):.2f} {data.get('currency', 'USD')}\n"
                f"    Equity:Opening Balances  {-float(data['amount']):.2f} {data.get('currency', 'USD')}\n"
            )
            
            # Commit to database
            db.session.commit()
            db.session.refresh(new_transaction)
            
            return jsonify({
                'message': 'Transaction created successfully',
                'transaction': {
                    'id': new_transaction.id,
                    'date': new_transaction.date.isoformat(),
                    'description': new_transaction.description,
                    'payee': new_transaction.payee,
                    'amount': new_transaction.amount,
                    'currency': new_transaction.currency,
                    'account_name': account.name
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating transaction: {str(e)}")
            return jsonify({'error': f'Error creating transaction: {str(e)}'}), 500

    except ValueError as ve:
        return jsonify({'error': f'Invalid data format: {str(ve)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error creating transaction: {str(e)}")
        return jsonify({'error': 'Internal server error during transaction creation'}), 500

@transactions.route('/api/transactions', methods=['GET'])
@jwt_required
def get_transactions():
    current_user = g.current_user
    limit = request.args.get('limit', type=int)
    
    query = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc())
    
    if limit:
        query = query.limit(limit)
        
    transactions_list = query.all()
    
    output = []
    for t in transactions_list:
        transaction_dict = {
            'id': t.id,
            'date': t.date.isoformat(),
            'description': t.description,
            'payee': t.payee,
            'amount': t.amount,
            'currency': t.currency,
            'account_name': None  # Default to None
        }
        
        # Safely get account name if account_id exists
        if t.account_id:
            account = Account.query.get(t.account_id)
            if account:
                transaction_dict['account_name'] = account.name
                
        output.append(transaction_dict)
    
    return jsonify(output) 