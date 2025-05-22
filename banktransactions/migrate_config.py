#!/usr/bin/env python3

import os
import sys
import argparse
import json
import requests
from dotenv import load_dotenv
from config_reader import load_config


def main():
    """
    Migrate configuration from TOML file to database API
    """
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Migrate TOML configuration to API database"
    )
    parser.add_argument(
        "--config", default="config.toml", help="Path to TOML config file"
    )
    parser.add_argument("--api-url", help="API URL (default from API_ENDPOINT env var)")
    parser.add_argument("--api-key", help="API key (default from API_KEY env var)")
    parser.add_argument("--book-id", help="Book ID to use for mappings")
    args = parser.parse_args()

    # Get API credentials from args or environment
    api_endpoint = args.api_url or os.getenv("API_ENDPOINT")
    api_key = args.api_key or os.getenv("API_KEY")

    if not api_endpoint or not api_key:
        print(
            "Error: API_ENDPOINT and API_KEY must be provided as arguments or environment variables"
        )
        sys.exit(1)

    # Ensure API endpoint is properly formatted
    if not api_endpoint.endswith("/"):
        api_endpoint += "/"

    # Add mappings import endpoint
    import_url = f"{api_endpoint}api/v1/mappings/import"

    # Load TOML configuration
    config_file = args.config
    config_data = load_config(config_file)

    if not config_data:
        print(f"Error: Could not load configuration from {config_file}")
        sys.exit(1)

    # Ensure we have both required sections
    if (
        "bank-account-map" not in config_data
        or "expense-account-map" not in config_data
    ):
        print(
            "Error: Configuration must contain both 'bank-account-map' and 'expense-account-map' sections"
        )
        sys.exit(1)

    # Prepare data for API import
    import_data = {
        "bank-account-map": config_data["bank-account-map"],
        "expense-account-map": config_data["expense-account-map"],
    }

    # Add book_id if provided
    if args.book_id:
        import_data["book_id"] = args.book_id

    # Print summary of what will be imported
    print(f"Will import {len(import_data['bank-account-map'])} bank account mappings")
    print(
        f"Will import {len(import_data['expense-account-map'])} expense account mappings"
    )

    # Confirm with user
    confirm = input("Do you want to proceed with the import? (y/n): ")
    if confirm.lower() != "y":
        print("Import cancelled")
        sys.exit(0)

    # Make API request to import mappings
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(import_url, json=import_data, headers=headers)

        if response.status_code == 200:
            print("Configuration successfully imported to the database")
            print(response.json().get("message", "Success"))
        else:
            print(f"Error importing configuration: {response.status_code}")
            print(response.text)
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Error making API request: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
