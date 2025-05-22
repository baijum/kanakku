#!/usr/bin/env python3

import os
import sys
import json
from dotenv import load_dotenv
from transaction_data import get_mappings_from_api, construct_transaction_data


def main():
    """
    Test the API integration for mappings
    """
    # Load environment variables
    load_dotenv()

    # Set API credentials for testing
    os.environ["API_ENDPOINT"] = "http://localhost:5000"
    os.environ["API_KEY"] = (
        "K81Sn0Rp-RmuDzuujBmAWrqMimgRBiW8AhLkdV-STDd0RlJKWV013tZp0Wp8287o"
    )

    print("Testing API integration...")

    # Test get_mappings_from_api()
    print("\nTesting get_mappings_from_api():")
    mappings = get_mappings_from_api()

    if mappings:
        print("Mappings fetched successfully from API!")
        print("\nBank Account Mappings:")
        for account_id, ledger_account in mappings.get("bank-account-map", {}).items():
            print(f"  {account_id} -> {ledger_account}")

        print("\nExpense Account Mappings:")
        for merchant, values in mappings.get("expense-account-map", {}).items():
            if isinstance(values, list) and len(values) > 1:
                print(f"  {merchant} -> {values[0]} ({values[1]})")
            else:
                print(f"  {merchant} -> {values}")
    else:
        print("Failed to fetch mappings from API.")

    # Test construct_transaction_data()
    print("\nTesting construct_transaction_data():")
    sample_transaction = {
        "amount": 500.0,
        "date": "2025-05-18",
        "transaction_time": "12:34:56",
        "account_number": "XX1648",
        "recipient": "BAKE HOUSE",
    }

    transaction_data = construct_transaction_data(sample_transaction)

    if transaction_data:
        print("Transaction data constructed successfully!")
        print(json.dumps(transaction_data, indent=2))
    else:
        print("Failed to construct transaction data.")


if __name__ == "__main__":
    main()
