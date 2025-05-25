#!/usr/bin/env python3

import re
import email
from email.header import decode_header
import logging
from datetime import datetime, timedelta
import json
import os
import requests
from typing import Dict, Any, Optional, Tuple
from google import genai

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ExchangeRateCache:
    """
    A simple cache for exchange rates with time-based expiration.
    """

    def __init__(self, expiration_minutes: int = 60):
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
        key = (from_currency, to_currency)
        if key in self.cache:
            rate, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(minutes=self.expiration_minutes):
                logging.debug(
                    f"Using cached exchange rate for {from_currency}/{to_currency}"
                )
                return rate
            else:
                logging.debug(
                    f"Cached exchange rate for {from_currency}/{to_currency} expired"
                )
                del self.cache[key]
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
        logging.debug(f"Cached exchange rate for {from_currency}/{to_currency}")

    def clear(self):
        """Clear all cached rates."""
        self.cache.clear()
        logging.debug("Exchange rate cache cleared")


# Create a global cache instance
exchange_rate_cache = ExchangeRateCache()


def decode_str(s):
    """Decode email subject or sender name"""
    decoded, charset = decode_header(s)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or "utf-8", errors="replace")
    return decoded


def standardize_date_format(date_str):
    """
    Standardize date format to DD-MM-YYYY
    """
    try:
        # Handle DD/MM/YYYY or DD-MM-YYYY format
        if re.match(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", date_str):
            # Replace / with - for consistent parsing
            date_str = date_str.replace("/", "-")
            parts = date_str.split("-")
            if len(parts[2]) == 2:  # Handle 2-digit year
                if int(parts[2]) > 50:  # Assume 19xx for years > 50
                    parts[2] = "19" + parts[2]
                else:  # Assume 20xx for years <= 50
                    parts[2] = "20" + parts[2]
            # Ensure day and month are 2 digits
            parts[0] = parts[0].zfill(2)
            parts[1] = parts[1].zfill(2)
            return f"{parts[0]}-{parts[1]}-{parts[2]}"

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
        for fmt in ["%b %d, %Y", "%d %b %Y", "%b %d %Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d-%m-%Y")
            except ValueError:
                continue

        # More specific pattern matching for "Apr 10, 2025" format
        match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:,|)\s+(\d{4})",
            date_str,
            re.IGNORECASE,
        )
        if match:
            month, day, year = match.groups()
            month = month_abbrs.get(
                month[:3].title(), "01"
            )  # Default to 01 if month not found
            day = day.zfill(2)  # Ensure 2-digit day
            return f"{day}-{month}-{year}"

        # Try "10 Apr 2025" format
        match = re.search(
            r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})",
            date_str,
            re.IGNORECASE,
        )
        if match:
            day, month, year = match.groups()
            month = month_abbrs.get(month[:3].title(), "01")
            day = day.zfill(2)
            return f"{day}-{month}-{year}"

        # If all parsing attempts fail, return the original string
        return date_str

    except Exception as e:
        logging.warning(f"Error standardizing date format '{date_str}': {e}")
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
    # Check cache first
    cached_rate = exchange_rate_cache.get(from_currency, to_currency)
    if cached_rate is not None:
        return cached_rate

    try:
        # Using exchangerate-api.com (free tier)
        api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        if not api_key:
            logging.warning("EXCHANGE_RATE_API_KEY not found. Using fallback rate.")
            fallback_rate = 83.0  # Fallback rate for USD to INR
            exchange_rate_cache.set(from_currency, to_currency, fallback_rate)
            return fallback_rate

        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        rate = float(data.get("conversion_rate", 83.0))

        # Cache the rate
        exchange_rate_cache.set(from_currency, to_currency, rate)

        return rate

    except Exception as e:
        logging.error(f"Error fetching exchange rate: {e}")
        fallback_rate = 83.0  # Fallback rate for USD to INR
        exchange_rate_cache.set(from_currency, to_currency, fallback_rate)
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
            from flask import current_app
            from app.utils.config_manager import get_gemini_api_token
            
            # Check if we're in Flask context
            if current_app:
                logging.debug("Using Flask context to get Gemini API key")
                return get_gemini_api_token()
        except (ImportError, RuntimeError):
            # Not in Flask context or Flask not available
            pass
        
        # Fallback to standalone database access
        logging.debug("Using standalone database access to get Gemini API key")
        
        # Import encryption utilities
        from cryptography.fernet import Fernet
        import base64
        
        def get_encryption_key_standalone():
            """Get encryption key without Flask context."""
            key = os.environ.get("ENCRYPTION_KEY")
            if not key:
                logging.warning("No encryption key found in environment")
                return None
            
            # Ensure the key is properly formatted for Fernet
            if not key.endswith("="):
                key = key + "=" * (-len(key) % 4)
            
            try:
                decoded_key = base64.urlsafe_b64decode(key)
                if len(decoded_key) != 32:
                    raise ValueError("Invalid key length")
                return key
            except Exception as e:
                logging.error(f"Invalid encryption key: {str(e)}")
                return None
        
        def decrypt_value_standalone(encrypted_value):
            """Decrypt value without Flask context."""
            if not encrypted_value:
                return None
            
            key = get_encryption_key_standalone()
            if not key:
                return None
                
            f = Fernet(key.encode() if isinstance(key, str) else key)
            try:
                decrypted_data = f.decrypt(encrypted_value.encode())
                return decrypted_data.decode()
            except Exception as e:
                logging.error(f"Failed to decrypt value: {str(e)}")
                return None
        
        # Access database directly
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
        
        # Create standalone model
        Base = declarative_base()
        
        class GlobalConfiguration(Base):
            __tablename__ = "global_configurations"
            
            id = Column(Integer, primary_key=True)
            key = Column(String(100), unique=True, nullable=False)
            value = Column(Text, nullable=False)
            description = Column(String(255), nullable=True)
            is_encrypted = Column(Boolean, default=True)
            created_at = Column(DateTime)
            updated_at = Column(DateTime)
        
        # Get database URL
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logging.error("DATABASE_URL environment variable not set")
            return None
        
        # Create database session
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Query for GEMINI_API_TOKEN
            config = session.query(GlobalConfiguration).filter_by(key="GEMINI_API_TOKEN").first()
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
                
        finally:
            session.close()
            
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
            examples_text += f"Extraction: {json.dumps(example['extraction'], indent=2)}\n"

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
        with open(sys.argv[1], "r", encoding="utf-8") as f:
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
