#!/usr/bin/env python3

import json
import logging
import os
from datetime import datetime  # Added for date formatting

import requests

logger = logging.getLogger(__name__)


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
    logger.debug("Starting send_transaction_to_api function")
    logger.debug(
        f"Input transaction data keys: {list(transaction_data.keys()) if transaction_data else 'None'}"
    )

    # Load configuration from environment variables
    logger.debug("Loading API configuration from environment variables...")
    api_endpoint = os.getenv(
        "API_ENDPOINT"
    )  # Should be like http://host/api/v1/transactions
    api_key = os.getenv("API_KEY")
    default_currency = os.getenv("DEFAULT_CURRENCY", "INR")  # Default to INR if not set

    logger.debug(f"API_ENDPOINT: {api_endpoint}")
    logger.debug(f"API_KEY present: {bool(api_key)}")
    logger.debug(f"DEFAULT_CURRENCY: {default_currency}")

    if not api_endpoint or not api_key:
        logger.error("API_ENDPOINT and API_KEY environment variables must be set.")
        logger.debug("Missing required environment variables for API configuration")
        return False

    logger.debug("API configuration loaded successfully")

    # Process amount
    logger.debug("Processing transaction amount...")
    raw_amount = transaction_data.get("amount", 0)
    logger.debug(f"Raw amount value: {raw_amount} (type: {type(raw_amount)})")

    try:
        amount_float = float(raw_amount)
        # The API expects amount as a string within postings
        amount_str = str(amount_float)
        logger.debug(f"Processed amount: {amount_str}")
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid amount format: {raw_amount}. Skipping API call")
        logger.debug(f"Amount processing error: {type(e).__name__}: {str(e)}")
        return False

    # Get date and format it
    logger.debug("Processing transaction date...")
    raw_date = transaction_data.get("transaction_date")
    logger.debug(f"Raw date value: {raw_date} (type: {type(raw_date)})")

    transaction_date_str = None
    if raw_date:
        try:
            logger.debug("Attempting to parse transaction date...")
            # Assuming raw_date is already YYYY-MM-DD or can be parsed
            # Add more robust date parsing if needed
            if isinstance(raw_date, str):
                logger.debug("Date is string, attempting to parse...")
                try:
                    parsed_date = datetime.strptime(raw_date.strip(), "%d-%m-%y")
                    logger.debug("Successfully parsed date with format %d-%m-%y")
                except ValueError:
                    parsed_date = datetime.strptime(raw_date.strip(), "%d-%m-%Y")
                    logger.debug("Successfully parsed date with format %d-%m-%Y")
            elif isinstance(raw_date, datetime.date):
                parsed_date = raw_date
                logger.debug("Date is already a date object")
            elif isinstance(raw_date, datetime):
                parsed_date = raw_date.date()
                logger.debug("Date is datetime object, extracted date part")
            else:
                raise ValueError("Unsupported date type")
            transaction_date_str = parsed_date.strftime("%Y-%m-%d")
            logger.debug(f"Formatted transaction date: {transaction_date_str}")
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid or unparseable date format: {raw_date}. Error: {e}. Skipping API call"
            )
            logger.debug(f"Date parsing error details: {type(e).__name__}: {str(e)}")
            return False
    else:
        logger.error("Missing transaction_date. Skipping API call")
        logger.debug("No transaction_date found in transaction data")
        return False

    # Get account information
    logger.debug("Processing account information...")
    from_account = transaction_data.get("from_account")
    logger.debug(f"From account: {from_account}")

    if not from_account:
        logger.error("Missing from_account. Skipping API call")
        logger.debug("No from_account found in transaction data")
        return False

    to_account = transaction_data.get("to_account")
    logger.debug(f"To account: {to_account}")

    if not to_account:
        logger.error("Missing to_account. Skipping API call")
        logger.debug("No to_account found in transaction data")
        return False

    # --- Construct Payload ---
    logger.debug("Constructing API payload...")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    logger.debug("API headers prepared")

    # Construct the payload based on API requirements
    # NOTE: This assumes a single transaction maps to a single posting.
    # Double-entry may require creating two postings (e.g., debit Expenses, credit Assets).
    # This example creates one posting based on the extracted amount and account_name.

    # Get transaction time from transaction data
    transaction_time = transaction_data.get("transaction_time", "Unknown")
    recipient = transaction_data.get("to_account", "").split(":")[-1]
    recipient_name = transaction_data.get("recipient_name", "Unknown")

    logger.debug(f"Transaction time: {transaction_time}")
    logger.debug(f"Recipient: {recipient}")
    logger.debug(f"Recipient name: {recipient_name}")

    # Create payee string with date and time (if available)
    payee_str = f"{recipient_name} {transaction_time}"
    logger.debug(f"Constructed payee string: {payee_str}")

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

    logger.debug("API payload constructed successfully")
    logger.debug("Payload structure:")
    logger.debug(f"  Date: {payload['date']}")
    logger.debug(f"  Payee: {payload['payee']}")
    logger.debug(f"  Postings count: {len(payload['postings'])}")
    logger.debug(f"  From posting: {payload['postings'][0]}")
    logger.debug(f"  To posting: {payload['postings'][1]}")

    logger.info(
        f"Attempting to send transaction to API: "
        f"Date={transaction_date_str}"
        f"Posting=[Acc: {from_account}, Amt: -{amount_str}]"
        f"Posting=[Acc: {to_account}, Amt: {amount_str}]"
    )
    logger.debug(f"Full payload: {json.dumps(payload)}")  # Log the actual payload

    # Make API request
    logger.debug(f"Making POST request to {api_endpoint}...")
    try:
        logger.debug("Sending HTTP POST request...")
        response = requests.post(
            api_endpoint, headers=headers, json=payload, timeout=15
        )
        logger.debug(f"Received response with status code: {response.status_code}")
        try:
            logger.debug(f"Response headers: {dict(response.headers)}")
        except (TypeError, AttributeError):
            logger.debug("Response headers: <unable to convert to dict>")

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        logger.info(f"API call successful. Status: {response.status_code}")
        logger.debug("Transaction sent to API successfully")
        return True

    except requests.exceptions.Timeout as e:
        logger.error("API call timed out.")
        logger.debug(f"Timeout error details: {type(e).__name__}: {str(e)}")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error("API call failed due to connection error.")
        logger.debug(f"Connection error details: {type(e).__name__}: {str(e)}")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"API HTTP Error: {e.response.status_code}")
        logger.debug(f"HTTP error details: {type(e).__name__}: {str(e)}")
        try:
            # Log the API's error message if available
            error_response = e.response.json()
            logger.error(f"API Response Body: {error_response}")
            logger.debug(f"API error response details: {error_response}")
        except json.JSONDecodeError:
            error_text = e.response.text
            logger.error(f"API Response Body (non-JSON): {error_text}")
            logger.debug(f"API error response text: {error_text}")
        return False
    except requests.exceptions.RequestException as e:
        # Catch any other requests-related errors
        logger.error(f"API request failed: {e}")
        logger.debug(
            f"Request exception details: {type(e).__name__}: {str(e)}", exc_info=True
        )
        return False
    except Exception as e:
        # Catch any unexpected errors during the process
        logger.error(
            f"An unexpected error occurred during API call: {e}", exc_info=True
        )
        logger.debug(f"Unexpected exception details: {type(e).__name__}: {str(e)}")
        return False


