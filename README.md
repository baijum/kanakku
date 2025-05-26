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
- **Email Automation**: Automated bank transaction processing from Gmail
- **AI-Powered Parsing**: Google Gemini LLM for transaction extraction
- **Background Processing**: Redis Queue for asynchronous email processing
- **Secure Configuration**: Encrypted storage of email credentials
- **Few-Shot Learning**: Improves accuracy with user-provided sample emails
- **Comprehensive PostgreSQL Full-Text Search**: Search across ALL transaction and account fields
- **Smart Search Capabilities**:
  - **Financial Data**: Search by amounts (e.g., "100", "50.75"), currencies ("INR", "USD")
  - **Status Search**: Use natural language - "cleared", "pending", "unmarked" instead of symbols
  - **Account Integration**: Search by account names and descriptions
  - **Combined Queries**: "starbucks 50 cleared checking" finds cleared $50 Starbucks transactions in checking accounts
- **Real-time Search**: Debounced search with 300ms delay for responsive UX
- **Prefix Matching**: Supports partial word matching as you type
- **Database Compatibility**: Full PostgreSQL FTS with SQLite fallback for development
- **Admin MCP Server**: Model Context Protocol server for production monitoring and debugging
- **Remote Administration**: Secure SSH-based access to production logs and system metrics
- **Cursor IDE Integration**: Direct access to production diagnostics from development environment

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database
- Redis (for job queue)
- Gmail account with App Password (for bank transaction processing)
- SSH access to production server (for admin MCP server)

## Dependency Management

Kanakku uses a **unified monorepo dependency management** system for simplified development and deployment.

### Key Files

- **`pyproject.toml`**: Central configuration file containing all Python dependencies, tool configurations, and project metadata
- **`requirements.txt`**: Simplified file that installs the project in development mode (`-e .[dev]`)
- **Individual module requirements**: Removed to eliminate duplication and version conflicts

### Unified Dependencies

All Python dependencies are now managed in a single `pyproject.toml` file:

- **Core Flask dependencies**: Latest stable versions
- **Database & caching**: PostgreSQL, Redis
- **Authentication & security**: JWT, OAuth, encryption
- **AI & automation**: Google Gemini, background processing
- **Development tools**: pytest, ruff, black
- **Production server**: Gunicorn

### Tool Configuration

All development tools are configured in `pyproject.toml`:

- **Ruff**: Fast Python linter with comprehensive rules
- **Black**: Code formatting with 88-character line length
- **Pytest**: Test discovery and execution

### Benefits

- **No version conflicts**: Single source of truth for all dependencies
- **Simplified installation**: One command installs everything
- **Consistent tooling**: Unified configuration across all modules
- **Easier maintenance**: Update dependencies in one place

## Project Structure

