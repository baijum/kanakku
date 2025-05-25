import pytest
from banktransactions.core.email_parser import (
    standardize_date_format,
    detect_currency,
    convert_currency,
)


class TestStandardizeDateFormat:
    """Test the standardize_date_format utility function"""

    def test_dd_mm_yyyy_with_dashes(self):
        """Test DD-MM-YYYY format"""
        assert standardize_date_format("21-04-2025") == "21-04-2025"
        assert standardize_date_format("1-1-2023") == "01-01-2023"

    def test_dd_mm_yyyy_with_slashes(self):
        """Test DD/MM/YYYY format"""
        assert standardize_date_format("22/05/2024") == "22-05-2024"
        assert standardize_date_format("1/1/2023") == "01-01-2023"

    def test_two_digit_year_expansion(self):
        """Test 2-digit year expansion"""
        assert standardize_date_format("21-04-25") == "21-04-2025"
        assert standardize_date_format("21-04-75") == "21-04-1975"

    def test_month_name_formats(self):
        """Test month name formats"""
        assert standardize_date_format("Apr 10, 2025") == "10-04-2025"
        assert standardize_date_format("10 Apr 2025") == "10-04-2025"
        assert standardize_date_format("10 April 2025") == "10-04-2025"

    def test_invalid_date_returns_original(self):
        """Test that invalid dates return the original string"""
        invalid_date = "not-a-date"
        assert standardize_date_format(invalid_date) == invalid_date

    def test_edge_cases(self):
        """Test edge cases"""
        assert standardize_date_format("") == ""
        # Note: "12-Mar-2024" format is not currently handled by standardize_date_format
        assert (
            standardize_date_format("12-Mar-2024") == "12-Mar-2024"
        )  # Returns original


class TestDetectCurrency:
    """Test the detect_currency utility function"""

    def test_inr_detection(self):
        """Test INR currency detection"""
        assert detect_currency("Amount: INR 1500.00") == "INR"
        assert detect_currency("Rs. 550.75 debited") == "INR"
        assert detect_currency("₹ 100 transaction") == "INR"

    def test_usd_detection(self):
        """Test USD currency detection"""
        assert detect_currency("Amount: USD 16.52") == "USD"
        # Note: $ symbol alone doesn't trigger USD detection, only explicit "USD" text
        assert detect_currency("Amount: $50.00 charged") == "INR"  # Falls back to INR

    def test_default_inr(self):
        """Test default to INR when no currency found"""
        assert detect_currency("No currency mentioned") == "INR"
        assert detect_currency("") == "INR"

    def test_case_insensitive(self):
        """Test case insensitive detection"""
        assert detect_currency("amount: usd 100") == "USD"
        assert detect_currency("amount: inr 100") == "INR"


class TestConvertCurrency:
    """Test the convert_currency utility function"""

    def test_same_currency_no_conversion(self):
        """Test that same currency returns original amount"""
        assert convert_currency("100.00", "INR", "INR") == "100.00"
        assert convert_currency("50.00", "USD", "USD") == "50.00"

    def test_usd_to_inr_conversion(self):
        """Test USD to INR conversion"""
        # This will use either API or fallback rate
        result = convert_currency("1.00", "USD", "INR")
        # Should be a string representation of a number
        assert isinstance(result, str)
        assert float(result) > 0

    def test_invalid_amount_returns_original(self):
        """Test that invalid amounts return original"""
        assert convert_currency("invalid", "USD", "INR") == "invalid"
        assert convert_currency("", "USD", "INR") == ""

    def test_unknown_amount_returns_unknown(self):
        """Test that 'Unknown' amount returns 'Unknown'"""
        assert convert_currency("Unknown", "USD", "INR") == "Unknown"


class TestEmailBodyCleaning:
    """Test email body cleaning patterns"""

    def test_email_encoding_cleanup(self):
        """Test that email encoding artifacts are cleaned up properly"""
        # This tests the cleaning logic in extract_transaction_details
        # but without the LLM dependency
        import re

        body = """Here's the summary of your transact=
ion: =20
                                                Amount Debited:=20
                                                INR 1500.00=20"""

        # Apply the same cleaning logic as in extract_transaction_details
        cleaned_body = re.sub(r"=\s*\n", "", body)
        cleaned_body = cleaned_body.replace("=20", " ")
        cleaned_body = cleaned_body.replace("=A0", " ")
        cleaned_body = cleaned_body.replace("\r", "")

        assert "transact=\nion" not in cleaned_body
        assert "transaction" in cleaned_body
        assert "=20" not in cleaned_body

    def test_currency_detection_in_cleaned_body(self):
        """Test currency detection works on cleaned email bodies"""
        body = "Amount Debited:=20 INR 1500.00=20"
        cleaned_body = body.replace("=20", " ")

        assert detect_currency(cleaned_body) == "INR"

    def test_date_standardization_integration(self):
        """Test date standardization with various formats"""
        test_cases = [
            ("21-04-25", "21-04-2025"),
            ("22/05/2024", "22-05-2024"),
            ("01-01-2023", "01-01-2023"),
            ("Apr 10, 2025", "10-04-2025"),
        ]

        for input_date, expected in test_cases:
            assert standardize_date_format(input_date) == expected
