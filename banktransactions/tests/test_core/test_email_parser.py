#!/usr/bin/env python3

import sys
import os

# Add parent directory to Python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from banktransactions.core.email_parser import extract_transaction_details
except ImportError:
    # Fallback to relative import if running from within the directory
    from email_parser import extract_transaction_details

# Test case for the problematic email format
test_message = """
We wish to inform you that your A/c no. XX1648 has been debited with INR 2500.00 on 08-05-25 22:05:42 IST by IMPS/P2A/512822864712/PERSON1.
"""

# Extract the details
details = extract_transaction_details(test_message)

# Print the results
print("Extracted Details:")
for key, value in details.items():
    print(f"{key}: {value}")

# Verify the expected values
expected = {"account_number": "XX1648", "recipient": "PERSON1"}

for key, expected_value in expected.items():
    actual_value = details[key]
    print(f"\nExpected {key}: {expected_value}")
    print(f"Actual {key}:   {actual_value}")
    if actual_value == expected_value:
        print("✓ MATCH")
    else:
        print("✗ MISMATCH")
