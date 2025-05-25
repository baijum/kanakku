# Bank Transaction Email Parser - Restructured

This directory contains the restructured modules for processing and extracting transaction details from bank emails. The modules are now organized into logical groups for better maintainability and clarity.

## Directory Structure

```
banktransactions/
├── core/                    # Core library modules
├── automation/              # Email automation system
├── tests/                   # Organized test suite
├── tools/                   # Development and debugging tools
├── docs/                    # Documentation
├── config/                  # Configuration files
├── data/                    # Runtime data files
└── logs/                    # Log files
```

## Core Modules (`core/`)

The core library contains the fundamental functionality for email processing and transaction extraction:

- **`email_parser.py`** - AI-powered transaction detail extraction using Google Gemini
- **`imap_client.py`** - IMAP client for fetching bank transaction emails
- **`transaction_data.py`** - Transaction data construction and validation
- **`api_client.py`** - RESTful API client for transaction data submission
- **`processed_ids_db.py`** - Database-backed email deduplication

### Key Features
- Handles various Indian bank formats (ICICI, HDFC, SBI, Axis, etc.)
- Extracts comprehensive transaction details (amount, date, account, recipient, etc.)
- Automatic mapping of transactions to expense categories
- Robust email body cleaning and encoding handling

## Automation System (`automation/`)

The automation system provides background processing and scheduling:

- **`run_scheduler.py`** - Main scheduler entry point for periodic job scheduling
- **`run_worker.py`** - Main worker entry point for background job processing
- **`email_processor.py`** - Core email processing worker logic
- **`scheduler.py`** - Job scheduling logic and management
- **`job_utils.py`** - Job utilities and helper functions
- **`job_wrapper.py`** - Job wrapper for reliable process spawning

### Key Features
- Redis Queue (RQ) based background processing
- Configurable polling intervals (hourly, daily)
- User-specific email configurations
- Encrypted credential storage
- Status monitoring and error reporting

## Testing (`tests/`)

Comprehensive test suite organized by functionality:

- **`test_core/`** - Tests for core library modules
- **`test_automation/`** - Tests for automation system
- **`test_integration/`** - Integration and system tests

## Tools (`tools/`)

Development and debugging utilities:

- **`debug_encryption.py`** - Encryption debugging utilities
- **`check_configs.py`** - Configuration validation
- **`check_failed.py`** - Failed job analysis
- **`move_jobs.py`** - Job management utilities
- **`update_test_password.py`** - Test credential management
- **`start_dev.sh`** - Development environment setup

## Documentation (`docs/`)

Comprehensive documentation:

- **`EMAIL_AUTOMATION.md`** - Email automation system guide
- **`SCHEDULER.md`** - Scheduler documentation
- **`JOB_DEDUPLICATION.md`** - Job deduplication strategies
- **`TEST_SUMMARY.md`** - Testing documentation
- **`TEST_README.md`** - Test setup and execution guide

## Configuration (`config/`)

Configuration files and environment settings:

- **`.env`** - Environment variables for development

## Prerequisites

- Python 3.9+
- PostgreSQL database (for API integration)
- Redis (for job queue)
- Google Gemini API key (for AI-powered parsing)

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export DATABASE_URL="postgresql://user:password@localhost/kanakku"
export REDIS_URL="redis://localhost:6379/0"
export GOOGLE_API_KEY="your_gemini_api_key"
export ENCRYPTION_KEY="your_32_byte_base64_encoded_key"
```

### 3. Start the Services

#### Start Email Worker
```bash
cd automation
python run_worker.py
```

#### Start Scheduler (optional)
```bash
cd automation
python run_scheduler.py
```

## Usage

### As a Library

```python
from banktransactions.core import extract_transaction_details

# Extract details from an email body using AI
email_body = "Your account XX1234 has been debited with INR 1,500.00 on 12-12-2023."
transaction_details = extract_transaction_details(email_body)
print(transaction_details)
```

### Testing

Run tests from the project root:
```bash
pytest tests/
```

Run specific test categories:
```bash
pytest tests/test_core/          # Core module tests
pytest tests/test_automation/    # Automation tests
pytest tests/test_integration/   # Integration tests
```

## Integration with Kanakku

These modules integrate with the main Kanakku application through:

1. **Backend API** (`backend/app/email_automation.py`) - REST API for configuration
2. **Frontend UI** - User interface for email automation settings
3. **Database Models** - EmailConfiguration model for user settings

## Error Handling

The modules include robust error handling for:
- Network connectivity issues
- API failures
- AI parsing errors
- Configuration problems
- Invalid transaction data
- Account mapping errors
- Database connection issues

## Migration Notes

This structure represents a major reorganization from the previous layout:
- Core functionality moved to `core/` package
- Automation system flattened from `email_automation/workers/`
- Tests organized by functionality
- Tools and documentation properly separated
- Clear separation of concerns between library and automation

For detailed migration information, see the individual module documentation in `docs/`. 