class APIClient:
    """
    API client class for creating transactions via the Kanakku API.
    This wraps the existing send_transaction_to_api function for use by the email processor.
    """

    def __init__(self):
        """Initialize the API client."""
        logger.debug("Initializing APIClient instance")

    def create_transaction(self, user_id: int, transaction_data: dict) -> dict:
        """
        Create a transaction via the API.

        Args:
            user_id (int): The user ID (currently not used but kept for compatibility)
            transaction_data (dict): Transaction data to send to the API

        Returns:
            dict: Response with 'success' key indicating if the operation was successful
        """
        logger.debug(f"APIClient.create_transaction called for user_id: {user_id}")
        logger.debug(
            f"Transaction data keys: {list(transaction_data.keys()) if transaction_data else 'None'}"
        )

        try:
            logger.debug("Calling send_transaction_to_api...")
            success = send_transaction_to_api(transaction_data)
            logger.debug(f"send_transaction_to_api returned: {success}")

            result = {
                "success": success,
                "error": None if success else "Failed to create transaction",
            }
            logger.debug(f"APIClient.create_transaction result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in APIClient.create_transaction: {str(e)}")
            logger.debug(
                f"APIClient exception details: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            result = {"success": False, "error": str(e)}
            logger.debug(f"APIClient.create_transaction error result: {result}")
            return result
