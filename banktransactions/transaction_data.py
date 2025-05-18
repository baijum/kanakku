import os
import requests
import logging
from urllib.parse import urljoin

def get_mappings_from_api():
    """
    Get mappings from the API.
    Returns a dictionary with bank-account-map and expense-account-map 
    based on the format defined in the mappings API.
    """
    api_endpoint = os.getenv("API_ENDPOINT")
    jwt_token = os.getenv("JWT_TOKEN")
    
    if not api_endpoint or not jwt_token:
        logging.warning("API_ENDPOINT or JWT_TOKEN not set. Unable to get mappings.")
        return None
    
    # Ensure API endpoint is properly formatted
    if not api_endpoint.endswith("/"):
        api_endpoint += "/"
    
    # Add mappings export endpoint
    export_url = urljoin(api_endpoint, "api/v1/mappings/export")
    
    # Set up headers with JWT token
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(export_url, headers=headers)
        
        if response.status_code == 200:
            mappings = response.json()
            # Validate the expected structure
            if "bank-account-map" not in mappings or "expense-account-map" not in mappings:
                logging.error("API response missing required mapping keys")
                return None
            return mappings
        elif response.status_code == 401:
            logging.error("Authentication failed. JWT token may be invalid or expired.")
            return None
        else:
            logging.error(f"Error fetching mappings from API: {response.status_code}")
            logging.debug(response.text)
            return None
    except requests.RequestException as e:
        logging.error(f"Error making API request: {str(e)}")
        return None

def construct_transaction_data(transaction):
    """
    Construct transaction data from transaction details.
    Uses mappings from API.
    """
    # Get mappings from API
    config = get_mappings_from_api()
    
    # Default mappings if API request fails
    if not config:
        logging.error("Failed to load configuration from API")
        bank_account_map = {}
        expense_account_map = {}
    else:
        bank_account_map = config.get('bank-account-map', {})
        expense_account_map = config.get('expense-account-map', {})

    # Default account if no mapping found
    default_expense_account = 'Expenses:Groceries'
    default_bank_account = 'Assets:Bank:Axis'
    
    # Get recipient info from the mapping or use default
    recipient_name = transaction.get("recipient", "Unknown")
    recipient_info = expense_account_map.get(recipient_name, [default_expense_account, "Unknown"])
    
    # Get account info from the mapping or use default
    account_number = transaction.get("account_number", "")
    from_account = bank_account_map.get(account_number, default_bank_account)
    
    # Build the transaction data structure
    transaction_data = {
        "amount": transaction["amount"],
        "transaction_date": transaction["date"],
        "transaction_time": transaction.get("transaction_time", "Unknown"),
        "from_account": from_account,
        "to_account": recipient_info[0],
        "recipient_name": recipient_name + " " + (recipient_info[1] if len(recipient_info) > 1 else ""),
    }
    return transaction_data