```
kanakku/
├── backend/           # Flask backend
│   ├── app/           # Application package
│   │   ├── __init__.py # App factory
│   │   ├── config.py  # Configuration settings
│   │   ├── extensions.py # Flask extensions (db, jwt)
│   │   ├── models/    # Modular SQLAlchemy models
│   │   │   ├── __init__.py # Model imports
│   │   │   ├── base.py    # Base model class
│   │   │   ├── user.py    # User model
│   │   │   ├── account.py # Account model
│   │   │   ├── transaction.py # Transaction model
│   │   │   ├── book.py    # Book model
│   │   │   └── other.py   # Other models (API tokens, etc.)
│   │   ├── auth_bp/   # Authentication blueprint
│   │   │   ├── __init__.py # Blueprint registration
│   │   │   ├── routes.py  # Authentication routes
│   │   │   ├── services.py # Authentication business logic
│   │   │   └── schemas.py # Validation schemas
│   │   ├── accounts_bp/ # Account management blueprint
│   │   │   ├── __init__.py # Blueprint registration
│   │   │   ├── routes.py  # Account routes
│   │   │   ├── services.py # Account business logic
│   │   │   └── schemas.py # Validation schemas
│   │   ├── transactions_bp/ # Transaction management blueprint
│   │   │   ├── __init__.py # Blueprint registration
│   │   │   ├── routes.py  # Transaction routes
│   │   │   ├── services.py # Transaction business logic
│   │   │   └── schemas.py # Validation schemas
│   │   ├── books_bp/  # Book management blueprint
│   │   │   ├── __init__.py # Blueprint registration
│   │   │   ├── routes.py  # Book routes
│   │   │   ├── services.py # Book business logic
│   │   │   └── schemas.py # Validation schemas
│   │   ├── reports_bp/ # Reporting blueprint
│   │   │   ├── __init__.py # Blueprint registration
│   │   │   ├── routes.py  # Report routes
│   │   │   ├── services.py # Report business logic
│   │   │   └── schemas.py # Validation schemas
│   │   ├── shared/    # Shared utilities and services
│   │   │   ├── __init__.py
│   │   │   ├── services.py # Common service functions
│   │   │   ├── schemas.py # Shared validation schemas
│   │   │   └── utils.py   # Shared utilities
│   │   ├── api.py     # General API routes (e.g., health check)
│   │   ├── ledger.py  # Ledger-specific routes (e.g., ledger format export)
│   │   ├── preamble.py # Core utilities and constants
│   │   ├── swagger.py # Swagger/OpenAPI documentation handlers
│   │   ├── errors.py  # Error handlers
│   │   ├── mappings.py # Data mapping configurations
│   │   ├── settings.py # Global settings management
│   │   ├── email_automation.py # Email automation features
│   │   └── utils/     # Utility modules
│   │       ├── email_utils.py  # Email handling utilities
│   │       ├── encryption.py  # Encryption utilities
│   │       └── logging_utils.py  # Logging configuration
│   ├── migrations/    # Database migrations (Alembic)
│   ├── swagger.yaml   # OpenAPI specification
│   ├── tests/         # Pytest test suite
│   ├── requirements.txt
│   └── ...
├── tools/            # Command-line tools
│   ├── accountimporter/  # Rust-based account importer
│   └── ledgertransactions/  # Go-based ledger transaction processor
├── hack/             # Debugging and development scripts
│   ├── debug_redis_queue.py  # Redis queue debugging script
│   ├── inspect_queues.py     # Queue inspection tool
│   └── health_check.sh       # System health check script
├── frontend/          # React frontend
│   ├── public/
│   ├── src/           # Source code
│   │   ├── components/ # React components
│   │   ├── api/       # API client code
│   │   └── ...
│   ├── package.json
│   └── ...
├── banktransactions/  # Bank transaction processing
│   ├── email_automation/  # Email automation system
│   │   ├── workers/   # Background workers for email processing
│   │   ├── run_worker.py  # Worker process script
│   │   ├── run_scheduler.py  # Scheduler process script
│   │   └── README.md  # Email automation documentation
│   ├── email_parser.py # Transaction extraction logic
│   ├── imap_client.py # Email fetching and processing
│   ├── api_client.py  # API integration
│   ├── main.py        # Main processing pipeline
│   └── tests/         # Test suite
├── adminserver/       # Admin MCP Server for production monitoring
│   ├── admin_server.py # Main MCP server implementation
│   ├── setup.sh       # Automated setup script
│   ├── deploy-production.sh # Production deployment script
│   ├── cursor-mcp-config.json # Cursor IDE configuration
│   ├── README.md      # Admin server documentation
│   ├── QUICKSTART.md  # Quick setup guide
│   ├── SECURITY.md    # Security guidelines
│   ├── SERVICE_MANAGEMENT.md # Service management guide
│   └── requirements.txt # Python dependencies
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

### CI/CD Pipelines

The project uses GitHub Actions for continuous integration and deployment, with workflows for:

- Linting (`lint-black.yml`)
- Backend testing (`test-backend.yml`)
- Release automation

### Database Migrations

Database schema changes are managed using Alembic migrations, located in `backend/migrations/`. This ensures version-controlled, reproducible database schema updates.

### Deployment Pipeline

Kanakku includes a comprehensive CI/CD pipeline for automated deployment to production servers:

- **Automated Testing**: Runs all backend and frontend tests before deployment
- **Build Process**: Builds React frontend and prepares deployment artifacts
- **SSH Deployment**: Securely deploys to Debian/Ubuntu servers via SSH
- **Health Checks**: Verifies deployment success with automated health checks
- **Rollback Support**: Automatic backup and rollback capabilities
- **Zero-Downtime**: Graceful service restarts with minimal downtime

For deployment setup, see:
- [Quick Start Guide](docs/deployment-quick-start.md) - Get deployed in 10 minutes
- [Comprehensive Deployment Guide](docs/deployment.md) - Detailed setup and configuration
- [Server Setup Script](scripts/server-setup.sh) - Automated server preparation

### Helper Scripts

Root-level scripts for common development tasks:

- `lint.sh` - Run code linting
- `test.sh` - Run test suite

## Core Technologies & Patterns

Kanakku is built using modern technologies and follows established architectural patterns:

### Backend Technologies
- **Python 3.12+**: Modern Python with type hints and async support
- **Flask 3.0+**: Lightweight web framework with Blueprint organization
- **SQLAlchemy 2.0+**: Modern ORM with declarative models
- **PostgreSQL**: Primary database with full-text search capabilities
- **Redis**: Background job queue and caching
- **Flask-JWT-Extended**: JWT-based authentication
- **Google Gemini AI**: LLM for transaction parsing
- **Gunicorn**: Production WSGI server

### Frontend Technologies
- **React 18+**: Modern React with hooks and functional components
- **Material-UI (MUI)**: Component library for consistent UI
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **React Context**: State management for shared data

### Development Tools
- **Ruff**: Fast Python linter and formatter
- **Black**: Code formatting
- **Pytest**: Testing framework with fixtures

### Administration & Monitoring
- **Model Context Protocol (MCP)**: Server protocol for IDE integration
- **SSH**: Secure remote server access
- **systemd**: Service management and monitoring
- **journalctl**: System log access and analysis

### Architectural Patterns

#### Backend Patterns
- **Flask Blueprints**: Modular route organization by feature
- **Service Layer Pattern**: Business logic separated from routes
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Configuration and service management
- **Background Jobs**: Asynchronous processing with Redis Queue

#### Frontend Patterns
- **Feature-based Structure**: Components organized by functionality
- **Custom Hooks**: Reusable stateful logic
- **Context Providers**: Shared state management
- **Error Boundaries**: Graceful error handling
- **Responsive Design**: Mobile-first approach with MUI breakpoints

## Architecture

Kanakku follows a modern, layered architecture with a clear separation between frontend and backend.

- **Frontend:** React application (`frontend/`) providing the user interface. It communicates with the backend via API calls.
  - Uses Material-UI (MUI) for component styling
  - React Router for navigation
  - Axios for API requests
- **Backend:** Flask application (`backend/`) serving a RESTful API. It handles:
  - **Business Logic:** Managing users, accounts, transactions, and book entries.
  - **Database Interaction:** Using SQLAlchemy with modular models (`backend/app/models/`) with a PostgreSQL database for application data.
  - **Authentication:** Utilizing Flask-JWT-Extended for token-based authentication and Google OAuth integration.
  - **Ledger Interaction:** Exporting data in Ledger format and generating reports.
- **API:** Defined using Flask Blueprints, organized by functionality with Swagger/OpenAPI documentation. All endpoints are prefixed with `/api/`.

For a detailed architectural overview, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

For visual architecture diagrams using Mermaid, see [architecture_diagrams.md](docs/architecture_diagrams.md).

## Admin Server (MCP Server)

Kanakku includes a **Model Context Protocol (MCP) server** for production monitoring and debugging directly from Cursor IDE. This enables efficient remote administration without manual SSH access.

### Features

- **Real-time Log Access**: Read application, system, and Nginx logs directly from Cursor
- **Log Search**: Search across multiple log files with time filtering
- **Service Monitoring**: Check status of all Kanakku services (app, worker, scheduler, nginx, postgresql, redis)
- **System Information**: Get server resource usage and performance metrics
- **Safe Command Execution**: Execute read-only system commands with security restrictions
- **Secure SSH Connection**: Uses SSH key authentication for secure remote access

### Available Log Sources

The Admin Server provides access to comprehensive logging across the entire Kanakku stack:

#### Application Logs
- `kanakku_app` - Main Flask application logs
- `kanakku_error` - Application error logs
- `kanakku_worker` - Email automation worker logs
- `kanakku_scheduler` - Email scheduler logs

#### System Service Logs
- `systemd_kanakku` - Kanakku service logs
- `systemd_kanakku_worker` - Worker service logs
- `systemd_kanakku_scheduler` - Scheduler service logs
- `systemd_nginx` - Nginx service logs
- `systemd_postgresql` - PostgreSQL service logs
- `systemd_redis` - Redis service logs

#### Infrastructure Logs
- `nginx_access` / `nginx_error` - Nginx access and error logs
- `syslog` - System messages
- `auth` - Authentication logs
- `fail2ban` - Security logs
- `health_check` - Application health check logs
- `deployment` - Deployment logs

### Quick Setup

1. **Configure environment variables**:
   ```bash
   export KANAKKU_DEPLOY_HOST="your-production-server-ip"
   export KANAKKU_DEPLOY_USER="root"
   export KANAKKU_SSH_KEY_PATH="~/.ssh/kanakku_deploy"
   export KANAKKU_SSH_PORT="22"
   ```

2. **Run setup script**:
   ```bash
   cd adminserver
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure Cursor IDE**:
   Add to Cursor settings:
   ```json
   {
     "mcpServers": {
       "kanakku-admin": {
         "command": "python",
         "args": ["/path/to/adminserver/admin_server.py"],
         "env": {
           "KANAKKU_DEPLOY_HOST": "your-production-server-ip",
           "KANAKKU_DEPLOY_USER": "root",
           "KANAKKU_SSH_KEY_PATH": "~/.ssh/kanakku_deploy",
           "KANAKKU_SSH_PORT": "22"
         }
       }
     }
   }
   ```

