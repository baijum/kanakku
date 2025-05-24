# Kanakku API Documentation

API documentation for Kanakku - A Simple Accounting Application

**Base URL:** http://localhost:8000

## Authentication

All API endpoints require authentication using API keys. You can authenticate in one of two ways:

1. Using the `X-API-Key` header with your API token:
   ```
   X-API-Key: your_api_token
   ```

2. Using the `Authorization` header with the format:
   ```
   Authorization: Token your_api_token
   ```

## Table of Contents
- [Health Checks](#health-checks)
- [Authentication](#authentication-endpoints)
- [Accounts](#account-endpoints)
- [Transactions](#transaction-endpoints)
- [Reports](#report-endpoints)
- [Ledger](#ledger-endpoints)
- [Preambles](#preamble-endpoints)
- [Books](#book-endpoints)

## Health Checks

### Check API Health
```
GET /api/v1/health
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/health
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

### Check Ledger API Health
```
GET /health
```

**Example:**
```bash
curl -X GET http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

## Authentication Endpoints

### Register User
```
POST /api/v1/auth/register
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123!"
  }'
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

### Login
```
POST /api/v1/auth/login
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123!"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NTA0MjQwMDB9.example_token"
}
```

### Logout
```
POST /api/v1/auth/logout
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

### Get Current User
```
GET /api/v1/auth/me
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2023-01-01T12:00:00Z",
  "picture": "https://example.com/profile.jpg"
}
```

### Update Password
```
PUT /api/v1/auth/password
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/auth/password \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "Password123!",
    "new_password": "NewPassword456!"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

### Request Password Reset
```
POST /api/v1/auth/forgot-password
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Password reset instructions sent"
}
```

### Reset Password
```
POST /api/v1/auth/reset-password
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset-token-received-by-email",
    "email": "user@example.com",
    "new_password": "NewPassword456!"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Password reset successful"
}
```

### Get All API Tokens
```
GET /api/v1/auth/tokens
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/tokens \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "My API Token",
    "token": "partial_token_xxx",
    "is_active": true,
    "created_at": "2023-01-01T12:00:00Z",
    "expires_at": "2023-02-01T12:00:00Z"
  }
]
```

### Create API Token
```
POST /api/v1/auth/tokens
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/tokens \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Token",
    "expires_in_days": 30
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "My API Token",
  "token": "new_full_token_xyz",
  "is_active": true,
  "created_at": "2023-01-01T12:00:00Z",
  "expires_at": "2023-02-01T12:00:00Z"
}
```

### Update API Token
```
PUT /api/v1/auth/tokens/{tokenId}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/auth/tokens/1 \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Token Name",
    "is_active": true
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Token Name",
  "token": "partial_token_xxx",
  "is_active": true,
  "created_at": "2023-01-01T12:00:00Z",
  "expires_at": "2023-02-01T12:00:00Z"
}
```

### Revoke API Token
```
DELETE /api/v1/auth/tokens/{tokenId}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/auth/tokens/1 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Token revoked successfully"
}
```

## Account Endpoints

### List All Accounts (Names Only)
```
GET /api/v1/accounts
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/accounts \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "accounts": [
    "Assets:Checking",
    "Expenses:Groceries",
    "Income:Salary"
  ]
}
```

### List All Accounts (Full Details)
```
GET /api/v1/accounts/details
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/accounts/details \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Assets:Checking",
    "currency": "INR",
    "balance": 5000,
    "created_at": "2023-01-01T12:00:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "name": "Expenses:Groceries",
    "currency": "INR",
    "balance": 0,
    "created_at": "2023-01-01T12:00:00Z"
  }
]
```

### Create Account
```
POST /api/v1/accounts
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assets:Savings",
    "currency": "INR",
    "balance": 10000
  }'
