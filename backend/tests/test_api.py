import pytest
import json
from app.models import User, Transaction, Account
from datetime import date

def test_register(authenticated_client, mock_ledger_command):
    """Test user registration."""
    response = authenticated_client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert 'token' in response.json

def test_login(authenticated_client, mock_ledger_command):
    """Test user login."""
    response = authenticated_client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_get_transactions(authenticated_client, mock_ledger_command):
    """Test getting transactions."""
    response = authenticated_client.get('/api/transactions')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_add_transaction(authenticated_client, mock_ledger_command):
    """Test adding a transaction."""
    # First create an account
    account_data = {
        'name': 'Assets:Checking',
        'type': 'asset',
        'currency': 'USD'
    }
    account_response = authenticated_client.post('/api/accounts', json=account_data)
    assert account_response.status_code == 201
    
    # Now create a transaction using the account
    transaction_data = {
        'date': '2025-01-17',
        'description': 'Grocery Shopping',
        'payee': 'Test Store',
        'amount': 50.00,
        'currency': 'USD',
        'account_name': 'Assets:Checking'
    }
    
    response = authenticated_client.post('/api/transactions', json=transaction_data)
    assert response.status_code == 201
    data = response.json
    assert 'message' in data
    assert 'Transaction created successfully' in data['message']

def test_get_accounts(authenticated_client, account):
    """Test getting accounts."""
    response = authenticated_client.get('/api/accounts')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    # Could assert the account from fixture is in the response

def test_add_account(authenticated_client):
    """Test adding an account."""
    response = authenticated_client.post('/api/accounts', json={
        'name': 'Test Account',
        'type': 'asset',
        'currency': 'USD'
    })
    assert response.status_code == 201
    data = response.json
    assert 'message' in data
    assert data['message'] == 'Account created successfully'

def test_get_balance(authenticated_client, mock_ledger_command):
    """Test getting balance report."""
    # Mock the ledger_command to return text not bytes
    mock_ledger_command.return_value = "Assets:Checking   $500.00"
    
    response = authenticated_client.get('/api/reports/balance')
    assert response.status_code == 200
    data = response.json
    assert 'balance' in data

def test_get_register(authenticated_client, mock_ledger_command):
    """Test getting register report."""
    # Mock the ledger_command to return text not bytes
    mock_ledger_command.return_value = "2025-01-17 Test Store   Expenses:Groceries   $50.00"
    
    response = authenticated_client.get('/api/reports/register')
    assert response.status_code == 200
    data = response.json
    assert 'register' in data 