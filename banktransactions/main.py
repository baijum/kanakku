#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
import logging

# --- Import project modules ---
from processed_ids import load_processed_gmail_msgids, save_processed_gmail_msgids
from imap_client import get_bank_emails


# Configure logging
# Recommended level for normal operation: INFO
# Use DEBUG only for troubleshooting
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Add requests library check (kept here for early exit) ---
try:
    import requests
except ImportError:
    logging.critical("The 'requests' library is not installed. Please install it using: pip install requests")
    sys.exit(1)
# ---

# --- Moved function definitions to separate files ---
# load_processed_gmail_msgids -> processed_ids.py
# save_processed_gmail_msgids -> processed_ids.py
# send_transaction_to_api -> api_client.py
# decode_str -> email_parser.py
# extract_transaction_details -> email_parser.py
# get_bank_emails -> imap_client.py

def main():
    """Main function to run the script"""
    # Load environment variables from .env file first
    load_dotenv()

    print("Bank Transaction Email Reader")
    print("=" * 40)

    # Get Gmail credentials from environment variables
    username = os.getenv("GMAIL_USERNAME")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if not username or not password:
        logging.critical(
            "Error: Please set GMAIL_USERNAME and GMAIL_APP_PASSWORD environment variables."
        )
        sys.exit(1)

    # Get bank email addresses from environment variable or use default
    banks_env = os.getenv("BANK_EMAILS", "alerts@axisbank.com")
    bank_emails = [
        email.strip() for email in banks_env.split(",") if email.strip()
    ]  # Ensure non-empty

    logging.info(f"Using Gmail account: {username.split('@')[0]}@****")
    logging.info(f"Searching for transaction emails from: {', '.join(bank_emails)}")

    # Load existing Gmail Message IDs
    processed_gmail_msgids = load_processed_gmail_msgids()
    initial_msgid_count = len(processed_gmail_msgids)

    # Get transactions and update Gmail Message IDs
    # This function now handles connecting, fetching, parsing, and calling the API
    updated_msgids, newly_processed_count = get_bank_emails(
        username, password, bank_emails, processed_gmail_msgids
    )

    # Save updated Gmail Message IDs if any new ones were processed or if the set was loaded
    if newly_processed_count > 0 or processed_gmail_msgids is not None:
        save_processed_gmail_msgids(updated_msgids)

    # Print summary
    print("\n" + "=" * 40)
    logging.info(
        f"Script finished. Processed and sent {newly_processed_count} new transaction(s) to the API."
    )
    print("=" * 40)


if __name__ == "__main__":
    main()
