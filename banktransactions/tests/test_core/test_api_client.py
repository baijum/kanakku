#!/usr/bin/env python3

import os
import sys
from datetime import datetime, date
from unittest.mock import patch, Mock

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from banktransactions.api_client import send_transaction_to_api, APIClient
except ImportError:
    # Fallback to relative import if running from within the directory
    from api_client import send_transaction_to_api, APIClient


class TestSendTransactionToApi:
    """Test cases for the send_transaction_to_api function."""

    @patch("banktransactions.api_client.requests.post")
    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
            "DEFAULT_CURRENCY": "INR",
        },
    )
    def test_send_transaction_to_api_success(self, mock_post):
        """Test successful API call to send transaction."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
            "transaction_time": "12:34:56",
            "recipient_name": "BAKE HOUSE Restaurant",
        }

        result = send_transaction_to_api(transaction_data)

        assert result is True
        mock_post.assert_called_once()

        # Verify the API call was made correctly
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:5000/api/v1/transactions"
        assert call_args[1]["headers"]["X-API-Key"] == "test_api_key"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

        # Verify payload structure
        payload = call_args[1]["json"]
        assert payload["date"] == "2025-05-18"
        assert payload["payee"] == "BAKE HOUSE Restaurant 12:34:56"
        assert len(payload["postings"]) == 2
        assert payload["postings"][0]["account"] == "Assets:Bank:Axis"
        assert payload["postings"][0]["amount"] == "-500.0"
        assert payload["postings"][1]["account"] == "Expenses:Food:Restaurant"
        assert payload["postings"][1]["amount"] == "500.0"

    @patch.dict(os.environ, {}, clear=True)
    def test_send_transaction_to_api_missing_env_vars(self, caplog):
        """Test behavior when environment variables are missing."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert (
            "API_ENDPOINT and API_KEY environment variables must be set" in caplog.text
        )

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_invalid_amount(self, caplog):
        """Test behavior with invalid amount."""
        import logging

        transaction_data = {
            "amount": "invalid_amount",
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "Invalid amount format" in caplog.text

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_missing_date(self, caplog):
        """Test behavior when transaction_date is missing."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "Missing transaction_date" in caplog.text

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_invalid_date_format(self, caplog):
        """Test behavior with invalid date format."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "invalid-date",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "Invalid or unparseable date format" in caplog.text

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_missing_from_account(self, caplog):
        """Test behavior when from_account is missing."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "Missing from_account" in caplog.text

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_missing_to_account(self, caplog):
        """Test behavior when to_account is missing."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "Missing to_account" in caplog.text

    @patch("banktransactions.api_client.requests.post")
    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_date_formats(self, mock_post):
        """Test different date formats are handled correctly."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test DD-MM-YY format
        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        result = send_transaction_to_api(transaction_data)
        assert result is True

        payload = mock_post.call_args[1]["json"]
        assert payload["date"] == "2025-05-18"

        # Test DD-MM-YYYY format
        mock_post.reset_mock()
        transaction_data["transaction_date"] = "18-05-2025"

        result = send_transaction_to_api(transaction_data)
        assert result is True

        payload = mock_post.call_args[1]["json"]
        assert payload["date"] == "2025-05-18"

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_datetime_object(self, caplog):
        """Test handling of datetime objects as transaction_date (currently not supported)."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "transaction_date": datetime(2025, 5, 18, 12, 30, 45),
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        # Currently the api_client doesn't properly handle datetime objects
        assert result is False
        assert "Invalid or unparseable date format" in caplog.text

    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_date_object(self, caplog):
        """Test handling of date objects as transaction_date (currently not supported)."""
        import logging

        transaction_data = {
            "amount": 500.0,
            "transaction_date": date(2025, 5, 18),
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        # Currently the api_client doesn't properly handle date objects
        assert result is False
        assert "Invalid or unparseable date format" in caplog.text

    @patch("banktransactions.api_client.requests.post")
    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_default_currency(self, mock_post):
        """Test default currency is used when not specified."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        result = send_transaction_to_api(transaction_data)
        assert result is True

        payload = mock_post.call_args[1]["json"]
        assert payload["postings"][0]["currency"] == "INR"
        assert payload["postings"][1]["currency"] == "INR"

    @patch("banktransactions.api_client.requests.post")
    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_http_error(self, mock_post, caplog):
        """Test handling of HTTP errors."""
        import logging
        import requests

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        mock_response.text = "Bad Request"

        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "API HTTP Error: 400" in caplog.text

    @patch("banktransactions.api_client.requests.post")
    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_timeout(self, mock_post, caplog):
        """Test handling of timeout errors."""
        import logging
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "API call timed out" in caplog.text

    @patch("banktransactions.api_client.requests.post")
    @patch.dict(
        os.environ,
        {
            "API_ENDPOINT": "http://localhost:5000/api/v1/transactions",
            "API_KEY": "test_api_key",
        },
    )
    def test_send_transaction_to_api_connection_error(self, mock_post, caplog):
        """Test handling of connection errors."""
        import logging
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()

        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = send_transaction_to_api(transaction_data)

        assert result is False
        assert "API call failed due to connection error" in caplog.text


class TestAPIClient:
    """Test cases for the APIClient class."""

    def test_api_client_init(self):
        """Test APIClient initialization."""
        client = APIClient()
        assert client is not None

    @patch("banktransactions.api_client.send_transaction_to_api")
    def test_create_transaction_success(self, mock_send):
        """Test successful transaction creation via APIClient."""
        mock_send.return_value = True

        client = APIClient()
        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        result = client.create_transaction(user_id=1, transaction_data=transaction_data)

        assert result["success"] is True
        assert result["error"] is None
        mock_send.assert_called_once_with(transaction_data)

    @patch("banktransactions.api_client.send_transaction_to_api")
    def test_create_transaction_failure(self, mock_send):
        """Test failed transaction creation via APIClient."""
        mock_send.return_value = False

        client = APIClient()
        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        result = client.create_transaction(user_id=1, transaction_data=transaction_data)

        assert result["success"] is False
        assert result["error"] == "Failed to create transaction"
        mock_send.assert_called_once_with(transaction_data)

    @patch("banktransactions.api_client.send_transaction_to_api")
    def test_create_transaction_exception(self, mock_send, caplog):
        """Test exception handling in APIClient.create_transaction."""
        import logging

        mock_send.side_effect = Exception("Test exception")

        client = APIClient()
        transaction_data = {
            "amount": 500.0,
            "transaction_date": "18-05-25",
            "from_account": "Assets:Bank:Axis",
            "to_account": "Expenses:Food:Restaurant",
        }

        with caplog.at_level(logging.ERROR):
            result = client.create_transaction(
                user_id=1, transaction_data=transaction_data
            )

        assert result["success"] is False
        assert result["error"] == "Test exception"
        assert "Error in APIClient.create_transaction" in caplog.text
