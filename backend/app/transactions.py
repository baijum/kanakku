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
    current_app.logger.debug("Entered create_transaction route")
    try:
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
            
        # Validate required top-level fields
        if 'date' not in data:
            return jsonify({'error': 'Missing required field: date'}), 400
        
        if 'payee' not in data or not data['payee']:
            return jsonify({'error': 'Missing required field: payee'}), 400
            
        if 'postings' not in data or not isinstance(data['postings'], list) or len(data['postings']) < 1:
            return jsonify({'error': 'Missing or invalid postings'}), 400
            
        # Validate date format
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': f"Invalid date format. Use YYYY-MM-DD."}), 400
        
        # Access current_user
        user = current_user 
        if not user:
            # Should not happen if @jwt_required() works
            return jsonify({'error': 'Authentication error: User not found'}), 401
            
        # Process each posting
        transaction_responses = []
        
        for posting in data['postings']:
            # Validate posting fields
            if 'account' not in posting or not posting['account']:
                return jsonify({'error': 'Missing account name in posting'}), 400
                
            if 'amount' not in posting or posting['amount'] == '':
                return jsonify({'error': 'Missing amount in posting'}), 400
                
            try:
                amount_float = float(posting['amount'])
            except ValueError:
                return jsonify({'error': 'Invalid amount format. Must be a number.'}), 400
                
            # Find the account
            account_name = posting['account']
            account = Account.query.filter_by(name=account_name, user_id=user.id).first()
            
            if not account:
                return jsonify({'error': f"Account '{account_name}' not found"}), 404
                
            # Create transaction object
            new_transaction = Transaction(
                user_id=user.id,
                account_id=account.id,
                date=transaction_date,
                description=data['payee'],  # Use payee as description
                payee=data['payee'],
                amount=amount_float,
                currency=posting.get('currency', 'USD')
            )
            
            # Update the account balance based on account type
            # For Asset and Expense accounts, positive amounts increase the balance
            # For Liability, Equity, and Income accounts, positive amounts decrease the balance
            if account.type.lower() in ['liability', 'equity', 'income']:
                # Invert the sign for these account types
                account.balance -= amount_float
            else:
                # Default behavior for Asset and Expense accounts
                account.balance += amount_float
            
            db.session.add(new_transaction)
            transaction_responses.append(new_transaction)
        
        # Commit all transactions together
        try:
            db.session.commit()
            # Refresh the objects to get updated values
            for tx in transaction_responses:
                db.session.refresh(tx)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit error: {str(e)}")
            return jsonify({'error': 'Failed to save transaction'}), 500
        
        # Prepare response
        response_data = {
            'message': 'Transaction created successfully',
            'transactions': [tx.to_dict() for tx in transaction_responses]
        }
        
        current_app.logger.debug(f"Transaction response: {json.dumps(response_data)}")
        return jsonify(response_data), 201

    except Exception as e:
        # Catch-all for any unexpected errors during processing
        current_app.logger.error(f"Unhandled error in create_transaction: {str(e)} - Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'An unexpected server error occurred'}), 500

@transactions.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_app.logger.debug("Entered get_transactions route")
    try:
        # Log request
        current_app.logger.debug(f"GET /api/transactions request with params: {request.args}")
        
        limit = request.args.get('limit', type=int)
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        offset = request.args.get('offset', type=int, default=0)
        
        # Start with base query
        query = Transaction.query.filter_by(user_id=current_user.id)
        
        # Apply date filters if provided
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date >= start_date_obj)
            except ValueError:
                current_app.logger.error(f"Invalid start date format: {start_date}")
                
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date <= end_date_obj)
            except ValueError:
                current_app.logger.error(f"Invalid end date format: {end_date}")
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply ordering, offset and limit
        query = query.order_by(Transaction.date.desc())
        
        if offset:
            query = query.offset(offset)
            
        if limit:
            query = query.limit(limit)
            
        transactions_list = query.all()
        
        # Group transactions by date and payee to create the expected structure
        grouped_transactions = {}
        
        for tx in transactions_list:
            # Get account name
            account = Account.query.get(tx.account_id)
            account_name = account.name if account else "Unknown Account"
            
            # Create a unique key for grouping
            key = f"{tx.date.isoformat()}|{tx.payee}"
            
            # Create or update transaction group
            if key not in grouped_transactions:
                grouped_transactions[key] = {
                    'date': tx.date.isoformat(),
                    'payee': tx.payee,
                    'status': '',  # Status not stored in database, using empty string
                    'postings': []
                }
            
            # Add posting to transaction group
            grouped_transactions[key]['postings'].append({
                'account': account_name,
                'amount': str(tx.amount),
                'currency': tx.currency
            })
        
        # Convert grouped transactions to a list
        formatted_transactions = list(grouped_transactions.values())
        
        # Return in the format expected by the frontend
        response = {
            'transactions': formatted_transactions,
            'total': total_count
        }
        
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Error in get_transactions: {str(e)} - Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to retrieve transactions'}), 500 