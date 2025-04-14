# Kanakku - An expense tracker

Kanakku provides a user-friendly way to manage your financial transactions.

## Features

- Add new transactions with a user-friendly form
- View existing transactions and account balances
- Generate standard Ledger reports
- Modern, responsive web interface
- JWT-based authentication
- Google Sign-In integration

## Prerequisites

- Python 3.12+
- Node.js 18+

## Project Structure

```
kanakku/
├── backend/           # Flask backend
│   ├── app/           # Application package
│   │   ├── __init__.py # App factory
│   │   ├── models.py  # SQLAlchemy models
│   │   ├── config.py  # Configuration settings
│   │   ├── extensions.py # Flask extensions (db, jwt)
│   │   ├── api.py     # General API routes (e.g., health check)
│   │   ├── auth.py    # Authentication routes
│   │   ├── accounts.py # Account management routes
│   │   ├── transactions.py # Transaction management routes
│   │   ├── ledger.py  # Ledger-specific routes (e.g., ledger format export)
│   │   ├── reports.py # Reporting routes (currently commented out)
│   │   └── errors.py  # Error handlers
│   ├── tests/         # Pytest test suite
│   ├── venv/          # Virtual environment
│   ├── requirements.txt
│   └── ...
├── frontend/          # React frontend
│   ├── public/
│   ├── src/           # Source code
│   ├── package.json
│   └── ...
├── fixes/             # Documentation for major bug fixes
    └── flask-jwt-extended-422-errors.md
```

## Architecture

*   **Frontend:** React application (`frontend/`) providing the user interface. It communicates with the backend via API calls.
*   **Backend:** Flask application (`backend/`) serving a RESTful API. It handles:
    *   **Business Logic:** Managing users, accounts, and transactions.
    *   **Database Interaction:** Using SQLAlchemy (`backend/app/models.py`) with an SQLite database (`backend/app/app.db`) for application data (users, accounts, transactions).
    *   **Authentication:** Utilizing Flask-JWT-Extended for token-based authentication (`backend/app/auth.py`, `backend/app/__init__.py`).
    *   **Ledger Interaction:** Currently limited to exporting data in Ledger format (`backend/app/ledger.py`). Direct interaction with `ledger-cli` for reporting is present but commented out.
*   **API:** Defined using Flask Blueprints, organized by functionality (auth, accounts, transactions, etc.). All endpoints are prefixed with `/api/`.

## API Endpoints

The main API endpoints are served under the `/api/` prefix by the Flask backend. Authentication via JWT (Bearer token in Authorization header) is required for most endpoints.

*   **Health Check (`api.py`)**
    *   `GET /api/health` (No Auth Required) - Basic health check.
*   **Authentication (`auth.py`)**
    *   `POST /api/auth/register` - Register a new user. (Body: `{ "username": "...", "email": "...", "password": "..." }`)
    *   `POST /api/auth/login` - Log in a user. (Body: `{ "username": "...", "password": "..." }`)
    *   `POST /api/auth/logout` (Auth Required) - Placeholder for logout (JWT handled client-side).
    *   `GET /api/auth/me` (Auth Required) - Get the current logged-in user's details.
*   **Accounts (`accounts.py`)** (Auth Required)
    *   `GET /api/accounts` - Get all accounts for the current user.
    *   `POST /api/accounts` - Add a new account. (Body: `{ "name": "...", "type": "...", "currency": "..." (optional), "balance": ... (optional) }`)
    *   `GET /api/accounts/<int:account_id>` - Get details for a specific account.
    *   `PUT /api/accounts/<int:account_id>` - Update a specific account. (Body: `{ "name": "...", "type": "...", ... }`)
    *   `DELETE /api/accounts/<int:account_id>` - Delete a specific account.
*   **Transactions (`transactions.py`)** (Auth Required)
    *   `POST /api/transactions` - Add a new transaction. (Body: `{ "date": "YYYY-MM-DD", "description": "...", "amount": ..., "account_name": "...", "payee": "..." (optional), "currency": "..." (optional) }`)
    *   `GET /api/transactions` - Get all transactions for the current user (supports `?limit=N` query parameter).
*   **Ledger (`ledger.py`)** (Auth Required)
    *   `GET /api/v1/ledgertransactions` - Get all transactions for the current user in Ledger text format.
*   **Reports (`reports.py`)**
    *   (No active API endpoints currently - routes are commented out)

## Authentication

Kanakku supports two authentication methods:

1. **Traditional username/password authentication**:
   - Register with a username, email, and password
   - Login with username and password
   - User accounts require activation by an administrator

2. **Google Sign-In**:
   - Sign in with your Google account
   - New users are automatically created and activated
   - Existing users can link their account with Google

### Setting up Google OAuth

To enable Google Sign-In, you need to:

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Configure the OAuth consent screen
3. Create OAuth client credentials (Web application type)
4. Add authorized JavaScript origins:
   - `http://localhost:5000` (backend development server)
   - `http://localhost:3000` (frontend development server)
5. Add authorized redirect URIs:
   - `http://localhost:5000/api/auth/google/callback`
6. Copy the Client ID and Client Secret to your backend `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

## Setup

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables (optional - defaults are provided in `config.py`):
    *   `SECRET_KEY`: A secret key for Flask sessions and security.
    *   `JWT_SECRET_KEY`: A secret key for JWT generation.
    *   `DATABASE_URL`: Database connection string (defaults to SQLite `app.db`).
    *   `LEDGER_PATH`: Path to the `ledger` executable (if not in system PATH).
5.  Run the backend server:
    ```bash
    flask run
    ```
    The backend will be available at `http://127.0.0.1:5000`.

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the frontend development server:
    ```bash
    npm start
    ```
    The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend.

## Usage

1.  Start both the backend and frontend servers.
2.  Access the web interface in your browser (usually `http://localhost:3000`).
3.  Register a new user or log in if you already have an account.
4.  Use the interface to add accounts and transactions.

## Testing

To run the backend tests:

1.  Ensure the backend virtual environment is active and development dependencies are installed (`pytest`, `pytest-cov`, `pytest-mock`).
2.  Navigate to the `kanakku` root directory.
3.  Run pytest:
    ```bash
    python -m pytest -v backend/tests/
    ```

## Activating a User

```
$ cd backend
$ flask shell
>>> from app.models import User
>>> user = User.query.filter_by(email='user@example.com').first()
>>> user.activate()
```
