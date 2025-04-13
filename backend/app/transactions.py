from flask import Blueprint, request, jsonify, current_app
from app.models import db, Transaction, Account
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
import traceback
import json

transactions = Blueprint('transactions', __name__)

@transactions.route('/api/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    try:
        # --- Start of main try block ---
        # Log the request for debugging
        current_app.logger.debug(f"Transaction request: {request.data}")
        
        try:
            data = request.get_json()
            if data is None:
                current_app.logger.error(f"Failed to parse JSON: {request.data}")
                return jsonify({'error': 'Request must be valid JSON'}), 400
        except Exception as json_error:
            current_app.logger.error(f"JSON parsing error: {str(json_error)}: {request.data}")
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        # --- More granular validation --- 
        if 'date' not in data:
            return jsonify({'error': 'Missing required field: date'}), 400
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': f"Invalid date format. Use YYYY-MM-DD."}), 400
            
        if 'description' not in data or not data['description']:
             return jsonify({'error': 'Missing required field: description'}), 400

        if 'amount' not in data:
             return jsonify({'error': 'Missing required field: amount'}), 400
        try:
            amount_float = float(data['amount'])
        except ValueError:
            return jsonify({'error': 'Invalid amount format. Must be a number.'}), 400

        if 'account_name' not in data or not data['account_name']:
             return jsonify({'error': 'Missing required field: account_name'}), 400
        # --- End granular validation ---
        
        # Access current_user *after* validation
        user = current_user 
        if not user:
            # Should not happen if @jwt_required() works
            return jsonify({'error': 'Authentication error: User not found'}), 401
            
        account = Account.query.filter_by(name=data['account_name'], user_id=user.id).first()
        if not account:
            return jsonify({'error': f"Account '{data['account_name']}' not found"}), 404
                
        new_transaction = Transaction(
            user_id=user.id,
            account_id=account.id,
            date=transaction_date,
            description=data['description'],
            payee=data.get('payee', ''),
            amount=amount_float, # Use the validated float
            currency=data.get('currency', 'USD')
        )
        
        db.session.add(new_transaction)
        
        try:
            db.session.commit()
            db.session.refresh(new_transaction)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({'error': 'Failed to save transaction'}), 500

        response_data = {
            'message': 'Transaction created successfully',
            'transaction': new_transaction.to_dict() # Use to_dict here too
        }
        current_app.logger.debug(f"Transaction response: {json.dumps(response_data)}")
        return jsonify(response_data), 201
        # --- End of main try block ---

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(f"Unhandled error in create_transaction: {str(e)} - Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'An unexpected server error occurred'}), 500

@transactions.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        # Log request
        current_app.logger.debug(f"GET /api/transactions request with params: {request.args}")
        
        limit = request.args.get('limit', type=int)
        
        query = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc())
        
        if limit:
            query = query.limit(limit)
            
        transactions_list = query.all()
        
        # Explicitly convert each transaction to a dictionary using its method
        output = [t.to_dict() for t in transactions_list]
        
        # Update account_name in the dictionaries after conversion
        for tx_dict in output:
            if tx_dict.get('account_id'):
                account = db.session.get(Account, tx_dict['account_id'])
                tx_dict['account_name'] = account.name if account else None
            else:
                tx_dict['account_name'] = None
                
        return jsonify(output)
    except Exception as e:
        current_app.logger.error(f"Error in get_transactions: {str(e)} - Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to retrieve transactions'}), 500 