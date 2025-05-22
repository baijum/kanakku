#!/usr/bin/env python3
"""
Example script demonstrating the use of the Gemini-powered transaction parser
"""

import os
import sys
from email_parser import extract_transaction_details_pure_llm


def compare_approaches(email_path):
    """
    Process email using the pure LLM approach

    Args:
        email_path (str): Path to email file (.eml)
    """
    # Check for API key
    if "GEMINI_API_KEY" not in os.environ:
        print("Warning: GEMINI_API_KEY not set. LLM approach will not work.")
        print("Set your API key with: export GEMINI_API_KEY='your-api-key-here'")
        print("")

    # Read email content
    with open(email_path, "r", encoding="utf-8") as f:
        email_content = f.read()

    # Parse email to get body
    import email

    msg = email.message_from_string(email_content)

    # Get email body
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode(errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="replace")

    # Process with pure LLM approach
    print("=" * 50)
    print("LLM APPROACH")
    print("=" * 50)
    llm_results = extract_transaction_details_pure_llm(body)
    for field, value in llm_results.items():
        print(f"{field.ljust(20)}: {value}")

    # Check for any "Unknown" values
    missing_fields = [
        field for field, value in llm_results.items() if value == "Unknown"
    ]
    if missing_fields:
        print("\nMissing fields:", ", ".join(missing_fields))
    else:
        print("\n✓ Successfully extracted all fields!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email_path = sys.argv[1]
        if not os.path.exists(email_path):
            print(f"Error: File not found: {email_path}")
            sys.exit(1)
    else:
        # Use the sample email if no file is provided
        email_path = "sample_email.eml"
        if not os.path.exists(email_path):
            print(f"Error: Sample email file not found: {email_path}")
            print(
                "Please run the script from the project root or provide a path to an email file."
            )
            sys.exit(1)

    print(f"Processing email from: {email_path}")
    compare_approaches(email_path)