### Usage Examples

Once configured, you can use natural language commands in Cursor:

- **"Show me the last 100 lines of the Kanakku application log"**
- **"Search for 'error' in all application logs from the last hour"**
- **"What's the status of all Kanakku services?"**
- **"Check memory usage on the server"**
- **"Find any 500 errors in Nginx logs since yesterday"**

### Documentation

For detailed setup and usage instructions, see:
- [Admin Server README](adminserver/README.md) - Complete setup guide
- [Quick Start Guide](adminserver/QUICKSTART.md) - Fast setup for immediate use
- [Security Guidelines](adminserver/SECURITY.md) - Security best practices
- [Service Management](adminserver/SERVICE_MANAGEMENT.md) - Managing production services

### Development Standards

Kanakku follows comprehensive development standards documented in `.cursor/rules/`:

- **[API Design Standards](.cursor/rules/api_design.mdc)**: REST principles, request/response formats
- **[Backend Standards](.cursor/rules/backend.mdc)**: Flask structure, database patterns, security
- **[Frontend Standards](.cursor/rules/frontend.mdc)**: React components, state management, MUI guidelines
- **[Code Quality Standards](.cursor/rules/code_quality.mdc)**: General standards, refactoring guidelines
- **[Security Standards](.cursor/rules/security.mdc)**: Authentication, input validation, production security
- **[Testing Standards](.cursor/rules/testing.mdc)**: Backend/frontend testing, coverage requirements
- **[Version Control Standards](.cursor/rules/version_control.mdc)**: Git workflow, file management

