import pytest
from banktransactions.core.email_parser import extract_transaction_details

# Sample bodies based on provided files and potential variations
SAMPLE_BODY_1 = """
Here's the summary of your transact=
ion: =20
                                                Amount Debited:=20
                                                INR 1500.00=20
                                                Account Number:=20
                                                XX1648=20
                                                Date & Time:=20
                                                21-04-25, 10:48:08 IST=20
                                                Transaction Info:=20
                                                UPI/P2M/618581274883/MERCHANT_XYZ=20
                                        If this transaction was not initiat=
ed by you: =20
"""

# Modified Sample 1: Different date format, 'Rs.' instead of INR, different payee format
SAMPLE_BODY_1_VAR1 = """
Here's the summary of your transaction:
                                                Amount Debited:
                                                Rs. 550.75
                                                Account Number:
                                                XX9999
                                                Date & Time:
                                                22/05/2024
                                                Transaction Info:
                                                IMPS/Ref123/SOME_STORE=
                                        If this transaction was not initiated by you:
"""

# Modified Sample 1: Missing recipient
SAMPLE_BODY_1_MISSING_RECIPIENT = """
Here's the summary of your transaction:
                                                Amount Debited: INR 200.00
                                                Account Number: XX1234
                                                Date & Time: 01-01-2023, 00:00:00 IST
                                                Transaction Info: UPI/P2A/12345
                                        If this transaction was not initiated by you:
"""


SAMPLE_BODY_2 = """
               =A0 25-04-2025 Dear Customer, Thank you for using yo=
ur credit card no. XX0907 for INR 870 at MERCHANT_ABC on 25-04-2025 11:32:05=
 IST. The total credit limit ... Regards,  Axis Bank Ltd  . =20
"""

# Modified Sample 2: Amount with 'Rs.', no account number
SAMPLE_BODY_2_VAR1 = """
               25-04-2025 Dear User, Thank you for your transaction=
 for Rs. 99.00 at ANOTHER_STORE on 25-04-2025 12:00:00 IST. Regards,  Bank =20
"""

# Modified Sample 2: Missing date
SAMPLE_BODY_2_MISSING_DATE = """
               Dear User, Thank you for using your credit card no. XX5678=
 for INR 100.00 at TEST_VENDOR. Regards,  Bank Ltd  . =20
"""

# Body with no relevant transaction info
NO_TRANSACTION_INFO = """
Dear Customer, Your monthly statement is ready. Please log in to view.
"""


# Test function using parametrize for multiple inputs/outputs
@pytest.mark.parametrize(
    "body, expected_details",
    [
        # Test Case 1: Based on sample1.txt
        (
            SAMPLE_BODY_1,
            {
                "amount": "1500.00",
                "date": "21-04-2025",  # LLM expands 2-digit year to 4-digit
                "transaction_time": "10:48:08",
                "account_number": "XX1648",
                "recipient": "MERCHANT_XYZ",
                "currency": "INR",
            },
        ),
        # Test Case 2: Variation of sample1.txt (Rs., different date, store name)
        (
            SAMPLE_BODY_1_VAR1,
            {
                "amount": "550.75",
                "date": "22-05-2024",  # Date gets standardized to DD-MM-YYYY format
                "transaction_time": "Unknown",
                "account_number": "XX9999",
                "recipient": "SOME_STORE",
                "currency": "INR",
            },
        ),
        # Test Case 3: Sample 1 missing recipient
        (
            SAMPLE_BODY_1_MISSING_RECIPIENT,
            {
                "amount": "200.00",
                "date": "01-01-2023",
                "transaction_time": "00:00:00",
                "account_number": "XX1234",
                "recipient": "UPI/P2A/12345",  # LLM extracts this from transaction info
                "currency": "INR",
            },
        ),
        # Test Case 4: Based on sample2.txt
        (
            SAMPLE_BODY_2,
            {
                "amount": "870",
                "date": "25-04-2025",
                "transaction_time": "11:32:05",
                "account_number": "XX0907",
                "recipient": "MERCHANT_ABC",
                "currency": "INR",
            },
        ),
        # Test Case 5: Variation of sample2.txt (Rs., no account)
        (
            SAMPLE_BODY_2_VAR1,
            {
                "amount": "99.00",
                "date": "25-04-2025",
                "transaction_time": "12:00:00",
                "account_number": "Unknown",
                "recipient": "ANOTHER_STORE",
                "currency": "INR",
            },
        ),
        # Test Case 6: Sample 2 missing date
        (
            SAMPLE_BODY_2_MISSING_DATE,
            {
                "amount": "100.00",
                "date": "Unknown",
                "transaction_time": "Unknown",
                "account_number": "XX5678",
                "recipient": "TEST_VENDOR",
                "currency": "INR",
            },
        ),
        # Test Case 7: Body with no transaction info
        (
            NO_TRANSACTION_INFO,
            {
                "amount": "Unknown",
                "date": "Unknown",
                "transaction_time": "Unknown",
                "account_number": "Unknown",
                "recipient": "Unknown",
                "currency": "INR",
            },
        ),
        # Test Case 9: Test recipient cleaning (= artifact)
        (
            "Transaction Info: UPI/ABC/DEF/GENERIC_PAYEE=\n",
            {
                "amount": "Unknown",
                "date": "Unknown",
                "transaction_time": "Unknown",
                "account_number": "Unknown",
                "recipient": "GENERIC_PAYEE",  # LLM extracts this from the transaction info
                "currency": "INR",
            },
        ),
        # Test Case 10: Test alternative date format (DD Mon YYYY) - Requires adding pattern
        (
            "Amount: Rs. 500. Date: 20 Jun 2024. Account: XX1111. Info: Test/VENDOR_XYZ",
            {
                "amount": "500",
                "date": "20-06-2024",  # Date gets standardized to DD-MM-YYYY format
                "transaction_time": "Unknown",
                "account_number": "XX1111",
                "recipient": "Test/VENDOR_XYZ",  # LLM extracts full info string
                "currency": "INR",
            },
        ),
    ],
)
def test_extract_transaction_details(body, expected_details):
    assert extract_transaction_details(body) == expected_details


# Specific test for the date format in SAMPLE_BODY_1_VAR1 if the main parametrize fails
def test_date_format_dd_mm_yyyy_slash():
    body = "Date & Time: 22/05/2024"
    details = extract_transaction_details(body)
    # Date gets standardized to DD-MM-YYYY format by the wrapper function
    assert details["date"] == "22-05-2024"


# Note: Some test cases (like 10) might fail initially if the regex patterns
# in extract_transaction_details_pure_llm don't cover those specific formats yet.
# These failing tests indicate where the function needs to be improved.
# The test `test_date_format_dd_mm_yyyy_slash` specifically checks a format
# that might be missed by the current date patterns.


# Specific test for the transaction time extraction
def test_transaction_time_extraction():
    # Test case 1: Standard format with Date & Time field
    body1 = "Date & Time: 21-04-25, 10:48:08 IST"
    details1 = extract_transaction_details(body1)
    assert details1["transaction_time"] == "10:48:08"

    # Test case 2: 'on' pattern
    body2 = "Transaction on 01-01-2023 13:45:30 IST"
    details2 = extract_transaction_details(body2)
    assert details2["transaction_time"] == "13:45:30"

    # Test case 3: Missing time
    body3 = "Date: 15-01-2023"
    details3 = extract_transaction_details(body3)
    assert details3["transaction_time"] == "Unknown"
