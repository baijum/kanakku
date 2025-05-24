#!/usr/bin/env python3

import pytest
import os
import sys
import json
from unittest.mock import patch, Mock

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from banktransactions.transaction_data import get_mappings_from_api, construct_transaction_data
except ImportError:
    # Fallback to relative import if running from within the directory
    from transaction_data import get_mappings_from_api, construct_transaction_data


class TestGetMappingsFromApi:
    """Test cases for the get_mappings_from_api function."""

    @patch('banktransactions.transaction_data.requests.get')
    @patch.dict(os.environ, {
        'API_ENDPOINT': 'http://localhost:5000',
        'JWT_TOKEN': 'test_jwt_token'
    })
    def test_get_mappings_from_api_success(self, mock_get):
        """Test successful API call to get mappings."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bank-account-map": {
                "XX1648": "Assets:Bank:Axis",
                "XX0907": "Liabilities:CC:Axis"
            },
            "expense-account-map": {
                "BAKE HOUSE": ["Expenses:Food:Restaurant", "Restaurant at Kattangal"],
                "Jio Prepaid": ["Expenses:Mobile:Baiju Jio", "FIXME"]
            }
        }
        mock_get.return_value = mock_response

        result = get_mappings_from_api()

        assert result is not None
        assert "bank-account-map" in result
        assert "expense-account-map" in result
        assert result["bank-account-map"]["XX1648"] == "Assets:Bank:Axis"
        assert result["expense-account-map"]["BAKE HOUSE"] == ["Expenses:Food:Restaurant", "Restaurant at Kattangal"]

        # Verify the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://localhost:5000/api/v1/mappings/export"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_jwt_token"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

    @patch('banktransactions.transaction_data.requests.get')
    @patch.dict(os.environ, {
        'API_ENDPOINT': 'http://localhost:5000/',  # With trailing slash
        'JWT_TOKEN': 'test_jwt_token'
    })
    def test_get_mappings_from_api_endpoint_with_trailing_slash(self, mock_get):
        """Test API call with endpoint that already has trailing slash."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bank-account-map": {},
            "expense-account-map": {}
        }
        mock_get.return_value = mock_response

        get_mappings_from_api()

        # Should not have double slashes
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://localhost:5000/api/v1/mappings/export"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_mappings_from_api_missing_env_vars(self, caplog):
        """Test behavior when environment variables are missing."""
        import logging
        
        with caplog.at_level(logging.WARNING):
            result = get_mappings_from_api()

        assert result is None
        assert "API_ENDPOINT or JWT_TOKEN not set" in caplog.text

    @patch.dict(os.environ, {'API_ENDPOINT': 'http://localhost:5000'}, clear=True)
    def test_get_mappings_from_api_missing_jwt_token(self, caplog):
        """Test behavior when JWT_TOKEN is missing."""
        import logging
        
        with caplog.at_level(logging.WARNING):
            result = get_mappings_from_api()

        assert result is None
        assert "API_ENDPOINT or JWT_TOKEN not set" in caplog.text

    @patch('banktransactions.transaction_data.requests.get')
    @patch.dict(os.environ, {
        'API_ENDPOINT': 'http://localhost:5000',
        'JWT_TOKEN': 'test_jwt_token'
    })
    def test_get_mappings_from_api_401_unauthorized(self, mock_get, caplog):
        """Test handling of 401 Unauthorized response."""
        import logging
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with caplog.at_level(logging.ERROR):
            result = get_mappings_from_api()

        assert result is None
        assert "Authentication failed" in caplog.text

    @patch('banktransactions.transaction_data.requests.get')
    @patch.dict(os.environ, {
        'API_ENDPOINT': 'http://localhost:5000',
        'JWT_TOKEN': 'test_jwt_token'
    })
    def test_get_mappings_from_api_other_error_status(self, mock_get, caplog):
        """Test handling of other error status codes."""
        import logging
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with caplog.at_level(logging.ERROR):
            result = get_mappings_from_api()

        assert result is None
        assert "Error fetching mappings from API: 500" in caplog.text

    @patch('banktransactions.transaction_data.requests.get')
    @patch.dict(os.environ, {
        'API_ENDPOINT': 'http://localhost:5000',
        'JWT_TOKEN': 'test_jwt_token'
    })
    def test_get_mappings_from_api_missing_required_keys(self, mock_get, caplog):
        """Test handling of response missing required keys."""
        import logging
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bank-account-map": {}
            # Missing expense-account-map
        }
        mock_get.return_value = mock_response

        with caplog.at_level(logging.ERROR):
            result = get_mappings_from_api()

        assert result is None
        assert "API response missing required mapping keys" in caplog.text

    @patch('banktransactions.transaction_data.requests.get')
    @patch.dict(os.environ, {
        'API_ENDPOINT': 'http://localhost:5000',
        'JWT_TOKEN': 'test_jwt_token'
    })
    def test_get_mappings_from_api_request_exception(self, mock_get, caplog):
        """Test handling of request exceptions."""
        import logging
        import requests
        
        mock_get.side_effect = requests.RequestException("Connection error")

        with caplog.at_level(logging.ERROR):
            result = get_mappings_from_api()

        assert result is None
        assert "Error making API request: Connection error" in caplog.text