## API Endpoints

The main API endpoints are served under the `/api/` prefix by the Flask backend. Authentication via JWT (Bearer token in Authorization header) is required for most endpoints.

- **Health Check (`api.py`)**
  - `GET /api/v1/health` (No Auth Required) - Basic health check.
- **Authentication (`auth_bp/`)**
  - `POST /api/v1/auth/register` - Register a new user. (Body: `{ "email": "...", "password": "..." }`)
  - `POST /api/v1/auth/login` - Log in a user. (Body: `{ "email": "...", "password": "..." }`)
  - `POST /api/v1/auth/logout` (Auth Required) - Placeholder for logout (JWT handled client-side).
  - `GET /api/v1/auth/me` (Auth Required) - Get the current logged-in user's details.
  - `POST /api/v1/auth/refresh` (Auth Required) - Refresh an expiring JWT token.
  - `GET /api/v1/auth/test-token-expiration` - Test endpoint that simulates token expiration.
  - `GET /api/v1/auth/google` - Initiate Google OAuth login flow.
  - `GET /api/v1/auth/google/callback` - Callback for Google OAuth.
  - `POST /api/v1/auth/reset-password-request` - Request a password reset.
  - `POST /api/v1/auth/reset-password` - Reset password with token.
  - `GET /api/v1/auth/tokens` - Get all API tokens for the user.
  - `POST /api/v1/auth/tokens` - Create a new API token.
  - `PUT /api/v1/auth/tokens/<token_id>` - Update an API token.
  - `DELETE /api/v1/auth/tokens/<token_id>` - Delete an API token.
