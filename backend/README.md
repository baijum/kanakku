# Kanakku Backend

This is the Flask backend API for the Kanakku expense tracking application. It provides RESTful endpoints for managing users, accounts, transactions, and reports.

## Technology Stack

- **Flask 3.0**: Core web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: JWT-based authentication
- **Flask-CORS**: Cross-Origin Resource Sharing support
- **Flask-Migrate**: Database migrations
- **Flask-Swagger-UI**: API documentation
- **PostgreSQL**: Database used for persistence

## Project Structure

```
backend/
├── app/               # Application package
│   ├── __init__.py    # App factory
│   ├── models.py      # SQLAlchemy models
│   ├── config.py      # Configuration settings
│   ├── extensions.py  # Flask extensions
│   ├── api.py         # General API routes
│   ├── auth.py        # Authentication routes
│   ├── accounts.py    # Account management routes
│   ├── transactions.py # Transaction management
│   ├── books.py       # Book entries
│   ├── reports.py     # Reporting functionality
│   ├── ledger.py      # Ledger integration
│   ├── preamble.py    # Core utilities
│   ├── swagger.py     # Swagger integration
│   ├── errors.py      # Error handlers
│   └── utils/         # Utility functions
├── migrations/        # Alembic migrations
├── tests/             # Test suite
├── instance/          # Instance-specific data
│   └── app.db         # SQLite database
├── swagger.yaml       # OpenAPI specification
├── requirements.txt   # Dependencies
├── run-backend.sh     # Startup script
└── ...
```

## Getting Started

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=postgresql://user:password@host:port/database # Example: postgresql://postgres:postgres@localhost:5432/kanakku
   FLASK_ENV=development
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the development server:
   ```bash
   ./run-backend.sh
   ```
   
   The API will be available at `http://localhost:8000`.

## API Documentation

Swagger/OpenAPI documentation is available at:
```
http://localhost:8000/api/docs
```

## Main API Endpoints

- **Authentication**
  - `POST /api/v1/auth/register` - Register a new user
  - `POST /api/v1/auth/login` - Login a user
  - `GET /api/v1/auth/me` - Get current user
  - `GET /api/v1/auth/google` - Google OAuth login

- **Accounts**
  - `GET /api/v1/accounts` - List accounts
  - `POST /api/v1/accounts` - Create account
  - `GET /api/v1/accounts/<id>` - Get account
  - `PUT /api/v1/accounts/<id>` - Update account
  - `DELETE /api/v1/accounts/<id>` - Delete account

- **Transactions**
  - `GET /api/v1/transactions` - List transactions
  - `POST /api/v1/transactions` - Create transaction
  - `PUT /api/v1/transactions/<id>` - Update transaction
  - `DELETE /api/v1/transactions/<id>` - Delete transaction

- **Books**
  - `GET /api/v1/books` - List book entries
  - `POST /api/v1/books` - Create book entry

- **Reports**
  - `GET /api/v1/reports/balance` - Get account balances
  - `GET /api/v1/reports/register` - Get transaction register

## Testing

Run the test suite:
```bash
python -m pytest -v tests/
```

Run with coverage:
```bash
python -m pytest --cov=app tests/
```

## Authentication

The API uses JWT tokens for authentication. Most endpoints require a valid token in the Authorization header:

```
Authorization: Bearer <token>
```

## Database Migrations

Create a migration:
```bash
flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

## Currency

The default currency is INR (Indian Rupee). All monetary values are stored with their currency code, with INR as the default if not specified.

## Developing

When adding new endpoints:
1. Create route handlers in the appropriate module
2. Update the Swagger documentation in `swagger.yaml`
3. Write tests in the `tests/` directory
4. Update error handlers if needed

## Activating a User

New users need to be activated before they can login (unless using Google OAuth):

```bash
flask shell
>>> from app.models import User
>>> user = User.query.filter_by(email='user@example.com').first()
>>> user.activate()
``` 