class TestConstructTransactionData:
    """Test cases for the construct_transaction_data function."""

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_success(self, mock_get_mappings):
        """Test successful construction of transaction data."""
        # Mock API response
        mock_get_mappings.return_value = {
            "bank-account-map": {
                "XX1648": "Assets:Bank:Axis",
                "XX0907": "Liabilities:CC:Axis"
            },
            "expense-account-map": {
                "BAKE HOUSE": ["Expenses:Food:Restaurant", "Restaurant at Kattangal"],
                "SUDEESHKUMA": ["Expenses:Groceries", "Unni at West Manassery"]
            }
        }

        transaction = {
            "amount": 500.0,
            "date": "2025-05-18",
            "transaction_time": "12:34:56",
            "account_number": "XX1648",
            "recipient": "BAKE HOUSE"
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["amount"] == 500.0
        assert result["transaction_date"] == "2025-05-18"
        assert result["transaction_time"] == "12:34:56"
        assert result["from_account"] == "Assets:Bank:Axis"
        assert result["to_account"] == "Expenses:Food:Restaurant"
        assert result["recipient_name"] == "BAKE HOUSE Restaurant at Kattangal"

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_unknown_recipient(self, mock_get_mappings):
        """Test construction with unknown recipient (uses defaults)."""
        mock_get_mappings.return_value = {
            "bank-account-map": {
                "XX1648": "Assets:Bank:Axis"
            },
            "expense-account-map": {}
        }

        transaction = {
            "amount": 250.0,
            "date": "2025-05-18",
            "account_number": "XX1648",
            "recipient": "UNKNOWN MERCHANT"
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["amount"] == 250.0
        assert result["from_account"] == "Assets:Bank:Axis"
        assert result["to_account"] == "Expenses:Groceries"  # Default
        assert result["recipient_name"] == "UNKNOWN MERCHANT Unknown"

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_unknown_account(self, mock_get_mappings):
        """Test construction with unknown account number (uses defaults)."""
        mock_get_mappings.return_value = {
            "bank-account-map": {},
            "expense-account-map": {
                "BAKE HOUSE": ["Expenses:Food:Restaurant", "Restaurant at Kattangal"]
            }
        }

        transaction = {
            "amount": 750.0,
            "date": "2025-05-18",
            "account_number": "XX9999",  # Unknown account
            "recipient": "BAKE HOUSE"
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["amount"] == 750.0
        assert result["from_account"] == "Assets:Bank:Axis"  # Default
        assert result["to_account"] == "Expenses:Food:Restaurant"
        assert result["recipient_name"] == "BAKE HOUSE Restaurant at Kattangal"

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_api_failure(self, mock_get_mappings, caplog):
        """Test construction when API call fails."""
        import logging
        
        mock_get_mappings.return_value = None

        transaction = {
            "amount": 300.0,
            "date": "2025-05-18",
            "account_number": "XX1648",
            "recipient": "SOME MERCHANT"
        }

        with caplog.at_level(logging.ERROR):
            result = construct_transaction_data(transaction)

        assert result is not None
        assert result["amount"] == 300.0
        assert result["from_account"] == "Assets:Bank:Axis"  # Default
        assert result["to_account"] == "Expenses:Groceries"  # Default
        assert result["recipient_name"] == "SOME MERCHANT Unknown"
        assert "Failed to load configuration from API" in caplog.text

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_missing_transaction_time(self, mock_get_mappings):
        """Test construction when transaction_time is missing."""
        mock_get_mappings.return_value = {
            "bank-account-map": {"XX1648": "Assets:Bank:Axis"},
            "expense-account-map": {"MERCHANT": ["Expenses:Shopping", "Store"]}
        }

        transaction = {
            "amount": 100.0,
            "date": "2025-05-18",
            "account_number": "XX1648",
            "recipient": "MERCHANT"
            # Missing transaction_time
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["transaction_time"] == "Unknown"

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_missing_recipient(self, mock_get_mappings):
        """Test construction when recipient is missing."""
        mock_get_mappings.return_value = {
            "bank-account-map": {"XX1648": "Assets:Bank:Axis"},
            "expense-account-map": {}
        }

        transaction = {
            "amount": 200.0,
            "date": "2025-05-18",
            "account_number": "XX1648"
            # Missing recipient
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["recipient_name"] == "Unknown Unknown"

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_missing_account_number(self, mock_get_mappings):
        """Test construction when account_number is missing."""
        mock_get_mappings.return_value = {
            "bank-account-map": {},
            "expense-account-map": {"MERCHANT": ["Expenses:Shopping", "Store"]}
        }

        transaction = {
            "amount": 150.0,
            "date": "2025-05-18",
            "recipient": "MERCHANT"
            # Missing account_number
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["from_account"] == "Assets:Bank:Axis"  # Default

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_recipient_info_single_value(self, mock_get_mappings):
        """Test construction when recipient mapping has only one value."""
        mock_get_mappings.return_value = {
            "bank-account-map": {"XX1648": "Assets:Bank:Axis"},
            "expense-account-map": {
                "SIMPLE MERCHANT": ["Expenses:Shopping"]  # Only one value
            }
        }

        transaction = {
            "amount": 400.0,
            "date": "2025-05-18",
            "account_number": "XX1648",
            "recipient": "SIMPLE MERCHANT"
        }

        result = construct_transaction_data(transaction)

        assert result is not None
        assert result["to_account"] == "Expenses:Shopping"
        assert result["recipient_name"] == "SIMPLE MERCHANT "  # Space but no second part

    @patch('banktransactions.transaction_data.get_mappings_from_api')
    def test_construct_transaction_data_all_required_fields(self, mock_get_mappings):
        """Test that all required fields are present in the result."""
        mock_get_mappings.return_value = {
            "bank-account-map": {"XX1648": "Assets:Bank:Axis"},
            "expense-account-map": {"MERCHANT": ["Expenses:Shopping", "Store"]}
        }

        transaction = {
            "amount": 500.0,
            "date": "2025-05-18",
            "transaction_time": "15:30:45",
            "account_number": "XX1648",
            "recipient": "MERCHANT"
        }

        result = construct_transaction_data(transaction)

        # Verify all expected fields are present
        required_fields = [
            "amount", "transaction_date", "transaction_time",
            "from_account", "to_account", "recipient_name"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}" 