- **Accounts (`accounts_bp/`)** (Auth Required)
  - `GET /api/v1/accounts` - Get all accounts for the current user.
  - `POST /api/v1/accounts` - Add a new account. (Body: `{ "name": "...", "description": "..." (optional), "currency": "..." (optional), "balance": ... (optional) }`)
  - `GET /api/v1/accounts/<int:account_id>` - Get details for a specific account.
  - `PUT /api/v1/accounts/<int:account_id>` - Update a specific account.
  - `DELETE /api/v1/accounts/<int:account_id>` - Delete a specific account.
- **Transactions (`transactions_bp/`)** (Auth Required)
  - `POST /api/v1/transactions` - Add a new transaction. (Body: `{ "date": "YYYY-MM-DD", "payee": "...", "postings": [...] }`)
  - `GET /api/v1/transactions` - Get all transactions for the current user (supports filtering parameters).
  - `GET /api/v1/transactions/<int:transaction_id>` - Get a specific transaction.
  - `PUT /api/v1/transactions/<int:transaction_id>` - Update a transaction.
  - `DELETE /api/v1/transactions/<int:transaction_id>` - Delete a transaction.
- **Ledger (`ledger.py`)** (Auth Required)
  - `GET /api/v1/ledgertransactions` - Get all transactions for the current user in Ledger text format.
- **Reports (`reports_bp/`)** (Auth Required)
  - `GET /api/v1/reports/balance` - Get account balances.
  - `GET /api/v1/reports/register` - Get transaction register.
  - `GET /api/v1/reports/balance_report` - Get detailed balance report by account type.
  - `GET /api/v1/reports/income_statement` - Get income statement (income vs expenses).
- **Books (`books_bp/`)** (Auth Required)
  - `GET /api/v1/books` - Get all books for the current user.
  - `POST /api/v1/books` - Create a new book.
  - `GET /api/v1/books/<int:book_id>` - Get a specific book.
  - `PUT /api/v1/books/<int:book_id>` - Update a book.
  - `DELETE /api/v1/books/<int:book_id>` - Delete a book.
  - `GET /api/v1/books/active` - Get the active book.
  - `PUT /api/v1/books/<int:book_id>/activate` - Set a book as active.

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

   ```bash
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

## Setup

### Unified Monorepo Setup (Recommended)

Kanakku now uses a unified monorepo structure with centralized dependency management. This is the recommended approach for development.

1. **Clone and navigate to the project**:

   ```bash
   git clone https://github.com/yourusername/kanakku.git
   cd kanakku
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install all dependencies** (backend, banktransactions, and development tools):

   ```bash
   pip install -e ".[dev]"
   ```

   This single command installs:
   - All backend Flask dependencies
   - Bank transaction processing dependencies
   - Development tools (pytest, ruff, black)
   - Shared utilities

4. **Configure environment variables** (optional - defaults are provided in `backend/app/config.py`):
   - `SECRET_KEY`: A secret key for Flask sessions and security
   - `JWT_SECRET_KEY`: A secret key for JWT generation
   - `DATABASE_URL`: PostgreSQL database connection string (e.g., `postgresql://user:password@host:port/database`)
   - `REDIS_URL`: Redis connection string for background jobs (e.g., `redis://localhost:6379/0`)
   - `GOOGLE_API_KEY`: Google Gemini API key for AI-powered transaction parsing
   - `LEDGER_PATH`: Path to the `ledger` executable (if not in system PATH)

5. **Run the backend server**:

   ```bash
   cd backend
   ./run-backend.sh
   ```

   The backend will be available at `http://localhost:8000`.

### Legacy Individual Module Setup

If you prefer to set up modules individually (not recommended for new development):

#### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables and run as described above.

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Run the frontend development server:

   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend.

## Usage

1. Start both the backend and frontend servers.
2. Access the web interface in your browser (usually `http://localhost:3000`).
3. Register a new user or log in if you already have an account.
4. Use the interface to add accounts and transactions.

## Testing

### Unified Testing (Recommended)

With the monorepo setup, you can run all tests from the project root:

1. **Ensure the virtual environment is active** and dependencies are installed:

   ```bash
   source venv/bin/activate  # If not already active
   pip install -e ".[dev]"   # If not already installed
   ```

2. **Run all backend tests** from the project root:

   ```bash
   python -m pytest backend/tests/ -v
   ```

3. **Run bank transaction tests**:

   ```bash
   python -m pytest banktransactions/tests/ -v
   ```

