#!/usr/bin/env python3

import email
import json
import logging
import os
import re
from datetime import datetime, timedelta
from email.header import decode_header
from typing import Dict, Optional, Tuple

import requests
from google import genai

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ExchangeRateCache:
    """
    A simple cache for exchange rates with time-based expiration.
    """

    def __init__(self, expiration_minutes: int = 60):
        logger.debug(
            f"Initializing ExchangeRateCache with {expiration_minutes} minute expiration"
        )
        self.cache: Dict[Tuple[str, str], Tuple[float, datetime]] = {}
        self.expiration_minutes = expiration_minutes

    def get(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get the exchange rate from cache if it exists and is not expired.

        Args:
            from_currency (str): Source currency code
            to_currency (str): Target currency code

        Returns:
            Optional[float]: Cached rate if valid, None otherwise
        """
        logger.debug(f"Checking cache for exchange rate {from_currency}/{to_currency}")
        key = (from_currency, to_currency)
        if key in self.cache:
            rate, timestamp = self.cache[key]
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            logger.debug(
                f"Found cached rate for {from_currency}/{to_currency}, age: {age_minutes:.1f} minutes"
            )

            if datetime.now() - timestamp < timedelta(minutes=self.expiration_minutes):
                logger.debug(
                    f"Using cached exchange rate for {from_currency}/{to_currency}: {rate}"
                )
                return rate
            else:
                logger.debug(
                    f"Cached exchange rate for {from_currency}/{to_currency} expired (age: {age_minutes:.1f} min)"
                )
                del self.cache[key]
        else:
            logger.debug(f"No cached rate found for {from_currency}/{to_currency}")
        return None

    def set(self, from_currency: str, to_currency: str, rate: float):
        """
        Store an exchange rate in the cache.

        Args:
            from_currency (str): Source currency code
            to_currency (str): Target currency code
            rate (float): Exchange rate to cache
        """
        key = (from_currency, to_currency)
        self.cache[key] = (rate, datetime.now())
        logger.debug(f"Cached exchange rate for {from_currency}/{to_currency}: {rate}")

    def clear(self):
        """Clear all cached rates."""
        cache_size = len(self.cache)
        self.cache.clear()
        logger.debug(f"Exchange rate cache cleared ({cache_size} entries removed)")


# Create a global cache instance
logger.debug("Creating global exchange rate cache instance")
exchange_rate_cache = ExchangeRateCache()


def decode_str(s):
    """Decode email subject or sender name"""
    logger.debug(f"Decoding string: {s[:50]}{'...' if len(str(s)) > 50 else ''}")
    try:
        decoded, charset = decode_header(s)[0]
        logger.debug(f"Decoded header charset: {charset}")
        if isinstance(decoded, bytes):
            result = decoded.decode(charset or "utf-8", errors="replace")
            logger.debug(
                f"Decoded bytes to string: {result[:50]}{'...' if len(result) > 50 else ''}"
            )
            return result
        logger.debug("String was already decoded")
        return decoded
    except Exception as e:
        logger.error(f"Error decoding string: {e}")
        logger.debug(
            f"Decode error details: {type(e).__name__}: {str(e)}", exc_info=True
        )
        return str(s)  # Fallback to string conversion


def standardize_date_format(date_str):
    """
    Standardize date format to DD-MM-YYYY
    """
    logger.debug(f"Standardizing date format: '{date_str}'")

    try:
        # Handle DD/MM/YYYY or DD-MM-YYYY format
        if re.match(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", date_str):
            logger.debug("Date matches DD/MM/YYYY or DD-MM-YYYY pattern")
            # Replace / with - for consistent parsing
            date_str = date_str.replace("/", "-")
            parts = date_str.split("-")
            logger.debug(f"Date parts: {parts}")

            if len(parts[2]) == 2:  # Handle 2-digit year
                if int(parts[2]) > 50:  # Assume 19xx for years > 50
                    parts[2] = "19" + parts[2]
                    logger.debug(f"Converted 2-digit year to 19xx: {parts[2]}")
                else:  # Assume 20xx for years <= 50
                    parts[2] = "20" + parts[2]
                    logger.debug(f"Converted 2-digit year to 20xx: {parts[2]}")
            # Ensure day and month are 2 digits
            parts[0] = parts[0].zfill(2)
            parts[1] = parts[1].zfill(2)
            result = f"{parts[0]}-{parts[1]}-{parts[2]}"
            logger.debug(f"Standardized date: {result}")
            return result

        # Handle "Apr 10, 2025" or "10 Apr 2025" format
        month_abbrs = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }

        # Try different formats
        logger.debug("Attempting to parse date with various datetime formats")
        for fmt in ["%b %d, %Y", "%d %b %Y", "%b %d %Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                result = dt.strftime("%d-%m-%Y")
                logger.debug(f"Successfully parsed date with format '{fmt}': {result}")
                return result
            except ValueError:
                logger.debug(f"Failed to parse with format '{fmt}'")
                continue

        # More specific pattern matching for "Apr 10, 2025" format
        logger.debug("Attempting regex pattern matching for month abbreviations")
        match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:,|)\s+(\d{4})",
            date_str,
            re.IGNORECASE,
        )
        if match:
            month, day, year = match.groups()
            logger.debug(f"Regex match found: month={month}, day={day}, year={year}")
            month = month_abbrs.get(
                month[:3].title(), "01"
            )  # Default to 01 if month not found
            day = day.zfill(2)  # Ensure 2-digit day
            result = f"{day}-{month}-{year}"
            logger.debug(f"Converted to standardized format: {result}")
            return result

        # Try "10 Apr 2025" format
        logger.debug("Attempting regex pattern matching for day-month-year format")
        match = re.search(
            r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})",
            date_str,
            re.IGNORECASE,
        )
        if match:
            day, month, year = match.groups()
            logger.debug(
                f"Day-month-year regex match: day={day}, month={month}, year={year}"
            )
            month = month_abbrs.get(month[:3].title(), "01")
            day = day.zfill(2)
            result = f"{day}-{month}-{year}"
            logger.debug(f"Converted to standardized format: {result}")
            return result

        # If all parsing attempts fail, return the original string
        logger.warning(f"Could not parse date format '{date_str}', returning original")
        return date_str

    except Exception as e:
        logger.warning(f"Error standardizing date format '{date_str}': {e}")
        logger.debug(
            f"Date standardization error details: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        return date_str


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Get the current exchange rate between two currencies using a free API.
    Uses caching to reduce API calls.

    Args:
        from_currency (str): Source currency code (e.g., 'USD')
        to_currency (str): Target currency code (e.g., 'INR')

    Returns:
        float: Exchange rate or 1.0 if API call fails
    """
    logger.debug(f"Getting exchange rate from {from_currency} to {to_currency}")

    # Check cache first
    cached_rate = exchange_rate_cache.get(from_currency, to_currency)
    if cached_rate is not None:
        logger.debug(f"Using cached exchange rate: {cached_rate}")
        return cached_rate

    logger.debug("No cached rate found, fetching from API")

    try:
        # Using exchangerate-api.com (free tier)
        api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        logger.debug(f"Exchange rate API key present: {bool(api_key)}")

        if not api_key:
            logger.warning("EXCHANGE_RATE_API_KEY not found. Using fallback rate.")
            fallback_rate = 83.0  # Fallback rate for USD to INR
            logger.debug(f"Using fallback rate: {fallback_rate}")
            exchange_rate_cache.set(from_currency, to_currency, fallback_rate)
            return fallback_rate

        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
        logger.debug(f"Making API request to: {url}")

        response = requests.get(url)
        logger.debug(f"API response status: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        logger.debug(f"API response data keys: {list(data.keys())}")

        rate = float(data.get("conversion_rate", 83.0))
        logger.debug(f"Retrieved exchange rate: {rate}")

        # Cache the rate
        exchange_rate_cache.set(from_currency, to_currency, rate)
        logger.debug("Cached exchange rate for future use")

        return rate

    except Exception as e:
        logger.error(
            f"Error fetching exchange rate for {from_currency}/{to_currency}: {e}"
        )
        logger.debug(
            f"Exchange rate API error details: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        fallback_rate = 83.0  # Fallback rate
        logger.debug(f"Using fallback rate due to error: {fallback_rate}")
        return fallback_rate


def convert_currency(amount: str, from_currency: str, to_currency: str) -> str:
    """
    Convert amount from one currency to another.

    Args:
        amount (str): Amount to convert
        from_currency (str): Source currency code
        to_currency (str): Target currency code

    Returns:
        str: Converted amount as string
    """
    try:
        # Convert amount to float
        amount_float = float(amount)

        # If currencies are the same, return original amount
        if from_currency == to_currency:
            return amount

        # Get exchange rate
        rate = get_exchange_rate(from_currency, to_currency)

        # Convert amount
        converted_amount = amount_float * rate

        # Format to 2 decimal places
        return f"{converted_amount:.2f}"

    except (ValueError, TypeError) as e:
        logging.error(f"Error converting currency: {e}")
        return amount


def detect_currency(cleaned_body: str) -> str:
    """
    Detect the currency from the email body.

    Args:
        cleaned_body (str): Cleaned email body text

    Returns:
        str: Currency code ('USD' or 'INR')
    """
    # Look for USD mentions
    if re.search(r"\bUSD\b", cleaned_body, re.IGNORECASE):
        return "USD"
    # Default to INR for Indian bank emails
    return "INR"


def get_gemini_api_key_from_config():
    """
    Get the Gemini API key from Global Configuration Settings.
    This function handles both Flask context and standalone usage.

    Returns:
        str or None: The decrypted Gemini API key, or None if not found/failed
    """
    try:
        # Try to use Flask context first (if available)
        try:
            # Set up project paths for shared imports
            import sys
            from pathlib import Path

            from flask import current_app

            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from shared.imports import get_gemini_api_token

            # Check if we're in Flask context
            if current_app:
                logging.debug("Using Flask context to get Gemini API key")
                return get_gemini_api_token()
        except (ImportError, RuntimeError):
            # Not in Flask context or Flask not available
            pass

        # Fallback to standalone database access
        logging.debug("Using standalone database access to get Gemini API key")

        # Set up project paths and import utilities from shared package
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from shared.imports import (
            GlobalConfiguration,
            database_session,
            decrypt_value_standalone,
        )

        # Use shared database session utilities
        with database_session() as session:
            # Query for GEMINI_API_TOKEN
            config = (
                session.query(GlobalConfiguration)
                .filter_by(key="GEMINI_API_TOKEN")
                .first()
            )
            if not config:
                logging.debug("GEMINI_API_TOKEN not found in global configurations")
                return None

            # Decrypt if encrypted
            if config.is_encrypted:
                decrypted_value = decrypt_value_standalone(config.value)
                if decrypted_value is None:
                    logging.error("Failed to decrypt GEMINI_API_TOKEN")
                    return None
                return decrypted_value
            else:
                return config.value

    except Exception as e:
        logging.error(f"Error retrieving Gemini API key from config: {str(e)}")
        return None


def extract_transaction_details(body):
    """
    Extract transaction details from email body using only LLM approach,
    with no regex fallback. Returns the same format as other extraction functions.

    Args:
        body (str): Email body text

    Returns:
        dict: Transaction details with keys: amount, date, transaction_time, account_number, recipient, currency
    """
    # Clean the body first
    cleaned_body = re.sub(r"=\s*\n", "", body)
    cleaned_body = cleaned_body.replace("=20", " ")
    cleaned_body = cleaned_body.replace("=A0", " ")
    cleaned_body = cleaned_body.replace("\r", "")

    # Use the few-shot LLM approach
    llm_details = _extract_with_llm_few_shot(cleaned_body)

    # Detect currency
    currency = detect_currency(cleaned_body)
    llm_details["currency"] = currency

    # Clean up amount field (remove commas)
    if llm_details["amount"] != "Unknown":
        llm_details["amount"] = llm_details["amount"].replace(",", "")

    # Post-process date format
    if llm_details["date"] != "Unknown":
        llm_details["date"] = standardize_date_format(llm_details["date"])

    # Convert USD to INR if needed
    if llm_details["currency"] == "USD" and llm_details["amount"] != "Unknown":
        llm_details["amount"] = convert_currency(llm_details["amount"], "USD", "INR")
        llm_details["currency"] = "INR"  # Update currency after conversion

    return llm_details


def _extract_with_llm_few_shot(cleaned_body: str) -> Dict[str, str]:
    """
    Extract transaction details using Google's Gemini LLM with few-shot examples

    Args:
        cleaned_body (str): The cleaned email body text

    Returns:
        dict: Transaction details extracted by the LLM
    """
    # Default values in case of API failures
    default_values = {
        "amount": "Unknown",
        "date": "Unknown",
        "transaction_time": "Unknown",
        "account_number": "Unknown",
        "recipient": "Unknown",
    }

    # Check if API key is available from Global Configuration Settings
    api_key = get_gemini_api_key_from_config()
    if not api_key:
        # Fallback to environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logging.warning(
                "Gemini API key not found in Global Configuration Settings or environment variables. Using regex fallback."
            )
            return default_values

    try:
        # Configure the Gemini API
        client = genai.Client(api_key=api_key)

        # Few-shot examples
        examples = [
            {
                "email": """Your HDFC Bank Credit Card ending 1234 was used for Rs.2,500.00 at AMAZON RETAIL INDIA on 2024-01-15 17:45:32. If not done by you, call 18002586161.""",
                "extraction": {
                    "amount": "2500.00",
                    "date": "2024-01-15",
                    "transaction_time": "17:45:32",
                    "account_number": "XX1234",
                    "recipient": "AMAZON RETAIL INDIA",
                },
            },
            {
                "email": """SBI Transaction Alert: Your account XX7890 has been debited by INR 1,200 on 12-Mar-2024 at 09:30:45 for payment to FLIPKART PVT LTD.""",
                "extraction": {
                    "amount": "1200",
                    "date": "12-Mar-2024",
                    "transaction_time": "09:30:45",
                    "account_number": "XX7890",
                    "recipient": "FLIPKART PVT LTD",
                },
            },
            {
                "email": """ICICI Bank: Rs 350.75 debited from your a/c XX5678 on 22 Apr 2024 for POS tx at SWIGGY. Avl Bal: Rs.12,456.80""",
                "extraction": {
                    "amount": "350.75",
                    "date": "22 Apr 2024",
                    "transaction_time": "Unknown",
                    "account_number": "XX5678",
                    "recipient": "SWIGGY",
                },
            },
            {
                "email": """Your ICICI Bank Credit Card XX9005 has been used for a transaction of USD 16.52 on May 11, 2025 at 12:00:54. Info: SQSP* INV181442393.""",
                "extraction": {
                    "amount": "16.52",
                    "date": "May 11, 2025",
                    "transaction_time": "12:00:54",
                    "account_number": "XX9005",
                    "recipient": "SQSP* INV181442393",
                },
            },
        ]

        # Format examples for the prompt
        examples_text = ""
        for idx, example in enumerate(examples):
            examples_text += f"\nExample {idx+1}:\nEmail: {example['email']}\n"
            examples_text += (
                f"Extraction: {json.dumps(example['extraction'], indent=2)}\n"
            )

        # Prepare the prompt with few-shot examples
        prompt = f"""You are a specialized financial email parser. Extract transaction details from bank notification emails.

Extract the following details from bank transaction emails:
- Amount (in INR/Rs or USD format, return only the number)
- Date (in any format)
- Transaction time (in HH:MM:SS format if available)
- Account number (masked as XXnnnn)
- Recipient/merchant name

Here are some examples of how to extract this information correctly:{examples_text}

Now extract details from this new email:
{cleaned_body}

Return ONLY a valid JSON object with these fields: "amount", "date", "transaction_time", "account_number", "recipient"

If any field cannot be found with high confidence, use "Unknown" as its value.

Follow these rules strictly:
1. Extract only the requested fields.
2. Return values EXACTLY as they appear in the email, following the format shown in the examples.
3. For amount, extract only the numeric value without currency symbols or commas.
4. DO NOT make up or infer values not clearly stated in the email."""

        # Generate response using the Gemini model
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config={
                "temperature": 0.2,
                "top_p": 0.9,
                "response_mime_type": "application/json",
            },
        )

        # Try to extract JSON from the response
        try:
            content = response.text
            # Attempt to parse the JSON response
            extracted_data = json.loads(content)

            # Ensure all required fields are present with proper type checking
            result_data = {}
            required_fields = [
                "amount",
                "date",
                "transaction_time",
                "account_number",
                "recipient",
            ]

            for field in required_fields:
                # Check if field exists and has a string value
                if field in extracted_data and isinstance(extracted_data[field], str):
                    result_data[field] = extracted_data[field]
                else:
                    result_data[field] = "Unknown"

            return result_data

        except (json.JSONDecodeError, IndexError, AttributeError, TypeError) as e:
            logging.error(f"Failed to parse Gemini response: {e}")
            logging.debug(
                f"Raw response: {response.text if hasattr(response, 'text') else str(response)}"
            )
            return default_values

    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return default_values


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        # Read email from file
        with open(sys.argv[1], encoding="utf-8") as f:
            email_text = f.read()

        # Process with pure LLM approach
        msg = email.message_from_string(email_text)
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="replace")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="replace")

        print("Processing email...")
        print("-" * 50)

        # Process with pure LLM approach
        print("Using LLM approach:")
        llm_results = extract_transaction_details(body)
        for field, value in llm_results.items():
            print(f"  {field}: {value}")

        # Check for any "Unknown" values
        missing_fields = [
            field for field, value in llm_results.items() if value == "Unknown"
        ]
        if missing_fields:
            print(f"\nMissing fields: {', '.join(missing_fields)}")
        else:
            print("\n✓ Successfully extracted all fields!")
    else:
        print("Usage: python email_parser.py <email_file_path>")
        print("Example: python email_parser.py your_email.eml")

        # Sample email for testing
        sample_email = """From: ICICI Bank <noreply@icicibank.com>
Subject: Transaction Alert for your ICICI Bank Credit Card
Date: Mon, 10 Apr 2023 13:45:22 +0530

Dear Customer,

Thank you for using your credit card no. XX1234.

Your ICICI Bank Credit Card has been debited with INR 1,235.50 at AMAZON RETAIL INDIA on 10-04-2023 at 13:41:20.

Transaction Info: UPI/P2M/123456/AMAZON

If you have not authorized this transaction, please call our customer service immediately.

Regards,
ICICI Bank"""

        print("\nProcessing sample email...")
        msg = email.message_from_string(sample_email)
        body = msg.get_payload(decode=True).decode(errors="replace")

        llm_results = extract_transaction_details(body)
        for field, value in llm_results.items():
            print(f"  {field}: {value}")
