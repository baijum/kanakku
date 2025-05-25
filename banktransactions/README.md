# Bank Transaction Email Parser - Core Modules

This directory contains the core modules for processing and extracting transaction details from bank emails. These modules are used by the Redis RQ-based email automation system in Kanakku.

**Note:** The standalone `main.py` script has been replaced by the Redis RQ-based email automation system located in `email_automation/`. This directory now serves as a library of core modules.

## Core Modules

- **Email Processing** (`imap_client.py`)
  - IMAP client for fetching bank transaction emails
  - Support for multiple bank email addresses
  - Robust email body cleaning and encoding handling

- **Transaction Extraction** (`email_parser.py`)
  - AI-powered transaction detail extraction using Google Gemini
  - Handles various Indian bank formats (ICICI, HDFC, SBI, Axis, etc.)
  - Extracts comprehensive transaction details:
    - Transaction amount
    - Date and time
    - Account/card number (masked)
    - Recipient/merchant name
    - Transaction type
    - Balance information (when available)

- **Data Processing** (`transaction_data.py`)
  - Transaction data construction and validation
  - Automatic mapping of transactions to expense categories
  - Configurable merchant-to-category mapping
  - Support for multiple expense accounts per merchant

- **API Integration** (`api_client.py`)
  - RESTful API client for transaction data submission
  - Configurable API endpoints
  - Error handling and retry mechanisms
  - Transaction data validation

- **Deduplication** (`processed_ids_db.py`)
  - Database-backed email deduplication
  - Prevents processing of duplicate emails
  - User-specific message ID tracking

- **Configuration** (`config_reader.py`)
  - TOML-based configuration for account and expense mapping
  - Environment-based configuration support

## Prerequisites

- Python 3.9+
- PostgreSQL database (for API integration)
- Redis (for job queue)
- Google Gemini API key (for AI-powered parsing)

## Usage

These modules are primarily used by the Redis RQ-based email automation system. However, they can also be used independently:

### As a Module

```python
from email_parser import extract_transaction_details_pure_llm

# Extract details from an email body using AI
email_body = "Your account XX1234 has been debited with INR 1,500.00 on 12-12-2023."
transaction_details = extract_transaction_details_pure_llm(email_body)
print(transaction_details)
```

### Testing and Examples

1. Run the example script to test parsing:
   ```bash
   python example_gemini.py sample_email.eml
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Migrate TOML configuration to database:
   ```bash
   python migrate_config.py --config config.toml --api-url http://localhost:5000 --api-key your-api-key
   ```

## Configuration

The modules can be configured through:

1. Environment variables
2. `config.toml` file for:
   - Bank account mapping
   - Expense category mapping
   - Transaction descriptions

Example `config.toml`:
```toml
[bank-account-map]
XX1648 = "Assets:Bank:Axis"
XX0907 = "Liabilities:CC:Axis"

[expense-account-map]
"MERCHANT_NAME" = ["Expenses:Category:Subcategory", "Description"]
```

## Project Structure

- `email_parser.py` - Core AI-powered transaction extraction logic
- `imap_client.py` - Email fetching and processing via IMAP
- `api_client.py` - API integration for transaction submission
- `config_reader.py` - Configuration management for TOML files
- `processed_ids_db.py` - Database-backed email deduplication
- `transaction_data.py` - Data models and validation
- `migrate_config.py` - Utility to migrate TOML config to database
- `example_gemini.py` - Example script for testing AI parsing
- `config.toml` - Account and expense mapping configuration
- `test_*.py` - Test suite for various components
- `email_automation/` - Redis RQ-based email automation system

## Testing

The modules include comprehensive tests:
- Unit tests for AI parsing logic
- Integration tests for email processing
- API client tests
- Configuration tests
- Account mapping tests
- Data validation tests

Run tests with:
```bash
pytest
```

## Integration with Kanakku

These modules are integrated into the main Kanakku application through:

1. **Email Automation System** (`email_automation/`) - Redis RQ-based background processing
2. **Backend API** (`backend/app/email_automation.py`) - REST API for configuration
3. **Frontend UI** - User interface for email automation settings

For the complete email automation setup, see the `email_automation/README.md` file.

## Error Handling

The modules include robust error handling for:
- Network connectivity issues
- API failures
- AI parsing errors
- Configuration problems
- Invalid transaction data
- Account mapping errors
- Database connection issues 