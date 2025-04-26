# Account Importer for Kanakku

This tool parses a ledger file and extracts account declarations, then creates those accounts in Kanakku using the API.

## Installation

### Prerequisites

- Rust and Cargo (https://rustup.rs)

### Building

```bash
cd tools/accountimporter
cargo build --release
```

The compiled binary will be available at `target/release/accountimporter`.

## Usage

```bash
# Get help
./accountimporter --help

# Basic usage
./accountimporter --file /path/to/journal.ledger --token YOUR_API_TOKEN

# With all options
./accountimporter \
  --file /path/to/journal.ledger \
  --api-url http://localhost:8000 \
  --token YOUR_API_TOKEN \
  --verbose \
  --dry-run
```

### Command-line Options

- `--file`, `-f`: Path to the ledger file to parse (required)
- `--api-url`, `-a`: API URL for the Kanakku backend (default: http://localhost:8000)
- `--token`, `-t`: API token for authenticating with the Kanakku backend (required)
- `--verbose`, `-v`: Enable verbose output
- `--dry-run`, `-d`: Parse the file but don't create accounts

## How It Works

1. The tool scans the ledger file for lines starting with `account ` followed by account names
2. For each account found, it makes an API request to the Kanakku backend to create the account
3. Authentication is handled via API token using the `Token` authentication scheme

## Troubleshooting

### Authentication Issues (401 Unauthorized)

If you receive 401 Unauthorized errors, try:
- Verifying your API token is correct and hasn't expired
- Using `--verbose` to see more details about the request
- Checking if your account is activated in the Kanakku system

### Server Errors (500)

If you receive 500 Internal Server Error responses:
- Check the server logs for more detailed error information
- Verify that the account format matches what the API expects
- Try creating an account manually through another client to confirm API functionality
- Make sure your API token has proper permissions

## Example

Given a ledger file with contents:

```
account Assets:Checking
account Expenses:Groceries
account Income:Salary
```

Running the tool will create these three accounts in Kanakku. 