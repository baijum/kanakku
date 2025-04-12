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