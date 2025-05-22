# Kanakku
> **Personal Expense Tracker**

Kanakku provides a user-friendly way to track your personal expenses.

## Features

- Add new transactions with a user-friendly form
- View existing transactions and account balances
- Generate standard Ledger reports
- Modern, responsive web interface
- JWT-based authentication
- Google Sign-In integration
- Default INR currency with proper symbol formatting
- Book entries for advanced accounting
- Comprehensive transaction reports
- Rate limiting for API security
- API token authentication support
- Swagger/OpenAPI documentation
- Automated bank transaction processing
- Email-based transaction extraction
- Automatic expense categorization
- Account mapping for bank transactions

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database
- Redis (for job queue)
- Gmail account with App Password (for bank transaction processing)
- Docker and Docker Compose (optional, for containerized development)

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
│   │   ├── reports.py # Reporting functionality
│   │   ├── books.py   # Book entries for advanced accounting
│   │   ├── preamble.py # Core utilities and constants
│   │   ├── swagger.py # Swagger/OpenAPI documentation handlers
│   │   ├── errors.py  # Error handlers
│   │   ├── mappings.py # Data mapping configurations
│   │   └── utils/     # Utility modules
│   │       ├── email_utils.py  # Email handling utilities
│   │       └── logging_utils.py  # Logging configuration
│   ├── migrations/    # Database migrations (Alembic)
│   ├── swagger.yaml   # OpenAPI specification
│   ├── tests/         # Pytest test suite
│   ├── requirements.txt
│   └── ...
├── tools/            # Command-line tools
│   ├── accountimporter/  # Rust-based account importer
│   └── ledgertransactions/  # Go-based ledger transaction processor
...
├── frontend/          # React frontend
│   ├── public/
│   ├── src/           # Source code
│   │   ├── components/ # React components
│   │   ├── api/       # API client code
│   │   └── ...
│   ├── package.json
│   └── ...
├── banktransactions/  # Bank transaction processing
│   ├── email_parser.py # Transaction extraction logic
│   ├── imap_client.py # Email fetching and processing
│   ├── api_client.py  # API integration
│   ├── config.toml    # Account and expense mapping
│   ├── main.py        # Main processing pipeline
│   └── tests/         # Test suite
├── fixes/             # Documentation for major bug fixes
│   └── transaction_update_with_postings_fix.md
├── docs/              # Project documentation
│   ├── ARCHITECTURE.md # Detailed architecture documentation
│   ├── architecture_diagrams.md # Visual architecture diagrams
│   ├── PRODUCTION_DEPLOYMENT.md # Production deployment guide
│   ├── PRODUCTION_CHECKLIST.md # Pre-production checklist
│   ├── rate-limit-configuration.md # Rate limiting documentation
│   ├── faq.md # Frequently asked questions
│   └── user_manual.md # User documentation
```

## Development Tools

### Docker Support
Kanakku includes a `docker-compose.yml` file for containerized development and deployment. This allows for consistent environments across development, testing, and production.

### CI/CD Pipelines
The project uses GitHub Actions for continuous integration and deployment, with workflows for:
- Linting (`lint-black.yml`)
- Backend testing (`test-backend.yml`)
- Release automation

### Database Migrations
Database schema changes are managed using Alembic migrations, located in `backend/migrations/`. This ensures version-controlled, reproducible database schema updates.

### Helper Scripts
Root-level scripts for common development tasks:
- `lint.sh` - Run code linting
- `test.sh` - Run test suite

## Architecture

Kanakku follows a modern, layered architecture with a clear separation between frontend and backend.

*   **Frontend:** React application (`frontend/`) providing the user interface. It communicates with the backend via API calls.
    * Uses Material-UI (MUI) for component styling
    * React Router for navigation
    * Axios for API requests
*   **Backend:** Flask application (`backend/`) serving a RESTful API. It handles:
    *   **Business Logic:** Managing users, accounts, transactions, and book entries.
    *   **Database Interaction:** Using SQLAlchemy (`backend/app/models.py`) with a PostgreSQL database for application data.
    *   **Authentication:** Utilizing Flask-JWT-Extended for token-based authentication and Google OAuth integration.
    *   **Ledger Interaction:** Exporting data in Ledger format and generating reports.
*   **API:** Defined using Flask Blueprints, organized by functionality with Swagger/OpenAPI documentation. All endpoints are prefixed with `/api/`.

For a detailed architectural overview, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

For visual architecture diagrams using Mermaid, see [architecture_diagrams.md](docs/architecture_diagrams.md).

## API Endpoints

The main API endpoints are served under the `/api/` prefix by the Flask backend. Authentication via JWT (Bearer token in Authorization header) is required for most endpoints.

*   **Health Check (`api.py`)**
    *   `GET /api/v1/health` (No Auth Required) - Basic health check.
*   **Authentication (`auth.py`)**
    *   `POST /api/v1/auth/register` - Register a new user. (Body: `{ "email": "...", "password": "..." }`)
    *   `POST /api/v1/auth/login` - Log in a user. (Body: `{ "email": "...", "password": "..." }`)
    *   `POST /api/v1/auth/logout` (Auth Required) - Placeholder for logout (JWT handled client-side).
    *   `GET /api/v1/auth/me` (Auth Required) - Get the current logged-in user's details.
    *   `POST /api/v1/auth/refresh` (Auth Required) - Refresh an expiring JWT token.
    *   `GET /api/v1/auth/test-token-expiration` - Test endpoint that simulates token expiration.
    *   `GET /api/v1/auth/google` - Initiate Google OAuth login flow.
    *   `GET /api/v1/auth/google/callback` - Callback for Google OAuth.
    *   `POST /api/v1/auth/reset-password-request` - Request a password reset.
    *   `POST /api/v1/auth/reset-password` - Reset password with token.
    *   `GET /api/v1/auth/tokens` - Get all API tokens for the user.
    *   `POST /api/v1/auth/tokens` - Create a new API token.
    *   `PUT /api/v1/auth/tokens/<token_id>` - Update an API token.
    *   `DELETE /api/v1/auth/tokens/<token_id>` - Delete an API token.
*   **Accounts (`accounts.py`)** (Auth Required)
    *   `GET /api/v1/accounts` - Get all accounts for the current user.
    *   `POST /api/v1/accounts` - Add a new account. (Body: `{ "name": "...", "description": "..." (optional), "currency": "..." (optional), "balance": ... (optional) }`)
    *   `GET /api/v1/accounts/<int:account_id>` - Get details for a specific account.
    *   `PUT /api/v1/accounts/<int:account_id>` - Update a specific account.
    *   `DELETE /api/v1/accounts/<int:account_id>` - Delete a specific account.
*   **Transactions (`transactions.py`)** (Auth Required)
    *   `POST /api/v1/transactions` - Add a new transaction. (Body: `{ "date": "YYYY-MM-DD", "payee": "...", "postings": [...] }`)
    *   `GET /api/v1/transactions` - Get all transactions for the current user (supports filtering parameters).
    *   `GET /api/v1/transactions/<int:transaction_id>` - Get a specific transaction.
    *   `PUT /api/v1/transactions/<int:transaction_id>` - Update a transaction.
    *   `DELETE /api/v1/transactions/<int:transaction_id>` - Delete a transaction.
*   **Ledger (`ledger.py`)** (Auth Required)
    *   `GET /api/v1/ledgertransactions` - Get all transactions for the current user in Ledger text format.
*   **Reports (`reports.py`)** (Auth Required)
    *   `GET /api/v1/reports/balance` - Get account balances.
    *   `GET /api/v1/reports/register` - Get transaction register.
    *   `GET /api/v1/reports/balance_report` - Get detailed balance report by account type.
    *   `GET /api/v1/reports/income_statement` - Get income statement (income vs expenses).
*   **Books (`books.py`)** (Auth Required)
    *   `GET /api/v1/books` - Get all books for the current user.
    *   `POST /api/v1/books` - Create a new book.
    *   `GET /api/v1/books/<int:book_id>` - Get a specific book.
    *   `PUT /api/v1/books/<int:book_id>` - Update a book.
    *   `DELETE /api/v1/books/<int:book_id>` - Delete a book.
    *   `GET /api/v1/books/active` - Get the active book.
    *   `PUT /api/v1/books/<int:book_id>/activate` - Set a book as active.

## API Documentation

Kanakku provides Swagger/OpenAPI documentation for its REST API endpoints.

### Accessing the API Documentation

After starting the backend server, you can access the Swagger UI at:
```
http://localhost:8000/api/docs
```

This interactive documentation allows you to:
- Browse all available API endpoints
- View request and response schemas
- Make API requests directly from the browser (with authentication)

### Frontend API Conventions

For frontend API requests:

- **ALWAYS** use the configured axios instance from `frontend/src/api/axiosInstance.js` rather than direct axios imports
- The axiosInstance automatically handles:
  - Authentication (JWT tokens)
  - CSRF protection
  - Error handling and interceptors
  - Base URL configuration

This ensures consistent API request behavior across the application and proper security handling.

### Running Backend with Swagger

To start the backend with Swagger documentation:

```bash
cd backend
./run-backend.sh
```

### Updating API Documentation

The API documentation is defined in `backend/swagger.yaml`. When new endpoints are added or existing ones are modified, the Swagger documentation should be updated accordingly.

## Authentication

Kanakku supports two authentication methods:

1. **Traditional username/password authentication**:
   - Register with an email and password
   - Login with email and password
   - User accounts require activation by an administrator

2. **Google Sign-In**:
   - Sign in with your Google account
   - New users are automatically created and activated
   - Existing users can link their account with Google

3. **API Token Authentication**:
   - Create API tokens for programmatic access
   - Use tokens for automation and integrations
   - Each token can have specific permissions and expiration

### JWT Token Handling

Kanakku uses JWT (JSON Web Tokens) for authentication with the following features:

- Access tokens expire after 24 hours by default
- Automatic token refresh mechanism when tokens expire
- The frontend automatically detects expired tokens and refreshes them
- Endpoint: `POST /api/v1/auth/refresh` to manually refresh tokens
- For testing: `GET /api/v1/auth/test-token-expiration` simulates token expiration

### Setting up Google OAuth

To enable Google Sign-In, you need to:

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Configure the OAuth consent screen
3. Create OAuth client credentials (Web application type)
4. Add authorized JavaScript origins:
   - `http://localhost:8000` (backend development server)
   - `http://localhost:3000` (frontend development server)
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback`
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
    *   `DATABASE_URL`: PostgreSQL database connection string (e.g., `postgresql://user:password@host:port/database`).
    *   `LEDGER_PATH`: Path to the `ledger` executable (if not in system PATH).
