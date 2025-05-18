# Bank Transaction Email Parser

A robust tool that processes and extracts transaction details from bank emails. The system includes a complete pipeline for email fetching, parsing, and API integration, with automatic expense categorization and account mapping.

## Features

- **Email Processing**
  - Automated fetching of bank transaction emails via IMAP
  - Support for multiple bank email addresses
  - Deduplication of processed emails
  - Robust email body cleaning and encoding handling

- **Transaction Extraction**
  - Advanced pattern matching for transaction details
  - Handles various Indian bank formats (ICICI, HDFC, SBI, Axis, etc.)
  - Extracts comprehensive transaction details:
    - Transaction amount
    - Date and time
    - Account/card number (masked)
    - Recipient/merchant name
    - Transaction type
    - Balance information (when available)

- **Expense Categorization**
  - Automatic mapping of transactions to expense categories
  - Configurable merchant-to-category mapping
  - Support for multiple expense accounts per merchant
  - Customizable transaction descriptions

- **Account Mapping**
  - Automatic mapping of bank accounts to ledger accounts
  - Support for multiple account types (Assets, Liabilities)
  - Configurable account hierarchy
  - Masked account number support

- **API Integration**
  - RESTful API client for transaction data submission
  - Configurable API endpoints
  - Error handling and retry mechanisms
  - Transaction data validation

- **Configuration & Security**
  - Environment-based configuration
  - TOML-based configuration for account and expense mapping
  - Secure credential management
  - Configurable logging levels
  - Support for multiple bank email addresses

## Prerequisites

- Python 3.9+
- Gmail account with App Password enabled
- PostgreSQL database (for API integration)
- Redis (for job queue)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd banktransactions
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

4. Set up environment variables in `.env`:
   ```
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   BANK_EMAILS=alerts@axisbank.com,alerts@icicibank.com
   ```

5. Configure account and expense mapping in `config.toml`:
   ```toml
   [bank-account-map]
   XX1648 = "Assets:Bank:Axis"
   XX0907 = "Liabilities:CC:Axis"

   [expense-account-map]
   "MERCHANT_NAME" = ["Expenses:Category:Subcategory", "Description"]
   ```

## Usage

### As a Module

```python
from email_parser import extract_transaction_details

# Extract details from an email body
email_body = "Your account XX1234 has been debited with INR 1,500.00 on 12-12-2023."
transaction_details = extract_transaction_details(email_body)
print(transaction_details)
```

### Command Line Usage

1. Run the main script to process emails:
   ```bash
   python main.py
   ```

2. Run the example script to test parsing:
   ```bash
   python example_gemini.py sample_email.eml
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Project Structure

- `main.py` - Main entry point for the email processing pipeline
- `email_parser.py` - Core transaction extraction logic
- `imap_client.py` - Email fetching and processing
- `api_client.py` - API integration for transaction submission
- `config_reader.py` - Configuration management
- `processed_ids.py` - Email deduplication handling
- `transaction_data.py` - Data models and validation
- `config.toml` - Account and expense mapping configuration
- `test_*.py` - Test suite for various components

## Configuration

The system can be configured through:

1. Environment variables
2. `config.toml` file for:
   - Bank account mapping
   - Expense category mapping
   - Transaction descriptions
3. Command-line arguments

Key configuration options:
- Gmail credentials
- Bank email addresses
- API endpoints
- Logging levels
- Processing intervals
- Account mappings
- Expense categories

## Testing

The project includes comprehensive tests:
- Unit tests for parsing logic
- Integration tests for email processing
- API client tests
- Configuration tests
- Account mapping tests
- Expense categorization tests

Run tests with:
```bash
pytest
```

## Error Handling

The system includes robust error handling for:
- Network connectivity issues
- API failures
- Email parsing errors
- Configuration problems
- Invalid transaction data
- Account mapping errors
- Expense categorization issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 