4. **Run all Python tests** (backend + banktransactions):

   ```bash
   python -m pytest backend/tests/ banktransactions/tests/ -v
   ```

5. **Use the convenience script**:

   ```bash
   ./test.sh
   ```

### Test Configuration

The unified test configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests", "banktransactions/tests"]
pythonpath = ["backend", "banktransactions", "shared"]
addopts = "-v --tb=short"
```

This configuration:
- Automatically discovers tests in both `backend/tests/` and `banktransactions/tests/`
- Sets up Python paths for proper imports
- Provides verbose output with short tracebacks

### Test Coverage

To run tests with coverage reporting:

```bash
python -m pytest backend/tests/ banktransactions/tests/ --cov=backend --cov=banktransactions --cov-report=html
```

Coverage reports will be generated in `htmlcov/` directory.

### Legacy Testing Approach

To run backend tests the traditional way:

1. Ensure the backend virtual environment is active and development dependencies are installed (`pytest`, `pytest-cov`, `pytest-mock`).
2. Navigate to the backend directory:

   ```bash
   cd backend
   python -m pytest -v tests/
   ```

### Frontend Testing

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

```bash
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

## Email Automation System

Kanakku includes a comprehensive email automation system that automatically processes bank transaction emails and creates transactions in your ledger.

### Features

- **Secure Gmail Integration**: Connect your Gmail account using app passwords
- **AI-Powered Parsing**: Uses Google Gemini LLM for intelligent transaction extraction
- **Background Processing**: Redis Queue (RQ) for asynchronous email processing
- **Few-Shot Learning**: Improves accuracy with user-provided sample emails
- **Real-time Monitoring**: Status tracking and error reporting
- **Flexible Scheduling**: Configurable polling intervals (hourly, daily)
- **Manual Triggers**: On-demand email processing

### Quick Setup

1. **Configure Environment Variables**:

   ```bash
   # Add to your .env file
   REDIS_URL=redis://localhost:6379/0
   GOOGLE_API_KEY=your_gemini_api_key
   ENCRYPTION_KEY=your_32_byte_base64_key
   ```

2. **Start Redis Server**:

   ```bash
   redis-server
   ```

3. **Start Email Workers and Scheduler**:

   **Option A: Using executable scripts (recommended)**:
   ```bash
   # Start the email worker (processes jobs)
   kanakku-worker
   
   # Start the scheduler (schedules periodic jobs) - in another terminal
   kanakku-scheduler --interval 300
   ```

   **Option B: Direct Python execution**:
   ```bash
   cd banktransactions/email_automation
   
   # Start the email worker (processes jobs)
   python run_worker.py
   
   # Start the scheduler (schedules periodic jobs) - in another terminal
   python run_scheduler.py --interval 300
   ```

4. **Configure in Web Interface**:
   - Go to Profile Settings → Email Automation
   - Enter Gmail credentials (email + app password)
   - Test connection and enable automation
   - Add sample emails for better AI accuracy

### Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an app password:
   - Google Account → Security → App passwords
   - Generate password for "Mail"
3. Use this app password in Kanakku (not your regular Gmail password)

### Debugging & Troubleshooting

For debugging Redis Queue issues and email automation problems:

- **[Redis Queue Debugging Guide](docs/redis-queue-debugging.md)**: Comprehensive debugging tools and techniques
- **[Quick Reference](docs/redis-queue-quick-reference.md)**: Common commands and quick fixes
- **Debugging Scripts**: Use `hack/debug_redis_queue.py` and `hack/health_check.sh` for system diagnostics

### Architecture

The email automation system consists of:

- **Backend API** (`backend/app/email_automation.py`) - Configuration management
- **Worker System** (`banktransactions/email_automation/workers/`) - Background processing
- **Scheduler** (`banktransactions/email_automation/run_scheduler.py`) - Periodic job scheduling
- **Frontend UI** - User-friendly configuration interface

### Components

#### Email Worker (`kanakku-worker`)
Processes email automation jobs from the Redis queue:
- Connects to Gmail via IMAP
- Extracts transaction data using AI
- Creates transactions in the ledger
- Handles errors and retries

**Usage:**
```bash
# Basic usage
kanakku-worker

# With custom options
kanakku-worker --queue-name email_processing --redis-url redis://localhost:6379/0 --worker-name my_worker
```