5.  Run the backend server:
    ```bash
    ./run-backend.sh
    ```
    The backend will be available at `http://localhost:8000`.

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

## Docker Development

Kanakku provides a Docker-based development environment for easy setup and consistency across different machines.

### Prerequisites
- Docker
- Docker Compose

### Quick Start

1. Clone the repository and navigate to the project root:
   ```bash
   git clone https://github.com/yourusername/kanakku.git
   cd kanakku
   ```

2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Swagger UI: http://localhost:8000/api/docs

### Services
- `web`: Frontend React application
- `api`: Backend Flask API
- `db`: PostgreSQL database
- `redis`: Redis for job queue
- `migrate`: Runs database migrations on startup

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=kanakku
DATABASE_URL=postgresql://postgres:postgres@db:5432/kanakku
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# hCaptcha Configuration (for spam protection)
HCAPTCHA_SECRET_KEY=your-hcaptcha-secret-key
```

For the frontend, create a `.env` file in the `frontend/` directory:
```
# hCaptcha Configuration
REACT_APP_HCAPTCHA_SITE_KEY=your-hcaptcha-site-key
```

**Note**: To get hCaptcha keys:
1. Sign up at [hCaptcha Dashboard](https://dashboard.hcaptcha.com/)
2. Create a new site
3. Copy the Site Key for the frontend environment variable
4. Copy the Secret Key for the backend environment variable

### Useful Commands
- Stop all services: `docker-compose down`
- View logs: `docker-compose logs -f`
- Run tests: `docker-compose run --rm api pytest`
- Access database: `docker-compose exec db psql -U postgres -d kanakku`

## Testing

To run the backend tests:

1.  Ensure the backend virtual environment is active and development dependencies are installed (`pytest`, `pytest-cov`, `pytest-mock`).
2.  Navigate to the `kanakku` root directory.
3.  Run pytest:
    ```bash
    cd backend
    python -m pytest -v tests/
    ```

To run frontend tests:

### Unit Tests
```bash
cd frontend
npm test
```

### End-to-End (E2E) Tests
Kanakku uses Playwright for E2E testing. The tests are located in `frontend/e2e/`.

Run E2E tests with:
```bash
cd frontend
npx playwright test
```

E2E test configuration is in `frontend/playwright.config.js`.

## Activating a User

```
$ cd backend
$ flask shell
>>> from app.models import User
>>> user = User.query.filter_by(email='user@example.com').first()
>>> user.activate()
```

## Deployment

For detailed production deployment instructions, see [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md).

For a pre-deployment checklist, see [PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md).

## Recent Updates and Fixes

### Transaction Updates with Postings
Fixed issue with updating transactions with multiple postings. See `fixes/transaction_update_with_postings_fix.md` for details.

### Rate Limiting Implementation
Added rate limiting for API security with configurable limits for different endpoints. See `docs/rate-limit-configuration.md` for configuration details.

## Bank Transaction Processing

Kanakku includes an automated bank transaction processing system that can:

1. **Fetch Bank Emails**
   - Automatically fetch transaction emails from multiple bank accounts
   - Support for various Indian banks (ICICI, HDFC, SBI, Axis, etc.)
   - Deduplication of processed emails

2. **Extract Transaction Details**
   - Parse transaction amounts, dates, and descriptions
   - Handle different email formats from various banks
   - Extract masked account numbers and merchant details

3. **Automatic Categorization**
   - Map transactions to expense categories
   - Configurable merchant-to-category mapping
   - Support for multiple expense accounts per merchant

4. **Account Mapping**
   - Map bank accounts to ledger accounts
   - Support for multiple account types (Assets, Liabilities)
   - Configurable account hierarchy

### Setting up Bank Transaction Processing

1. Configure Gmail credentials in `.env`:
   ```
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   BANK_EMAILS=alerts@axisbank.com,alerts@icicibank.com
   ```

2. Configure account and expense mapping in `config.toml`:
   ```toml
   [bank-account-map]
   XX1648 = "Assets:Bank:Axis"
   XX0907 = "Liabilities:CC:Axis"

   [expense-account-map]
   "MERCHANT_NAME" = ["Expenses:Category:Subcategory", "Description"]
   ```

3. Run the transaction processor:
   ```bash
   cd banktransactions
   python main.py
   ```

For more details, see the [banktransactions README](banktransactions/README.md).

## Security Features

### Spam Protection

The application includes multiple layers of protection against automated bot registrations:

#### hCaptcha Integration

- **Human Verification**: Users must complete an hCaptcha challenge during registration to verify they are human
- **Server-side Verification**: The backend verifies the hCaptcha response token with hCaptcha's API before processing registration
- **Privacy-focused**: hCaptcha provides a privacy-focused alternative to other CAPTCHA services
- **Configurable**: Uses environment variables for easy configuration across different environments
- **Fallback**: Gracefully handles verification failures and provides clear error messages to users

#### Honeypot Trap

- **Honeypot Field**: The registration form includes a hidden `website` field that is invisible to human users but may be filled by automated bots
- **Bot Detection**: If the honeypot field contains any data during registration, the request is rejected with a generic error message
- **Backward Compatibility**: The system also checks for the legacy `username` honeypot field to maintain compatibility
- **Logging**: Honeypot triggers are logged for monitoring purposes, including which field was filled and the attempted value
- **Non-intrusive**: Legitimate users are unaffected as the field is completely hidden from view using CSS positioning and accessibility attributes

This multi-layered approach helps maintain the quality of registered users and significantly reduces spam registrations while providing a good user experience for legitimate users.
