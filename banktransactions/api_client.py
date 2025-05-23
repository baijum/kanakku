#!/usr/bin/env python3

import os
import requests
import json
import uuid
import logging
from datetime import datetime  # Added for date formatting


def send_transaction_to_api(transaction_data):
    """
    Sends transaction data to the configured REST API endpoint using the expected format.

    Args:
        transaction_data (dict): Dictionary containing transaction details.
                                 Expected keys include:
                                 'amount', 'transaction_date' (YYYY-MM-DD or parsable),
                                 'payee' (or 'subject' as fallback),
                                 'account_name' (the primary account for the posting),
                                 'from_bank', 'body_excerpt'.

    Returns:
        bool: True if the API call was successful (2xx status), False otherwise.
    """
    # Load configuration from environment variables
    api_endpoint = os.getenv(
        "API_ENDPOINT"
    )  # Should be like http://host/api/v1/transactions
    api_key = os.getenv("API_KEY")
    default_currency = os.getenv("DEFAULT_CURRENCY", "INR")  # Default to INR if not set

    if not api_endpoint or not api_key:
        logging.error("API_ENDPOINT and API_KEY environment variables must be set.")
        return False

    try:
        amount_float = float(transaction_data.get("amount", 0))
        # The API expects amount as a string within postings
        amount_str = str(amount_float)
    except (ValueError, TypeError):
        logging.error(
            f"Invalid amount format: {transaction_data.get('amount')}. Skipping API call"
        )
        return False

    # Get date and format it
    raw_date = transaction_data.get("transaction_date")
    transaction_date_str = None
    if raw_date:
        try:
            # Assuming raw_date is already YYYY-MM-DD or can be parsed
            # Add more robust date parsing if needed
            if isinstance(raw_date, str):
                try:
                    parsed_date = datetime.strptime(raw_date.strip(), "%d-%m-%y")
                except ValueError:
                    parsed_date = datetime.strptime(raw_date.strip(), "%d-%m-%Y")
            elif isinstance(raw_date, datetime.date):
                parsed_date = raw_date
            elif isinstance(raw_date, datetime):
                parsed_date = raw_date.date()
            else:
                raise ValueError("Unsupported date type")
            transaction_date_str = parsed_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError) as e:
            logging.error(
                f"Invalid or unparseable date format: {raw_date}. Error: {e}. Skipping API call"
            )
            return False
    else:
        logging.error(f"Missing transaction_date. Skipping API call")
        return False

    # Get payee (fallback to subject if payee is missing)
    from_account = transaction_data.get("from_account")
    if not from_account:
        logging.error(f"Missing from_account. Skipping API call")
        return False

    # Get account name (use default if missing)
    to_account = transaction_data.get("to_account")
    if not to_account:
        logging.error(f"Missing to_account. Skipping API call")
        return False

    # --- Construct Payload ---

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    # Construct the payload based on API requirements
    # NOTE: This assumes a single transaction maps to a single posting.
    # Double-entry may require creating two postings (e.g., debit Expenses, credit Assets).
    # This example creates one posting based on the extracted amount and account_name.

    # Get transaction time from transaction data
    transaction_time = transaction_data.get("transaction_time", "Unknown")
    recipient = transaction_data.get("to_account", "").split(":")[-1]
    recipient_name = transaction_data.get("recipient_name", "Unknown")

    # Create payee string with date and time (if available)
    payee_str = f"{recipient_name} {transaction_time}"

    payload = {
        "date": transaction_date_str,
        "payee": payee_str,
        "postings": [
            {
                "account": from_account,
                "amount": "-" + amount_str,
                "currency": default_currency,
            },
            {
                "account": to_account,
                "amount": amount_str,
                "currency": default_currency,
            },
        ],
    }

    logging.info(
        f"Attempting to send transaction to API: "
        f"Date={transaction_date_str}"
        f"Posting=[Acc: {from_account}, Amt: -{amount_str}]"
        f"Posting=[Acc: {to_account}, Amt: {amount_str}]"
    )
    logging.debug(f"Payload: {json.dumps(payload)}")  # Log the actual payload

    try:
        response = requests.post(
            api_endpoint, headers=headers, json=payload, timeout=15
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        logging.info(f"API call successful. Status: {response.status_code}")
        return True

    except requests.exceptions.Timeout:
        logging.error(f"API call timed out.")
        return False
    except requests.exceptions.ConnectionError:
        logging.error(f"API call failed due to connection error.")
        return False
    except requests.exceptions.HTTPError as e:
        logging.error(f"API HTTP Error: {e.response.status_code}")
        try:
            # Log the API's error message if available
            logging.error(f"API Response Body: {e.response.json()}")
        except json.JSONDecodeError:
            logging.error(f"API Response Body (non-JSON): {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        # Catch any other requests-related errors
        logging.error(f"API request failed: {e}")
        return False
    except Exception as e:
        # Catch any unexpected errors during the process
        logging.error(
            f"An unexpected error occurred during API call: {e}", exc_info=True
        )
        return False


class APIClient:
    """
    API client class for creating transactions via the Kanakku API.
    This wraps the existing send_transaction_to_api function for use by the email processor.
    """

    def __init__(self):
        """Initialize the API client."""
        pass

    def create_transaction(self, user_id: int, transaction_data: dict) -> dict:
        """
        Create a transaction via the API.

        Args:
            user_id (int): The user ID (currently not used but kept for compatibility)
            transaction_data (dict): Transaction data to send to the API

        Returns:
            dict: Response with 'success' key indicating if the operation was successful
        """
        try:
            success = send_transaction_to_api(transaction_data)
            return {
                "success": success,
                "error": None if success else "Failed to create transaction",
            }
        except Exception as e:
            logging.error(f"Error in APIClient.create_transaction: {str(e)}")
            return {"success": False, "error": str(e)}
