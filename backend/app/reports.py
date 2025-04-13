from flask import Blueprint, jsonify, request, current_app, g
from app.ledger import run_ledger_command
from app.auth import jwt_required

reports = Blueprint('reports', __name__)

@reports.route('/api/reports/balance', methods=['GET'])
@jwt_required
def get_balance():
    account = request.args.get('account')
    depth = request.args.get('depth')
    
    cmd_args = ['balance']
    if account:
        cmd_args.append(account)
    if depth:
        cmd_args.extend(['--depth', depth])
        
    try:
        output = run_ledger_command(cmd_args)
        return jsonify({'balance': output})
    except Exception as e:
        current_app.logger.error(f"Ledger balance error: {e}")
        return jsonify({'error': str(e)}), 500

@reports.route('/api/reports/register', methods=['GET'])
@jwt_required
def get_register():
    account = request.args.get('account')
    limit = request.args.get('limit')
    
    cmd_args = ['register']
    if account:
        cmd_args.append(account)
    if limit:
        cmd_args.extend(['--limit', limit])
        
    try:
        output = run_ledger_command(cmd_args)
        return jsonify({'register': output})
    except Exception as e:
        current_app.logger.error(f"Ledger register error: {e}")
        return jsonify({'error': str(e)}), 500

@reports.route('/api/reports/accounts', methods=['GET'])
@jwt_required
def get_accounts():
    try:
        # Using ledger accounts command
        output = run_ledger_command(['accounts'])
        # Simple parsing assuming one account per line
        accounts_list = [line.strip() for line in output.splitlines() if line.strip()]
        # Return in the expected format
        return jsonify({'accounts': accounts_list})
    except Exception as e:
        current_app.logger.error(f"Ledger accounts error: {e}")
        return jsonify({'error': str(e)}), 500
        
# Placeholder for other report types
@reports.route('/api/reports/balance_report', methods=['GET'])
@jwt_required
def get_balance_report():
    # Example: Use ledger balance command for a full balance report
    try:
        output = run_ledger_command(['balance'])
        return jsonify({'balance_report': output})
    except Exception as e:
        current_app.logger.error(f"Ledger balance report error: {e}")
        return jsonify({'error': str(e)}), 500

@reports.route('/api/reports/income_statement', methods=['GET'])
@jwt_required
def get_income_statement():
    # Example: Use ledger balance for Income/Expenses
    try:
        output = run_ledger_command(['balance', 'Income', 'Expenses'])
        return jsonify({'income_statement': output})
    except Exception as e:
        current_app.logger.error(f"Ledger income statement error: {e}")
        return jsonify({'error': str(e)}), 500 