```

**Response (201 Created):**
```json
{
  "message": "Account created successfully",
  "account": {
    "id": 3,
    "user_id": 1,
    "name": "Assets:Savings",
    "currency": "INR",
    "balance": 10000,
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

### Get Account Details
```
GET /api/v1/accounts/{accountId}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/accounts/1 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Assets:Checking",
  "currency": "INR",
  "balance": 5000,
  "created_at": "2023-01-01T12:00:00Z"
}
```

### Update Account
```
PUT /api/v1/accounts/{accountId}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/accounts/1 \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assets:Current",
    "currency": "INR",
    "balance": 5500
  }'
```

**Response (200 OK):**
```json
{
  "message": "Account updated successfully",
  "account": {
    "id": 1,
    "user_id": 1,
    "name": "Assets:Current",
    "currency": "INR",
    "balance": 5500,
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

### Delete Account
```
DELETE /api/v1/accounts/{accountId}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/accounts/3 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Account deleted successfully"
}
```

### Account Autocomplete
```
GET /api/v1/accounts/autocomplete
```

**Description:** Get account name suggestions for auto-completion based on a prefix. Auto-completion only activates when the prefix contains at least one colon (:) to support Ledger CLI-style hierarchical account names.

**Parameters:**
- `prefix` (optional): The account name prefix to search for (must contain at least one colon)
- `limit` (optional): Maximum number of suggestions to return (default: 20)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/accounts/autocomplete?prefix=Assets:Bank:&limit=10" \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "suggestions": [
    "Assets:Bank:Checking",
    "Assets:Bank:Savings",
    "Assets:Bank"
  ],
  "prefix": "Assets:Bank:"
}
```

**Use Cases:**
- When user types `Assets:`, suggestions include `Assets:Bank:Checking`, `Assets:Bank:Savings`, `Assets:Cash`, and `Assets:Bank`
- When user types `Assets:Bank:`, suggestions include `Assets:Bank:Checking`, `Assets:Bank:Savings`
- When user types `Expenses:Food:`, suggestions include `Expenses:Food:Restaurant`, `Expenses:Food:Groceries`

## Transaction Endpoints

### List Transactions
```
GET /api/v1/transactions
```

**Parameters:**
- `limit` (optional): Number of transactions to return
- `offset` (optional): Number of transactions to skip
- `startDate` (optional): Filter by start date (YYYY-MM-DD)
- `endDate` (optional): Filter by end date (YYYY-MM-DD)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/transactions?limit=10&offset=0&startDate=2023-01-01&endDate=2023-01-31" \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "id": 1,
      "user_id": 1,
      "account_id": 1,
      "date": "2023-01-15",
      "description": "Monthly groceries",
      "payee": "Local Supermarket",
      "amount": -2000,
      "currency": "INR",
      "created_at": "2023-01-15T15:30:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "account_id": 1,
      "date": "2023-01-01",
      "description": "Salary deposit",
      "payee": "Employer Inc",
      "amount": 50000,
      "currency": "INR",
      "created_at": "2023-01-01T10:00:00Z"
    }
  ],
  "total_count": 2
}
```

### Create Transaction
```
POST /api/v1/transactions
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2023-01-20",
    "payee": "Electricity Company",
    "postings": [
      {
        "account": "Expenses:Utilities",
        "amount": "1500",
        "currency": "INR"
      },
      {
        "account": "Assets:Checking",
        "amount": "-1500",
        "currency": "INR"
      }
    ]
  }'
```

**Response (201 Created):**
```json
{
  "message": "Transaction created successfully",
  "transactions": [
    {
      "id": 3,
      "user_id": 1,
      "account_id": 4,
      "date": "2023-01-20",
      "description": "",
      "payee": "Electricity Company",
      "amount": 1500,
      "currency": "INR",
      "created_at": "2023-01-20T14:00:00Z"
    },
    {
      "id": 4,
      "user_id": 1,
      "account_id": 1,
      "date": "2023-01-20",
      "description": "",
      "payee": "Electricity Company",
      "amount": -1500,
      "currency": "INR",
      "created_at": "2023-01-20T14:00:00Z"
    }
  ]
}
```

### Get Transaction Details
```
GET /api/v1/transactions/{transactionId}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/transactions/1 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "account_id": 1,
  "date": "2023-01-15",
  "description": "Monthly groceries",
  "payee": "Local Supermarket",
  "amount": -2000,
  "currency": "INR",
  "created_at": "2023-01-15T15:30:00Z"
}
```

### Update Transaction
```
PUT /api/v1/transactions/{transactionId}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/transactions/1 \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2023-01-16",
    "description": "Weekly groceries",
    "payee": "Local Supermarket",
    "amount": -1800,
    "currency": "INR"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Transaction updated successfully",
  "transaction": {
    "id": 1,
    "user_id": 1,
    "account_id": 1,
    "date": "2023-01-16",
    "description": "Weekly groceries",
    "payee": "Local Supermarket",
    "amount": -1800,
    "currency": "INR",
    "created_at": "2023-01-15T15:30:00Z"
  }
}
```

### Update Transaction with Postings
```
PUT /api/v1/transactions/{transactionId}/update_with_postings
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/transactions/1/update_with_postings \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2023-01-16",
    "payee": "Organic Market",
    "postings": [
      {
        "id": 1,
        "account": "Expenses:Groceries",
        "amount": "2200",
        "currency": "INR"
      },
      {
        "id": 2,
        "account": "Assets:Checking",
        "amount": "-2200",
        "currency": "INR"
      }
    ]
  }'
