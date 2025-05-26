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
├── pyproject.toml     # Dependencies and configuration
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
   pip install -e ".[dev]"
   ```

3. Set up environment variables (optional):
   Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=postgresql://user:password@host:port/database # Example: postgresql://postgres:postgres@localhost:5432/kanakku
   FLASK_ENV=development
   LOG_LEVEL=DEBUG  # Set to DEBUG to see detailed debug logs
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

## Debug Logging

The application includes comprehensive debug logging that can be enabled by setting the `LOG_LEVEL` environment variable to `DEBUG`. When enabled, you'll see detailed logs for:

### Logging Features

- **Service Layer Logging**: Entry/exit logging for all service methods with parameters and results
- **Database Operations**: Detailed logging of all database queries, commits, and errors
- **API Calls**: Request/response logging with user context and timing information
- **Business Logic**: Key business operations and decision points
- **Authentication**: User login, token generation, and security events
- **Error Tracking**: Comprehensive error logging with context and stack traces

### Log Levels

- **DEBUG**: Detailed operational information (only visible when LOG_LEVEL=DEBUG)
- **INFO**: General application flow information
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Serious errors that may cause the application to stop

### Log Format

Logs include structured information:
```
[2024-01-15 10:30:45] [DEBUG] [req-12345] AccountService: ENTER get_accounts | Data: {"include_details": true, "user_id": 1}
[2024-01-15 10:30:45] [DEBUG] [req-12345] AccountService: Querying accounts for user and active book | Data: {"user_id": 1, "active_book_id": 1, "include_details": true}
[2024-01-15 10:30:45] [DEBUG] [req-12345] AccountService: EXIT get_accounts | Result: returned 5 detailed accounts
```

### Enabling Debug Logging

1. **Environment Variable**: Set `LOG_LEVEL=DEBUG` in your `.env` file or environment
2. **Development**: Debug logging is automatically enabled when `FLASK_ENV=development`
3. **Production**: Only set to DEBUG temporarily for troubleshooting

### Log Files

Logs are written to:
- `logs/kanakku.log`: All application logs (INFO and above)
- `logs/error.log`: Error logs only (ERROR and above)
- Console output: Respects the LOG_LEVEL setting

### Debugging Specific Components

The enhanced logging covers:

- **User Operations**: Password changes, account activation, token generation
- **Account Management**: CRUD operations, validation, autocomplete
- **Transaction Processing**: Creation, updates, validation
- **Email Automation**: Configuration management, processing
- **Settings Management**: Global configuration operations
- **Gmail Integration**: Message processing and tracking
- **Authentication**: Login attempts, token validation, OAuth flows

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
5. Add appropriate debug logging using the utilities in `app/utils/logging_utils.py`

## Activating a User

New users need to be activated before they can login (unless using Google OAuth):

```bash
flask shell
>>> from app.models import User
>>> user = User.query.filter_by(email='user@example.com').first()
>>> user.activate()
``` 