#### Scheduler (`kanakku-scheduler`)
Manages periodic email processing:
- Schedules jobs based on user polling intervals (hourly/daily)
- Monitors enabled email configurations
- Enqueues jobs at appropriate times
- Runs continuously in the background

**Usage:**
```bash
# Basic usage (5-minute interval)
kanakku-scheduler

# Custom interval (10 minutes)
kanakku-scheduler --interval 600 --redis-url redis://localhost:6379/0
```

**Legacy Direct Execution**: You can still run the scripts directly if needed:
```bash
cd banktransactions/email_automation
python run_worker.py
python run_scheduler.py --interval 300
```

### Production Deployment

For production, run workers as systemd services:

```bash
# Start email worker
sudo systemctl start kanakku-email-worker

# Start scheduler (recommended for automatic processing)
sudo systemctl start kanakku-email-scheduler
```

**Environment Variables Required:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis server URL
- `ENCRYPTION_KEY`: 32-byte base64 encoded key for encrypting email passwords

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

**Documentation:**
- [Executable Scripts Guide](docs/executable-scripts.md) - Complete guide to using kanakku-worker and kanakku-scheduler commands
- [Email Automation README](banktransactions/email_automation/README.md) - Complete setup guide
- [Scheduler Documentation](banktransactions/email_automation/SCHEDULER.md) - Detailed scheduler usage and troubleshooting

## Legacy Bank Transaction Processing

Kanakku also includes a legacy command-line bank transaction processing system. For details, see the [banktransactions README](banktransactions/README.md).

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

## Development Standards & Patterns

Kanakku follows comprehensive development standards to ensure code quality, security, and maintainability. These standards are documented in the `.cursor/rules/` directory and are automatically applied during development.

### Technology Stack & Patterns

**Frontend:**

- React 18 with functional components and hooks
- Material-UI (MUI) for consistent UI components
- Axios via configured `axiosInstance` for API requests
- React Router 6 for client-side routing
- Jest and React Testing Library for testing
- Playwright for end-to-end testing

**Backend:**

- Flask with Blueprint organization
- SQLAlchemy ORM with Alembic migrations
- Flask-JWT-Extended for authentication
- PostgreSQL for production database
- Redis Queue (RQ) for background processing
- Pytest for comprehensive testing

**Infrastructure:**

- Nginx for reverse proxy and static file serving
- Gunicorn for production WSGI serving
- GitHub Actions for CI/CD
- SSL/TLS with security headers

### Development Rules

The project includes the following rule sets:

- **[API Design Rules](.cursor/rules/api_design.mdc)**: REST API design principles and standards
- **[Backend Rules](.cursor/rules/backend.mdc)**: Flask application structure and Python coding standards
- **[Code Quality Rules](.cursor/rules/code_quality.mdc)**: General development guidelines and best practices
- **[Cursor Rules](.cursor/rules/cursor_rules.mdc)**: Guidelines for cursor AI rule structure and formatting
- **[Debugging Rules](.cursor/rules/debugging.mdc)**: Error handling and debugging standards
- **[Deployment Rules](.cursor/rules/deployment.mdc)**: Infrastructure and production deployment standards
- **[Frontend Rules](.cursor/rules/frontend.mdc)**: React component standards and UI development guidelines
- **[Markdown Rules](.cursor/rules/markdown.mdc)**: Markdown formatting and documentation standards
- **[Project Management Rules](.cursor/rules/project_management.mdc)**: Project planning and documentation standards
- **[Security Rules](.cursor/rules/security.mdc)**: Security standards for authentication, data protection, and secure coding
- **[Self Improvement Rules](.cursor/rules/self_improve.mdc)**: Guidelines for maintaining and improving the rule system
- **[Testing Rules](.cursor/rules/testing.mdc)**: Comprehensive testing standards for quality assurance
- **[Version Control Rules](.cursor/rules/version_control.mdc)**: Git workflow and file management standards

### Key Development Principles

1. **Security First**: All code follows security best practices with proper authentication, input validation, and data protection
2. **API Consistency**: RESTful API design with consistent patterns and comprehensive documentation
3. **Test Coverage**: High test coverage with both unit and integration tests
4. **Code Quality**: Automated linting, formatting, and code quality checks
5. **Documentation**: Comprehensive documentation for all features and deployment procedures

### Getting Started with Development