```

**Response (200 OK):**
```json
{
  "message": "Transaction updated successfully",
  "transactions": [
    {
      "id": 1,
      "user_id": 1,
      "account_id": 2,
      "date": "2023-01-16",
      "description": "",
      "payee": "Organic Market",
      "amount": 2200,
      "currency": "INR",
      "created_at": "2023-01-15T15:30:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "account_id": 1,
      "date": "2023-01-16",
      "description": "",
      "payee": "Organic Market",
      "amount": -2200,
      "currency": "INR",
      "created_at": "2023-01-15T15:30:00Z"
    }
  ]
}
```

### Delete Transaction
```
DELETE /api/v1/transactions/{transactionId}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/transactions/1 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Transaction deleted successfully"
}
```

### Get Related Transactions
```
GET /api/v1/transactions/{transactionId}/related
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/transactions/1/related \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "user_id": 1,
    "account_id": 2,
    "date": "2023-01-16",
    "description": "",
    "payee": "Organic Market",
    "amount": -2200,
    "currency": "INR",
    "created_at": "2023-01-15T15:30:00Z"
  }
]
```

### Delete Related Transactions
```
DELETE /api/v1/transactions/{transactionId}/related
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/transactions/1/related \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Related transactions deleted successfully"
}
```

## Report Endpoints

### Get Balance Report
```
GET /api/v1/reports/balance
```

**Parameters:**
- `account` (optional): Filter by account
- `depth` (optional): Depth of the account hierarchy

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/balance?account=Assets&depth=2" \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "balance": "Assets:Checking                 5500.00 INR\nAssets:Savings                  10000.00 INR\n"
}
```

### Get Transaction Register
```
GET /api/v1/reports/register
```

**Parameters:**
- `account` (optional): Filter by account
- `limit` (optional): Number of transactions to return

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/register?account=Assets:Checking&limit=10" \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "register": "2023-01-16 Organic Market         Expenses:Groceries           2200.00 INR    2200.00 INR\n                                Assets:Checking              -2200.00 INR        0.00 INR"
}
```

### Get Balance Report by Account Type
```
GET /api/v1/reports/balance_report
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/reports/balance_report \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "balance_report": "Assets:Checking                 5500.00 INR\nAssets:Savings                  10000.00 INR\n-------------------------------------------\n                               15500.00 INR\n\nExpenses:Groceries               2200.00 INR\nExpenses:Utilities               1500.00 INR\n-------------------------------------------\n                                3700.00 INR\n\nIncome:Salary                 -50000.00 INR\n-------------------------------------------\n                              -50000.00 INR"
}
```

### Get Income Statement
```
GET /api/v1/reports/income_statement
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/reports/income_statement \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "income_statement": "Income:Salary                  50000.00 INR\n-------------------------------------------\nTotal Income                    50000.00 INR\n\nExpenses:Groceries               2200.00 INR\nExpenses:Utilities               1500.00 INR\n-------------------------------------------\nTotal Expenses                   3700.00 INR\n\nNet Income                      46300.00 INR"
}
```

## Ledger Endpoints

### Get Transactions in Ledger Format
```
GET /api/v1/ledgertransactions
```

**Parameters:**
- `preamble_id` (optional): ID of a specific preamble to include
- `startDate` (optional): Filter transactions starting from this date (YYYY-MM-DD)
- `endDate` (optional): Filter transactions until this date (YYYY-MM-DD)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ledgertransactions?startDate=2023-01-01&endDate=2023-01-31" \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```
2023-01-01 Employer Inc
    Income:Salary                     -50000 INR
    Assets:Checking                    50000 INR

2023-01-16 Organic Market
    Expenses:Groceries                  2200 INR
    Assets:Checking                    -2200 INR

2023-01-20 Electricity Company
    Expenses:Utilities                  1500 INR
    Assets:Checking                    -1500 INR
```

## Preamble Endpoints

### List All Preambles
```
GET /api/v1/preambles
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/preambles \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "preambles": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Default Preamble",
      "content": "; Default ledger configuration\nP INR ₹ 1000.00\n",
      "is_default": true,
      "created_at": "2023-01-01T10:00:00Z",
      "updated_at": "2023-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "name": "USD Configuration",
      "content": "; USD ledger configuration\nP USD $ 1000.00\n",
      "is_default": false,
      "created_at": "2023-01-01T11:00:00Z",
      "updated_at": "2023-01-01T11:00:00Z"
    }
  ]
}
```

### Create Preamble
```
POST /api/v1/preambles
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/preambles \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Euro Configuration",
    "content": "; Euro ledger configuration\nP EUR € 1000.00\n",
    "is_default": false
  }'
