import os
import subprocess
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
LEDGER_FILE = os.getenv('LEDGER_FILE', 'journal.ledger')
LEDGER_CMD = os.getenv('LEDGER_CMD', 'ledger')

def run_ledger_command(cmd_args):
    """Execute a ledger command and return its output."""
    try:
        result = subprocess.run(
            [LEDGER_CMD, '-f', LEDGER_FILE] + cmd_args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return {'error': str(e), 'output': e.output}, 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get a list of transactions."""
    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    # Use ledger print command with limit and offset
    output = run_ledger_command(['print', f'--limit={limit}', f'--offset={offset}'])
    return jsonify({'transactions': output})

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add a new transaction."""
    data = request.json
    
    # Validate required fields
    required_fields = ['date', 'payee', 'postings']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Format transaction for ledger
    status = data.get('status', '')
    date = data['date']
    payee = data['payee']
    postings = data['postings']
    
    # Validate postings balance
    total = sum(float(p['amount']) for p in postings)
    if abs(total) > 0.01:  # Allow for small floating point differences
        return jsonify({'error': 'Transaction does not balance'}), 400
    
    # Format transaction
    transaction = f"{date} {status} {payee}\n"
    for posting in postings:
        account = posting['account']
        amount = posting['amount']
        currency = posting.get('currency', '$')
        transaction += f"    {account}    {currency} {amount}\n"
    
    # Append to ledger file
    try:
        with open(LEDGER_FILE, 'a') as f:
            f.write(transaction + '\n')
        return jsonify({'message': 'Transaction added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get list of accounts."""
    output = run_ledger_command(['accounts'])
    accounts = [line.strip() for line in output.split('\n') if line.strip()]
    return jsonify({'accounts': accounts})

@app.route('/api/reports/balance', methods=['GET'])
def get_balance():
    """Get balance report."""
    account = request.args.get('account')
    depth = request.args.get('depth')
    
    cmd_args = ['balance']
    if account:
        cmd_args.append(account)
    if depth:
        cmd_args.append(f'--depth={depth}')
    
    output = run_ledger_command(cmd_args)
    return jsonify({'balance': output})

@app.route('/api/reports/register', methods=['GET'])
def get_register():
    """Get register report."""
    account = request.args.get('account')
    limit = request.args.get('limit', default=50, type=int)
    
    cmd_args = ['register', f'--limit={limit}']
    if account:
        cmd_args.append(account)
    
    output = run_ledger_command(cmd_args)
    return jsonify({'register': output})

if __name__ == '__main__':
    app.run(debug=True) 