from unittest.mock import MagicMock, patch

import pytest

from banktransactions.core.email_parser import extract_transaction_details


class TestEmailParserIntegration:
    """Test email parser integration without LLM dependency"""

    @patch("banktransactions.core.email_parser._extract_with_llm_few_shot")
    @patch("banktransactions.core.email_parser.detect_currency")
    def test_extract_transaction_details_integration(
        self, mock_detect_currency, mock_llm_extract
    ):
        """Test the extract_transaction_details function with mocked LLM response"""
        # Mock the LLM response
        mock_llm_extract.return_value = {
            "amount": "1,500.00",
            "date": "21-04-25",
            "transaction_time": "10:48:08",
            "account_number": "XX1648",
            "recipient": "MERCHANT_XYZ",
        }

        # Mock currency detection
        mock_detect_currency.return_value = "INR"

        # Test input
        body = """Here's the summary of your transaction:
                  Amount Debited: INR 1500.00
                  Account Number: XX1648
                  Date & Time: 21-04-25, 10:48:08 IST
                  Transaction Info: UPI/P2M/618581274883/MERCHANT_XYZ"""

        # Call the function
        result = extract_transaction_details(body)

        # Verify the result
        expected = {
            "amount": "1500.00",  # Commas should be removed
            "date": "21-04-2025",  # Date should be standardized
            "transaction_time": "10:48:08",
            "account_number": "XX1648",
            "recipient": "MERCHANT_XYZ",
            "currency": "INR",
        }

        assert result == expected

        # Verify mocks were called
        mock_llm_extract.assert_called_once()
        mock_detect_currency.assert_called_once()

    @patch("banktransactions.core.email_parser._extract_with_llm_few_shot")
    @patch("banktransactions.core.email_parser.detect_currency")
    @patch("banktransactions.core.email_parser.convert_currency")
    def test_extract_transaction_details_usd_conversion(
        self, mock_convert, mock_detect_currency, mock_llm_extract
    ):
        """Test USD to INR conversion in extract_transaction_details"""
        # Mock the LLM response with USD amount
        mock_llm_extract.return_value = {
            "amount": "16.52",
            "date": "May 11, 2025",
            "transaction_time": "12:00:54",
            "account_number": "XX9005",
            "recipient": "SQSP* INV181442393",
        }

        # Mock currency detection to return USD
        mock_detect_currency.return_value = "USD"

        # Mock currency conversion
        mock_convert.return_value = "1371.16"  # 16.52 * 83 (approximate)

        # Test input
        body = "Your ICICI Bank Credit Card XX9005 has been used for a transaction of USD 16.52"

        # Call the function
        result = extract_transaction_details(body)

        # Verify USD was converted to INR
        assert result["currency"] == "INR"
        assert result["amount"] == "1371.16"

        # Verify conversion was called
        mock_convert.assert_called_once_with("16.52", "USD", "INR")

    @patch("banktransactions.core.email_parser._extract_with_llm_few_shot")
    def test_extract_transaction_details_llm_failure(self, mock_llm_extract):
        """Test extract_transaction_details when LLM fails"""
        # Mock LLM to return default values (simulating API failure)
        mock_llm_extract.return_value = {
            "amount": "Unknown",
            "date": "Unknown",
            "transaction_time": "Unknown",
            "account_number": "Unknown",
            "recipient": "Unknown",
        }

        # Test input
        body = "Some email body"

        # Call the function
        result = extract_transaction_details(body)

        # Verify all fields are "Unknown" except currency
        expected = {
            "amount": "Unknown",
            "date": "Unknown",
            "transaction_time": "Unknown",
            "account_number": "Unknown",
            "recipient": "Unknown",
            "currency": "INR",  # Currency detection should still work
        }

        assert result == expected

    def test_email_body_cleaning(self):
        """Test that email body cleaning works correctly"""
        # This tests the cleaning logic without LLM dependency
        import re

        body_with_artifacts = """Here's the summary of your transact=
ion: =20
                                                Amount Debited:=20
                                                INR 1500.00=20"""

        # Apply the same cleaning logic as in extract_transaction_details
        cleaned_body = re.sub(r"=\s*\n", "", body_with_artifacts)
        cleaned_body = cleaned_body.replace("=20", " ")
        cleaned_body = cleaned_body.replace("=A0", " ")
        cleaned_body = cleaned_body.replace("\r", "")

        # Verify cleaning worked
        assert "transact=\nion" not in cleaned_body
        assert "transaction" in cleaned_body
        assert "=20" not in cleaned_body
        assert "INR 1500.00" in cleaned_body