```

**Response (201 Created):**
```json
{
  "message": "Preamble created successfully",
  "preamble": {
    "id": 3,
    "user_id": 1,
    "name": "Euro Configuration",
    "content": "; Euro ledger configuration\nP EUR € 1000.00\n",
    "is_default": false,
    "created_at": "2023-01-02T10:00:00Z",
    "updated_at": "2023-01-02T10:00:00Z"
  }
}
```

### Get Preamble Details
```
GET /api/v1/preambles/{preambleId}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/preambles/1 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Default Preamble",
  "content": "; Default ledger configuration\nP INR ₹ 1000.00\n",
  "is_default": true,
  "created_at": "2023-01-01T10:00:00Z",
  "updated_at": "2023-01-01T10:00:00Z"
}
```

### Update Preamble
```
PUT /api/v1/preambles/{preambleId}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/preambles/1 \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Default Preamble",
    "content": "; Updated default ledger configuration\nP INR ₹ 1000.00\n",
    "is_default": true
  }'
```

**Response (200 OK):**
```json
{
  "message": "Preamble updated successfully",
  "preamble": {
    "id": 1,
    "user_id": 1,
    "name": "Updated Default Preamble",
    "content": "; Updated default ledger configuration\nP INR ₹ 1000.00\n",
    "is_default": true,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-02T15:00:00Z"
  }
}
```

### Delete Preamble
```
DELETE /api/v1/preambles/{preambleId}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/preambles/3 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Preamble deleted successfully",
  "was_default": false
}
```

### Get Default Preamble
```
GET /api/v1/preambles/default
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/preambles/default \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Updated Default Preamble",
  "content": "; Updated default ledger configuration\nP INR ₹ 1000.00\n",
  "is_default": true,
  "created_at": "2023-01-01T10:00:00Z",
  "updated_at": "2023-01-02T15:00:00Z"
}
```

## Book Endpoints

### List All Books
```
GET /api/v1/books
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/books \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Personal Finances",
    "is_active": true,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-01T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "name": "Business Accounts",
    "is_active": false,
    "created_at": "2023-01-01T11:00:00Z",
    "updated_at": "2023-01-01T11:00:00Z"
  }
]
```

### Create Book
```
POST /api/v1/books
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/books \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Household Expenses"
  }'
```

**Response (201 Created):**
```json
{
  "message": "Book created successfully",
  "book": {
    "id": 3,
    "user_id": 1,
    "name": "Household Expenses",
    "is_active": false,
    "created_at": "2023-01-02T10:00:00Z",
    "updated_at": "2023-01-02T10:00:00Z"
  }
}
```

### Get Book Details
```
GET /api/v1/books/{bookId}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/books/1 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Personal Finances",
  "is_active": true,
  "created_at": "2023-01-01T10:00:00Z",
  "updated_at": "2023-01-01T10:00:00Z"
}
```

### Update Book
```
PUT /api/v1/books/{bookId}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/books/1 \
  -H "X-API-Key: your_api_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Personal Finances"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Book updated successfully",
  "book": {
    "id": 1,
    "user_id": 1,
    "name": "Updated Personal Finances",
    "is_active": true,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-02T15:00:00Z"
  }
}
```

### Delete Book
```
DELETE /api/v1/books/{bookId}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/books/3 \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Book and all associated accounts deleted successfully"
}
```

### Set Active Book
```
POST /api/v1/books/{bookId}/set-active
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/books/2/set-active \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "message": "Book set as active successfully",
  "active_book": {
    "id": 2,
    "user_id": 1,
    "name": "Business Accounts",
    "is_active": true,
    "created_at": "2023-01-01T11:00:00Z",
    "updated_at": "2023-01-02T16:00:00Z"
  }
}
```

### Get Active Book
```
GET /api/v1/books/active
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/v1/books/active \
  -H "X-API-Key: your_api_token"
```

**Response (200 OK):**
```json
{
  "id": 2,
  "user_id": 1,
  "name": "Business Accounts",
  "is_active": true,
  "created_at": "2023-01-01T11:00:00Z",
  "updated_at": "2023-01-02T16:00:00Z"
}
```