1. Review the development rules in `.cursor/rules/` before contributing
2. Use the configured development tools (ESLint, Black, pytest)
3. Follow the established patterns for API design and component structure
4. Write tests for all new features and bug fixes
5. Ensure all CI checks pass before submitting pull requests

For detailed information about specific development standards, refer to the individual rule files in the `.cursor/rules/` directory.

## PostgreSQL Full-Text Search Implementation

#### Database Changes
- Added `search_vector` column (TSVECTOR) to `transaction` table
- Created comprehensive PostgreSQL triggers that automatically update search vectors
- Status mapping: `*` → "Cleared", `!` → "Pending", `NULL` → "Unmarked"
- Amount formatting for both integer and decimal searches
- GIN index for optimal search performance

#### Backend Enhancements
- Enhanced `GET /api/v1/transactions` API with `search` parameter
- Intelligent database detection (PostgreSQL FTS vs SQLite fallback)
- Comprehensive search across: description, payee, amount, currency, status, account name, account description
- Prefix matching support for real-time search

#### Frontend Improvements
- New search input field in ViewTransactions component
- Debounced search (300ms) to prevent excessive API calls
- Helpful search examples and placeholder text
- Responsive grid layout accommodating search field
- Automatic pagination reset when searching

#### Search Examples
```
# Financial searches
"100"           → Find all transactions with amount 100
"50.75"         → Find transactions with exact decimal amounts
"INR"           → Find all INR transactions

# Status searches  
"cleared"       → Find all cleared transactions (status = '*')
"pending"       → Find all pending transactions (status = '!')
"unmarked"      → Find all unmarked transactions (no status)

# Combined searches
"starbucks 50 cleared"              → Cleared $50 Starbucks transactions
"groceries checking unmarked"       → Unmarked grocery transactions in checking account
"100 INR pending"                   → Pending 100 INR transactions
"salary deposit cleared"            → Cleared salary deposits
```

## Search API
```
GET /api/v1/transactions?search={term}&startDate={date}&endDate={date}&limit={n}&offset={n}
```

**Parameters:**
- `search`: Search term for comprehensive FTS
- `startDate`: Filter by start date (YYYY-MM-DD)
- `endDate`: Filter by end date (YYYY-MM-DD)
- `limit`: Number of results per page
- `offset`: Pagination offset

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "date": "2024-01-15",
      "payee": "Starbucks",
      "status": "*",
      "postings": [
        {
          "id": 1,
          "account": "Checking",
          "amount": "50.00",
          "currency": "INR"
        }
      ]
    }
  ],
  "total": 1
}
```

## Database Schema

### Transaction Table (Enhanced)
```sql
CREATE TABLE transaction (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    account_id INTEGER,
    date DATE NOT NULL,
    description VARCHAR(200) NOT NULL,
    payee VARCHAR(100),
    amount FLOAT NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(1),  -- '*' = cleared, '!' = pending, NULL = unmarked
    search_vector TSVECTOR,  -- Full-text search vector
    created_at TIMESTAMP DEFAULT NOW()
);

-- GIN index for efficient full-text search
CREATE INDEX idx_transaction_search_vector ON transaction USING GIN (search_vector);
```

### Search Vector Content
The `search_vector` includes:
- Transaction description and payee
- Formatted amount (both integer and decimal)
- Currency code
- Verbose status ("Cleared", "Pending", "Unmarked")
- Associated account name and description

## Performance Considerations

### Search Performance
- **GIN Index**: Single index covers all search scenarios
- **Efficient Updates**: Triggers only update search vectors when relevant fields change
- **Prefix Matching**: Supports real-time search as users type
- **Scalability**: FTS performance remains consistent as transaction volume grows

### Database Compatibility
- **PostgreSQL**: Full FTS with comprehensive search capabilities
- **SQLite**: Graceful fallback to basic text search for development
- **Automatic Detection**: Backend automatically detects database type

## Contributing

### Code Quality Standards
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React
- Comprehensive error handling and logging
- Write tests for new functionality
- Update documentation for significant changes

### Search Feature Development
- Test with both PostgreSQL and SQLite
- Verify trigger functionality after schema changes
- Test search performance with large datasets
- Ensure frontend search UX remains responsive

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues related to the search functionality:
1. Check database configuration (PostgreSQL vs SQLite)
2. Verify migration has been applied: `python -m flask db current`
3. Test search API directly: `GET /api/v1/transactions?search=test`
4. Check browser console for frontend errors
5. Review backend logs for search query processing
