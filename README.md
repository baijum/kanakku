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

- **Frontend:** React application (`frontend/`) providing the user interface. It communicates with the backend via API calls.
  - Uses Material-UI (MUI) for component styling
  - React Router for navigation
  - Axios for API requests
- **Backend:** Flask application (`backend/`) serving a RESTful API. It handles:
  - **Business Logic:** Managing users, accounts, transactions, and book entries.
  - **Database Interaction:** Using SQLAlchemy (`backend/app/models.py`) with a PostgreSQL database for application data.
  - **Authentication:** Utilizing Flask-JWT-Extended for token-based authentication and Google OAuth integration.
  - **Ledger Interaction:** Exporting data in Ledger format and generating reports.
- **API:** Defined using Flask Blueprints, organized by functionality with Swagger/OpenAPI documentation. All endpoints are prefixed with `/api/`.

For a detailed architectural overview, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

For visual architecture diagrams using Mermaid, see [architecture_diagrams.md](docs/architecture_diagrams.md).

## API Endpoints

The main API endpoints are served under the `/api/` prefix by the Flask backend. Authentication via JWT (Bearer token in Authorization header) is required for most endpoints.

- **Health Check (`api.py`)**
  - `GET /api/v1/health` (No Auth Required) - Basic health check.
- **Authentication (`auth.py`)**
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
- **Accounts (`accounts.py`)** (Auth Required)
  - `GET /api/v1/accounts` - Get all accounts for the current user.
  - `POST /api/v1/accounts` - Add a new account. (Body: `{ "name": "...", "description": "..." (optional), "currency": "..." (optional), "balance": ... (optional) }`)
  - `GET /api/v1/accounts/<int:account_id>` - Get details for a specific account.
  - `PUT /api/v1/accounts/<int:account_id>` - Update a specific account.
  - `DELETE /api/v1/accounts/<int:account_id>` - Delete a specific account.
- **Transactions (`transactions.py`)** (Auth Required)
  - `POST /api/v1/transactions` - Add a new transaction. (Body: `{ "date": "YYYY-MM-DD", "payee": "...", "postings": [...] }`)
  - `GET /api/v1/transactions` - Get all transactions for the current user (supports filtering parameters).
  - `GET /api/v1/transactions/<int:transaction_id>` - Get a specific transaction.
  - `PUT /api/v1/transactions/<int:transaction_id>` - Update a transaction.
  - `DELETE /api/v1/transactions/<int:transaction_id>` - Delete a transaction.
- **Ledger (`ledger.py`)** (Auth Required)
  - `GET /api/v1/ledgertransactions` - Get all transactions for the current user in Ledger text format.
- **Reports (`reports.py`)** (Auth Required)
  - `GET /api/v1/reports/balance` - Get account balances.
  - `GET /api/v1/reports/register` - Get transaction register.
  - `GET /api/v1/reports/balance_report` - Get detailed balance report by account type.
  - `GET /api/v1/reports/income_statement` - Get income statement (income vs expenses).
- **Books (`books.py`)** (Auth Required)
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

### Backend Setup

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

4. Configure environment variables (optional - defaults are provided in `config.py`):
   - `SECRET_KEY`: A secret key for Flask sessions and security.
   - `JWT_SECRET_KEY`: A secret key for JWT generation.
   - `DATABASE_URL`: PostgreSQL database connection string (e.g., `postgresql://user:password@host:port/database`).
   - `LEDGER_PATH`: Path to the `ledger` executable (if not in system PATH).

5. Run the backend server:

   ```bash
   ./run-backend.sh
   ```

   The backend will be available at `http://localhost:8000`.

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

```bash
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

```bash
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

1. Ensure the backend virtual environment is active and development dependencies are installed (`pytest`, `pytest-cov`, `pytest-mock`).
2. Navigate to the `kanakku` root directory.
3. Run pytest:

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

#### Email Worker (`run_worker.py`)
Processes email automation jobs from the Redis queue:
- Connects to Gmail via IMAP
- Extracts transaction data using AI
- Creates transactions in the ledger
- Handles errors and retries

#### Scheduler (`run_scheduler.py`)
Manages periodic email processing:
- Schedules jobs based on user polling intervals (hourly/daily)
- Monitors enabled email configurations
- Enqueues jobs at appropriate times
- Runs continuously in the background

**Important**: Always run from the `banktransactions/email_automation` directory:
```bash
cd banktransactions/email_automation
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

- Docker and Docker Compose for containerization
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
