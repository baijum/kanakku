from app.models import User


def test_register(authenticated_client, mock_ledger_command):
    """Test user registration."""
    response = authenticated_client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "hcaptcha_token": "test_token",  # In testing mode, this will be accepted
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "User and default book created successfully." in data["message"]
    assert "user_id" in data


def test_login(authenticated_client, mock_ledger_command, db_session):
    """Test user login."""
    # First activate the test user
    user = db_session.query(User).filter_by(email="test@example.com").first()
    user.activate()
    db_session.commit()

    response = authenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data


def test_get_transactions(authenticated_client, mock_ledger_command):
    """Test getting transactions."""
    response = authenticated_client.get("/api/v1/transactions")
    assert response.status_code == 200
    data = response.get_json()
    assert "transactions" in data
    assert isinstance(data["transactions"], list)
    assert "total" in data


def test_add_transaction(authenticated_client, mock_ledger_command):
    """Test adding a transaction."""
    # First create an account
    account_data = {"name": "Assets:Checking", "currency": "INR"}
    account_response = authenticated_client.post("/api/v1/accounts", json=account_data)
    assert account_response.status_code == 201

    # Now create a transaction using the account
    transaction_data = {
        "date": "2025-01-17",
        "payee": "Test Store",
        "postings": [
            {"account": "Assets:Checking", "amount": 50.00, "currency": "INR"}
        ],
    }

    response = authenticated_client.post("/api/v1/transactions", json=transaction_data)
    assert response.status_code == 201
    data = response.json
    assert "message" in data
    assert "Transaction created successfully" in data["message"]


def test_get_accounts(authenticated_client, account):
    """Test getting accounts."""
    response = authenticated_client.get("/api/v1/accounts")
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, dict)
    assert "accounts" in data
    assert isinstance(data["accounts"], list)
    assert "Test Account" in data["accounts"]


def test_add_account(authenticated_client):
    """Test adding an account."""
    response = authenticated_client.post(
        "/api/v1/accounts",
        json={"name": "Test Account", "currency": "INR"},
    )
    assert response.status_code == 201
    assert "Test Account" in response.json["account"]["name"]


# Remove the following two tests as the routes were removed from api.py
# def test_get_balance(authenticated_client, mock_ledger_command):
#     """Test getting balance report."""
#     # Mock the ledger_command to return text not bytes
#     mock_ledger_command.return_value = "Assets:Checking   $500.00"
#
#     response = authenticated_client.get('/api/reports/balance')
#     assert response.status_code == 200
#     data = response.json
#     assert 'balance' in data
#     assert data['balance'] == "Assets:Checking   $500.00"
#
# def test_get_register(authenticated_client, mock_ledger_command):
#     """Test getting register report."""
#     # Mock the ledger_command to return text not bytes
#     mock_ledger_command.return_value = "2025-01-17 Test Store   Expenses:Groceries   $50.00"
#
#     response = authenticated_client.get('/api/reports/register')
#     assert response.status_code == 200
#     data = response.json
#     assert 'register' in data
#     assert data['register'] == "2025-01-17 Test Store   Expenses:Groceries   $50.00"
