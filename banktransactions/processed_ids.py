#!/usr/bin/env python3

import logging
import os

# File to store processed Gmail Message IDs
PROCESSED_GMAIL_MSGIDS_FILE = "processed_gmail_msgids.txt"


def load_processed_gmail_msgids(filepath=PROCESSED_GMAIL_MSGIDS_FILE):
    """Load processed Gmail Message IDs from a file."""
    try:
        with open(filepath, "r") as f:
            # X-GM-MSGID are large integers, store as strings for simplicity
            msgids = {line.strip() for line in f if line.strip().isdigit()}
            logging.info(
                f"Loaded {len(msgids)} processed Gmail Message IDs from {filepath}"
            )
            return msgids
    except FileNotFoundError:
        logging.info(
            f"Processed Gmail Message IDs file ({filepath}) not found. Starting fresh."
        )
        return set()
    except Exception as e:
        logging.error(f"Error loading processed Gmail Message IDs from {filepath}: {e}")
        return set()  # Start fresh on error


def save_processed_gmail_msgids(msgids, filepath=PROCESSED_GMAIL_MSGIDS_FILE):
    """Save processed Gmail Message IDs to a file."""
    try:
        # Store as strings
        with open(filepath, "w") as f:
            for msgid in sorted(list(msgids)):  # Sort for consistency
                f.write(f"{msgid}\n")  # Corrected: Use single backslash for newline
        logging.info(f"Saved {len(msgids)} processed Gmail Message IDs to {filepath}")
    except Exception as e:
        logging.error(f"Error saving processed Gmail Message IDs to {filepath}: {e}")
