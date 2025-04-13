# Kanakku - Ledger CLI Web Interface

A modern web interface for the Ledger CLI double-entry accounting tool. Kanakku provides a user-friendly way to manage your financial transactions while keeping your data in the standard Ledger plain text format.

## Features

- Add new transactions with a user-friendly form
- View existing transactions and account balances
- Generate standard Ledger reports
- Modern, responsive web interface
- Single-user, local-first design

## Prerequisites

- Python 3.12+
- Node.js 18+
- Ledger CLI installed and accessible in PATH

## Project Structure

```
kanakku/
├── backend/           # Flask backend
├── frontend/          # React frontend
└── journal.ledger     # Ledger file (created on first run)
```

## Architecture

*   **Frontend:** React application located in the `frontend/` directory (`frontend/src`). It provides the user interface and interacts with the backend via API calls.
*   **Backend:** Flask application located in the `backend/` directory (`backend/app`). It serves a RESTful API, handles business logic, interacts with the `ledger-cli` tool, and manages authentication.
*   **API:** Defined using Flask Blueprints. The main API endpoints are consolidated under `/api/`. Authentication is handled via JWT.
*   **Data Storage:**
    *   **Ledger Data:** Stored in a plain text file (e.g., `journal.ledger`), managed via the `ledger-cli` tool (`backend/app/ledger.py`).
    *   **Application Data:** An SQLite database (`backend/app/app.db`) for users, sessions, etc. (managed via SQLAlchemy in `backend/app/models.py`).

## API Endpoints

The main API endpoints are served under the `/api/` prefix by the Flask backend. Authentication via JWT is required for most endpoints.

*   **Health Check**
    *   `GET /api/health` (No Auth Required) - Basic health check.
*   **Transactions**
    *   `GET /api/transactions` - Get all transactions for the current user.
    *   `POST /api/transactions` - Add a new transaction. (Body: `{ "date": "YYYY-MM-DD", "payee": "...", "postings": [...] }`)
*   **Accounts**
    *   `GET /api/accounts` - Get all account names for the current user.
    *   `POST /api/accounts` - Add a new account. (Body: `{ "name": "...", "type": "..." }`)
*   **Reports**
    *   `GET /api/reports/balance` - Get balance report.
    *   `GET /api/reports/register` - Get register report.
*   **Authentication**
    *   Endpoints for user registration, login, logout, and token management are likely provided by the `auth` blueprint (see `backend/app/auth.py`).

*(Note: Some API endpoints might currently return mocked data as per `backend/app/api.py`)*

## Setup

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
export LEDGER_FILE=../journal.ledger
export FLASK_APP=app.py
export FLASK_ENV=development
```

4. Run the backend server:
```bash
flask run
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Development

The application runs in development mode with:
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

## License

MIT License 