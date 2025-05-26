import logging
import os
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


def get_mappings_from_api():
    """
    Get mappings from the API.
    Returns a dictionary with bank-account-map and expense-account-map
    based on the format defined in the mappings API.
    """
    logger.debug("Starting get_mappings_from_api function")

    api_endpoint = os.getenv("API_ENDPOINT")
    jwt_token = os.getenv("JWT_TOKEN")

    logger.debug(f"API_ENDPOINT: {api_endpoint}")
    logger.debug(f"JWT_TOKEN present: {bool(jwt_token)}")

    if not api_endpoint or not jwt_token:
        logger.warning("API_ENDPOINT or JWT_TOKEN not set. Unable to get mappings.")
        logger.debug(f"API_ENDPOINT value: {api_endpoint}")
        logger.debug(f"JWT_TOKEN value: {'[REDACTED]' if jwt_token else 'None'}")
        return None

    # Ensure API endpoint is properly formatted
    if not api_endpoint.endswith("/"):
        api_endpoint += "/"
        logger.debug(f"Added trailing slash to API endpoint: {api_endpoint}")

    # Add mappings export endpoint
    export_url = urljoin(api_endpoint, "api/v1/mappings/export")
    logger.debug(f"Constructed export URL: {export_url}")

    # Set up headers with JWT token
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    logger.debug("Headers prepared for API request")

    try:
        logger.debug("Making GET request to mappings API...")
        response = requests.get(export_url, headers=headers)
        logger.debug(f"API response status code: {response.status_code}")
        try:
            logger.debug(f"API response headers: {dict(response.headers)}")
        except (TypeError, AttributeError):
            logger.debug("API response headers: <unable to convert to dict>")

        if response.status_code == 200:
            logger.debug("API request successful, parsing JSON response...")
            mappings = response.json()
            logger.debug(
                f"Received mappings keys: {list(mappings.keys()) if mappings else 'None'}"
            )

            # Validate the expected structure
            if (
                "bank-account-map" not in mappings
                or "expense-account-map" not in mappings
            ):
                logger.error("API response missing required mapping keys")
                logger.debug(f"Available keys in response: {list(mappings.keys())}")
                return None

            bank_account_count = len(mappings.get("bank-account-map", {}))
            expense_account_count = len(mappings.get("expense-account-map", {}))
            logger.debug(f"Bank account mappings count: {bank_account_count}")
            logger.debug(f"Expense account mappings count: {expense_account_count}")
            logger.debug("Successfully loaded mappings from API")
            return mappings
        elif response.status_code == 401:
            logger.error("Authentication failed. JWT token may be invalid or expired.")
            logger.debug("Received 401 Unauthorized response from API")
            return None
        else:
            logger.error(f"Error fetching mappings from API: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error making API request: {str(e)}")
        logger.debug(f"Request exception details: {type(e).__name__}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_mappings_from_api: {str(e)}")
        logger.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
        return None


def construct_transaction_data(transaction):
    """
    Construct transaction data from transaction details.
    Uses mappings from API.
    """
    logger.debug("Starting construct_transaction_data function")
    logger.debug(
        f"Input transaction keys: {list(transaction.keys()) if transaction else 'None'}"
    )
    logger.debug(f"Transaction amount: {transaction.get('amount', 'Not found')}")
    logger.debug(f"Transaction date: {transaction.get('date', 'Not found')}")
    logger.debug(f"Transaction recipient: {transaction.get('recipient', 'Not found')}")
    logger.debug(
        f"Transaction account_number: {transaction.get('account_number', 'Not found')}"
    )

    # Get mappings from API
    logger.debug("Fetching mappings from API...")
    config = get_mappings_from_api()

    # Default mappings if API request fails
    if not config:
        logger.error("Failed to load configuration from API")
        logger.debug("Using default empty mappings")
        bank_account_map = {}
        expense_account_map = {}
    else:
        bank_account_map = config.get("bank-account-map", {})
        expense_account_map = config.get("expense-account-map", {})
        logger.debug(f"Loaded bank account mappings: {len(bank_account_map)} entries")
        logger.debug(
            f"Loaded expense account mappings: {len(expense_account_map)} entries"
        )

    # Default account if no mapping found
    default_expense_account = "Expenses:Groceries"
    default_bank_account = "Assets:Bank:Axis"
    logger.debug(f"Default expense account: {default_expense_account}")
    logger.debug(f"Default bank account: {default_bank_account}")

    # Get recipient info from the mapping or use default
    recipient_name = transaction.get("recipient", "Unknown")
    logger.debug(
        f"Looking up recipient '{recipient_name}' in expense account mappings..."
    )
    recipient_info = expense_account_map.get(
        recipient_name, [default_expense_account, "Unknown"]
    )
    logger.debug(f"Recipient mapping result: {recipient_info}")

    # Get account info from the mapping or use default
    account_number = transaction.get("account_number", "")
    logger.debug(
        f"Looking up account number '{account_number}' in bank account mappings..."
    )
    from_account = bank_account_map.get(account_number, default_bank_account)
    logger.debug(f"Bank account mapping result: {from_account}")

    # Build the transaction data structure
    transaction_data = {
        "amount": transaction["amount"],
        "transaction_date": transaction["date"],
        "transaction_time": transaction.get("transaction_time", "Unknown"),
        "from_account": from_account,
        "to_account": recipient_info[0],
        "recipient_name": recipient_name
        + " "
        + (recipient_info[1] if len(recipient_info) > 1 else ""),
    }

    logger.debug("Constructed transaction data:")
    logger.debug(f"  Amount: {transaction_data['amount']}")
    logger.debug(f"  Date: {transaction_data['transaction_date']}")
    logger.debug(f"  Time: {transaction_data['transaction_time']}")
    logger.debug(f"  From account: {transaction_data['from_account']}")
    logger.debug(f"  To account: {transaction_data['to_account']}")
    logger.debug(f"  Recipient name: {transaction_data['recipient_name']}")

    logger.debug("construct_transaction_data completed successfully")
    return transaction_data
