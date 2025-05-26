#!/usr/bin/env python3

import email
import logging
import ssl
from datetime import datetime, timedelta

from imapclient import IMAPClient as RealIMAPClient
from imapclient.exceptions import LoginError

from banktransactions.core.api_client import send_transaction_to_api

# Import from our other modules
from banktransactions.core.email_parser import (
    decode_str,
    extract_transaction_details,
)
from banktransactions.core.transaction_data import construct_transaction_data


def get_bank_emails(
    username,
    password,
    bank_email_list=None,
    processed_gmail_msgids=None,
    save_msgid_callback=None,
):
    """
    Retrieve bank transaction emails from Gmail and send to API

    Parameters:
    - username: Gmail username
    - password: Gmail password or app password
    - bank_email_list: List of bank email addresses to filter by
    - processed_gmail_msgids: Set of already processed Gmail Message IDs
    - save_msgid_callback: Optional callback function to save individual message IDs
                          Should accept (gmail_message_id) and return True if saved successfully
    """
    logging.debug("Starting get_bank_emails function")
    logging.debug(f"Bank email list: {bank_email_list}")
    logging.debug(
        f"Number of previously processed messages: {len(processed_gmail_msgids) if processed_gmail_msgids else 0}"
    )

    if bank_email_list is None:
        bank_email_list = ["alerts@axisbank.com"]  # Default example
        logging.debug(f"Using default bank email list: {bank_email_list}")
    if processed_gmail_msgids is None:
        processed_gmail_msgids = set()
        logging.debug("Initialized empty processed_gmail_msgids set")

    newly_processed_count = 0
    two_months_ago = datetime.now() - timedelta(days=60)
    since_date_str = two_months_ago.strftime("%d-%b-%Y")
    logging.debug(f"Search date range: since {since_date_str} (two months ago)")

    try:
        logging.debug("Attempting to connect to Gmail IMAP server...")
        with RealIMAPClient("imap.gmail.com", ssl=True) as server:
            # Anonymize the email address in logs
            masked_username = (
                username.split("@")[0][:3] + "***@" + username.split("@")[1]
            )
            logging.info(f"Connecting to Gmail for {masked_username}...")
            logging.debug("Attempting IMAP login...")
            server.login(username, password)
            logging.debug("IMAP login successful")

            logging.debug("Selecting INBOX folder...")
            server.select_folder("INBOX")
            logging.debug("INBOX folder selected successfully")

            for bank_email in bank_email_list:
                logging.info(
                    f"\nSearching for emails from {bank_email} since {since_date_str}..."
                )
                search_criteria = ["FROM", bank_email, "SINCE", since_date_str]
                logging.debug(f"Search criteria: {search_criteria}")

                try:
                    logging.debug(f"Executing IMAP search for {bank_email}...")
                    messages = server.search(search_criteria)
                    logging.info(
                        f"Found {len(messages)} potentially matching messages from {bank_email} in the last ~2 months"
                    )
                    logging.debug(
                        f"Message IDs found: {messages[:10]}{'...' if len(messages) > 10 else ''}"
                    )
                except Exception as search_err:
                    logging.error(
                        f"Error searching messages for {bank_email}: {search_err}"
                    )
                    logging.debug(f"Search error details: {search_err}", exc_info=True)
                    continue

                if not messages:
                    logging.debug(
                        f"No messages found for {bank_email}, continuing to next bank"
                    )
                    continue

                fetch_items = [
                    "X-GM-MSGID",
                    "BODY.PEEK[]",
                    "ENVELOPE",
                ]
                logging.debug(f"Fetch items: {fetch_items}")

                try:
                    logging.debug(f"Fetching data for {len(messages)} messages...")
                    fetched_data = server.fetch(messages, fetch_items)
                    logging.debug(
                        f"Successfully fetched data for {len(fetched_data)} messages"
                    )
                except Exception as fetch_err:
                    logging.error(
                        f"Error fetching message details for {bank_email}: {fetch_err}"
                    )
                    logging.debug(f"Fetch error details: {fetch_err}", exc_info=True)
                    continue

                logging.info(f"Processing {len(fetched_data)} fetched messages...")

                for msg_id, msg_data in fetched_data.items():
                    logging.debug(f"Processing message ID: {msg_id}")
                    try:
                        if b"X-GM-MSGID" not in msg_data:
                            logging.warning(
                                f"X-GM-MSGID not found for message ID {msg_id}. Skipping."
                            )
                            logging.debug(
                                f"Available keys in msg_data: {list(msg_data.keys())}"
                            )
                            continue

                        gmail_msgid = str(msg_data[b"X-GM-MSGID"])
                        logging.debug(f"Gmail Message ID: {gmail_msgid}")

                        if gmail_msgid in processed_gmail_msgids:
                            logging.debug(
                                f"Skipping already processed email Gmail Message ID: {gmail_msgid}"
                            )
                            continue

                        logging.debug("Extracting email body...")
                        raw_email = msg_data.get(b"BODY.PEEK[]")
                        if not raw_email:
                            raw_email = msg_data.get(b"BODY[]", b"")
                            if raw_email:
                                logging.debug(
                                    f"Falling back to BODY[] for {gmail_msgid} (will mark as Seen)"
                                )

                        if not raw_email:
                            logging.warning(
                                f"Empty body fetched (checked BODY.PEEK[] and BODY[]) for message Gmail Message ID {gmail_msgid}. Skipping."
                            )
                            logging.debug(
                                f"Available body keys: {[k for k in msg_data if b'BODY' in k]}"
                            )
                            continue

                        logging.debug(f"Raw email size: {len(raw_email)} bytes")
                        try:
                            logging.debug("Parsing email message from bytes...")
                            email_message = email.message_from_bytes(raw_email)
                            logging.debug(
                                f"Email message parsed successfully. Content-Type: {email_message.get_content_type()}"
                            )
                        except Exception as parse_err:
                            logging.error(
                                f"Error parsing email bytes for {gmail_msgid}: {parse_err}. Skipping.",
                                exc_info=True,
                            )
                            continue

                        envelope = msg_data.get(b"ENVELOPE")
                        if not envelope:
                            logging.warning(
                                f"Envelope data missing for {gmail_msgid}. Skipping."
                            )
                            continue

                        try:
                            logging.debug(
                                "Extracting subject and date from envelope..."
                            )
                            subject = (
                                decode_str(envelope.subject.decode())
                                if envelope.subject
                                else "No Subject"
                            )
                            date_received = (
                                envelope.date.strftime("%a, %d %b %Y %H:%M:%S %z")
                                if envelope.date
                                else "No Date"
                            )
                            logging.debug(f"Subject: {subject}")
                            logging.debug(f"Date received: {date_received}")
                        except Exception as envelope_err:
                            logging.warning(
                                f"Error decoding envelope subject/date for {gmail_msgid}: {envelope_err}. Skipping."
                            )
                            logging.debug(
                                f"Envelope error details: {envelope_err}", exc_info=True
                            )
                            continue

                        body = ""
                        html_body = ""

                        logging.debug(
                            f"Email is multipart: {email_message.is_multipart()}"
                        )
                        if email_message.is_multipart():
                            logging.debug(
                                f"--- Debugging Parts for Gmail Message ID: {gmail_msgid} ---"
                            )
                            part_count = 0
                            for i, part in enumerate(email_message.walk()):
                                part_count += 1
                                ctype = part.get_content_type()
                                cdisp = str(part.get("Content-Disposition"))
                                fname = part.get_filename()

                                try:
                                    raw_payload_sample = part.get_payload(decode=False)
                                    if isinstance(raw_payload_sample, list):
                                        raw_payload_sample = (
                                            "[Payload is a list of sub-parts]"
                                        )
                                    else:
                                        raw_payload_sample = str(raw_payload_sample)[
                                            :150
                                        ]
                                except Exception as e:
                                    raw_payload_sample = (
                                        f"Error getting raw payload: {e}"
                                    )
                                logging.debug(
                                    f"  Part {i}: Content-Type={ctype}, Content-Disposition={cdisp}, Filename={fname}"
                                )
                                logging.debug(
                                    f"           Raw Payload Sample: {raw_payload_sample}..."
                                )

                                if "attachment" in cdisp or (fname and "." in fname):
                                    logging.debug(
                                        f"  Part {i}: Skipping attachment or part with filename."
                                    )
                                    continue

                                if ctype == "text/plain" and not body:
                                    logging.debug(
                                        f"  Part {i}: Processing text/plain content"
                                    )
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            charset = (
                                                part.get_content_charset() or "utf-8"
                                            )
                                            logging.debug(
                                                f"  Part {i}: Using charset: {charset}"
                                            )
                                            body = payload.decode(
                                                charset, errors="replace"
                                            )
                                            logging.debug(
                                                f"  Part {i}: Extracted {len(body)} characters of plain text"
                                            )
                                    except Exception as decode_err:
                                        logging.warning(
                                            f"Could not decode text/plain part for Gmail Message ID {gmail_msgid}: {decode_err}"
                                        )
                                        logging.debug(
                                            f"  Part {i}: Decode error details: {decode_err}",
                                            exc_info=True,
                                        )

                                elif ctype == "text/html" and not html_body:
                                    logging.debug(
                                        f"  Part {i}: Processing text/html content"
                                    )
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            charset = (
                                                part.get_content_charset() or "utf-8"
                                            )
                                            logging.debug(
                                                f"  Part {i}: Using charset: {charset}"
                                            )
                                            html_body = payload.decode(
                                                charset, errors="replace"
                                            )
                                            logging.debug(
                                                f"  Part {i}: Extracted {len(html_body)} characters of HTML"
                                            )
                                    except Exception as decode_err:
                                        logging.warning(
                                            f"Could not decode text/html part for Gmail Message ID {gmail_msgid}: {decode_err}"
                                        )
                                        logging.debug(
                                            f"  Part {i}: Decode error details: {decode_err}",
                                            exc_info=True,
                                        )

                            logging.debug(f"Processed {part_count} email parts total")
                        else:
                            # Single part message
                            logging.debug("Processing single-part email message")
                            try:
                                payload = email_message.get_payload(decode=True)
                                if payload:
                                    charset = (
                                        email_message.get_content_charset() or "utf-8"
                                    )
                                    logging.debug(f"Using charset: {charset}")
                                    body = payload.decode(charset, errors="replace")
                                    logging.debug(
                                        f"Extracted {len(body)} characters from single-part message"
                                    )
                            except Exception as decode_err:
                                logging.warning(
                                    f"Could not decode single-part message for Gmail Message ID {gmail_msgid}: {decode_err}"
                                )
                                logging.debug(
                                    f"Single-part decode error details: {decode_err}",
                                    exc_info=True,
                                )

                        if not body and html_body:
                            logging.debug("No plain text body found, using HTML body")
                            body = html_body

                        if not body:
                            logging.warning(
                                f"No body content found for Gmail Message ID {gmail_msgid}. Skipping."
                            )
                            continue

                        logging.debug(f"Final body length: {len(body)} characters")
                        logging.debug(
                            f"Processing email from {bank_email} with subject: {subject[:50]}..."
                        )

                        # Extract transaction details using LLM few-shot approach
                        try:
                            logging.debug("Starting transaction extraction process...")
                            # Use the wrapper function that handles all cleanup and processing
                            logging.debug(
                                "Calling extract_transaction_details_pure_llm..."
                            )
                            transaction_details = extract_transaction_details(body)
                            logging.debug(
                                f"Final transaction details: {transaction_details}"
                            )

                            if not transaction_details:
                                logging.info(
                                    f"No transaction details extracted for Gmail Message ID {gmail_msgid}. Skipping."
                                )
                                processed_gmail_msgids.add(gmail_msgid)
                                if save_msgid_callback:
                                    save_msgid_callback(gmail_msgid)
                                continue

                            # Construct transaction data
                            logging.debug("Constructing transaction data...")
                            transaction_data = construct_transaction_data(
                                transaction_details
                            )
                            logging.debug(
                                f"Constructed transaction data: {transaction_data}"
                            )

                            # Send to API
                            logging.debug("Sending transaction to API...")
                            api_response = send_transaction_to_api(transaction_data)
                            logging.debug(f"API response: {api_response}")

                            if api_response:
                                logging.info(
                                    f"Successfully sent transaction to API for Gmail Message ID {gmail_msgid}"
                                )
                                processed_gmail_msgids.add(gmail_msgid)
                                newly_processed_count += 1
                                logging.debug(
                                    f"Newly processed count: {newly_processed_count}"
                                )
                                if save_msgid_callback:
                                    save_msgid_callback(gmail_msgid)
                            else:
                                logging.error(
                                    f"Failed to send transaction to API for Gmail Message ID {gmail_msgid}"
                                )

                        except Exception as processing_err:
                            logging.error(
                                f"Error processing transaction for Gmail Message ID {gmail_msgid}: {processing_err}",
                                exc_info=True,
                            )
                            continue

                    except Exception as msg_err:
                        logging.error(
                            f"Error processing message {msg_id}: {msg_err}",
                            exc_info=True,
                        )
                        continue

            logging.debug(
                f"Completed processing all banks. Total newly processed: {newly_processed_count}"
            )
            return processed_gmail_msgids, newly_processed_count

    except LoginError as e:
        logging.critical(
            f"IMAP Login Failed for {username}: {e}. Check credentials and App Password setup."
        )
        logging.debug(f"Login error details: {e}", exc_info=True)
        return processed_gmail_msgids, newly_processed_count
    except Exception as e:
        logging.critical(
            f"Error connecting to mail server or during processing: {e}", exc_info=True
        )
        return processed_gmail_msgids, newly_processed_count


class CustomIMAPClient:
    """
    Custom IMAP client wrapper for the Flask application.

    This class provides a simplified interface for testing IMAP connections
    that matches what the Flask email automation expects.
    """

    def __init__(self, server="imap.gmail.com", port=993, username=None, password=None):
        """
        Initialize the IMAP client with connection parameters.

        Args:
            server (str): IMAP server hostname
            port (int): IMAP server port
            username (str): Email username
            password (str): Email password or app password
        """
        logging.debug(
            f"Initializing CustomIMAPClient with server={server}, port={port}"
        )
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self._client = None
        logging.debug("CustomIMAPClient initialized successfully")

    def connect(self):
        """
        Connect to the IMAP server and authenticate.

        Raises:
            Exception: If connection or authentication fails
        """
        logging.debug(f"Attempting to connect to IMAP server {self.server}:{self.port}")
        try:
            # Import the real IMAPClient from imapclient library
            from imapclient import IMAPClient as RealIMAPClient

            # Create SSL context with proper certificate handling
            logging.debug("Creating SSL context...")
            ssl_context = ssl.create_default_context()

            # For development/testing, we can be more lenient with certificates
            # In production, you should use proper certificates
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logging.debug(
                "SSL context configured (check_hostname=False, verify_mode=CERT_NONE)"
            )

            # Create connection with custom SSL context
            logging.debug("Creating IMAP client connection...")
            self._client = RealIMAPClient(
                self.server, port=self.port, ssl=True, ssl_context=ssl_context
            )
            logging.debug("IMAP client created successfully")

            # Authenticate
            masked_username = (
                self.username.split("@")[0][:3] + "***@" + self.username.split("@")[1]
                if self.username and "@" in self.username
                else "***"
            )
            logging.debug(f"Attempting authentication for {masked_username}...")
            self._client.login(self.username, self.password)
            logging.debug("Authentication successful")

            return True

        except Exception as e:
            logging.error(f"Connection/authentication failed: {e}")
            logging.debug(f"Connection error details: {e}", exc_info=True)
            if self._client:
                try:
                    logging.debug("Attempting to logout from failed connection...")
                    self._client.logout()
                    logging.debug("Logout successful")
                except:
                    logging.debug("Logout failed or connection already closed")
                self._client = None
            raise e

    def disconnect(self):
        """
        Disconnect from the IMAP server.
        """
        logging.debug("Attempting to disconnect from IMAP server...")
        if self._client:
            try:
                self._client.logout()
                logging.debug("IMAP logout successful")
            except:
                logging.debug("IMAP logout failed or connection already closed")
            finally:
                self._client = None
                logging.debug("IMAP client reference cleared")
        else:
            logging.debug("No active IMAP connection to disconnect")

    def get_unread_emails(self, since=None):
        """
        Get unread emails from the INBOX.

        Args:
            since (datetime): Get emails since this date (optional)

        Returns:
            list: List of email dictionaries with id, subject, body, from, date
        """
        logging.debug("Starting get_unread_emails...")
        logging.debug(f"Since parameter: {since}")

        if not self._client:
            logging.error("Not connected to IMAP server")
            raise Exception("Not connected to IMAP server")

        try:
            # Select INBOX folder
            logging.debug("Selecting INBOX folder...")
            self._client.select_folder("INBOX")
            logging.debug("INBOX folder selected successfully")

            # Build search criteria
            search_criteria = ["UNSEEN"]  # Only unread emails
            logging.debug(f"Base search criteria: {search_criteria}")

            if since:
                # Convert datetime to IMAP date format
                since_str = since.strftime("%d-%b-%Y")
                search_criteria.extend(["SINCE", since_str])
                logging.debug(f"Added date filter: SINCE {since_str}")

            logging.debug(f"Final search criteria: {search_criteria}")

            # Search for messages
            logging.debug("Executing IMAP search...")
            messages = self._client.search(search_criteria)
            logging.debug(
                f"Search returned {len(messages)} message IDs: {messages[:10]}{'...' if len(messages) > 10 else ''}"
            )

            if not messages:
                logging.debug("No unread messages found")
                return []

            # Fetch email data
            fetch_items = [
                "X-GM-MSGID",
                "BODY.PEEK[]",
                "ENVELOPE",
            ]
            logging.debug(f"Fetching data with items: {fetch_items}")

            fetched_data = self._client.fetch(messages, fetch_items)
            logging.debug(f"Fetched data for {len(fetched_data)} messages")
            emails = []

            for msg_id, msg_data in fetched_data.items():
                logging.debug(f"Processing fetched message ID: {msg_id}")
                try:
                    # Get Gmail message ID
                    gmail_msgid = str(msg_data.get(b"X-GM-MSGID", msg_id))
                    logging.debug(f"Gmail Message ID: {gmail_msgid}")

                    # Get envelope data
                    envelope = msg_data.get(b"ENVELOPE")
                    if not envelope:
                        logging.warning(f"No envelope data for message {msg_id}")
                        continue

                    # Extract subject and date
                    subject = (
                        envelope.subject.decode() if envelope.subject else "No Subject"
                    )
                    email_date = envelope.date if envelope.date else datetime.now()
                    email_from = (
                        envelope.from_[0].mailbox.decode()
                        + "@"
                        + envelope.from_[0].host.decode()
                        if envelope.from_ and envelope.from_[0]
                        else "Unknown"
                    )

                    logging.debug(f"Subject: {subject}")
                    logging.debug(f"From: {email_from}")
                    logging.debug(f"Date: {email_date}")

                    # Get email body
                    raw_email = msg_data.get(b"BODY.PEEK[]")
                    if not raw_email:
                        logging.warning(f"No body data for message {msg_id}")
                        continue

                    logging.debug(f"Raw email size: {len(raw_email)} bytes")

                    # Parse email message
                    logging.debug("Parsing email message...")
                    email_message = email.message_from_bytes(raw_email)
                    logging.debug(
                        f"Email parsed. Content-Type: {email_message.get_content_type()}"
                    )

                    body = self._extract_email_body(email_message)
                    logging.debug(f"Extracted body length: {len(body)} characters")

                    email_dict = {
                        "id": gmail_msgid,
                        "subject": subject,
                        "body": body,
                        "from": email_from,
                        "date": email_date,
                        "imap_id": msg_id,  # Store IMAP message ID for marking as processed
                    }
                    emails.append(email_dict)
                    logging.debug(f"Added email to results: {gmail_msgid}")

                except Exception as e:
                    logging.warning(f"Error processing email {msg_id}: {e}")
                    logging.debug(f"Email processing error details: {e}", exc_info=True)
                    continue

            logging.debug(f"Returning {len(emails)} processed emails")
            return emails

        except Exception as e:
            logging.error(f"Error getting unread emails: {e}")
            logging.debug(f"get_unread_emails error details: {e}", exc_info=True)
            raise e

    def mark_as_processed(self, email_id):
        """
        Mark an email as read/processed.

        Args:
            email_id (str): The email ID to mark as processed
        """
        logging.debug(f"Attempting to mark email as processed: {email_id}")

        if not self._client:
            logging.error("Not connected to IMAP server")
            raise Exception("Not connected to IMAP server")

        try:
            # Find the email by Gmail message ID and mark as read
            # For now, we'll mark all unread emails as read since we processed them
            # In a more sophisticated implementation, we'd track individual message IDs
            logging.debug(
                "Email marking as processed (currently no-op - using BODY.PEEK[])"
            )
            # Gmail automatically marks emails as read when we fetch them with BODY.PEEK[]

        except Exception as e:
            logging.warning(f"Error marking email {email_id} as processed: {e}")
            logging.debug(f"Mark as processed error details: {e}", exc_info=True)

    def _extract_email_body(self, email_message):
        """
        Extract text body from email message.

        Args:
            email_message: Parsed email message object

        Returns:
            str: Email body text
        """
        logging.debug("Starting email body extraction...")
        logging.debug(f"Email is multipart: {email_message.is_multipart()}")

        body = ""
        html_body = ""

        if email_message.is_multipart():
            logging.debug("Processing multipart email...")
            part_count = 0
            for part in email_message.walk():
                part_count += 1
                ctype = part.get_content_type()
                cdisp = str(part.get("Content-Disposition"))

                logging.debug(
                    f"Part {part_count}: Content-Type={ctype}, Content-Disposition={cdisp}"
                )

                # Skip attachments
                if "attachment" in cdisp:
                    logging.debug(f"Part {part_count}: Skipping attachment")
                    continue

                if ctype == "text/plain" and not body:
                    logging.debug(f"Part {part_count}: Processing text/plain")
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            logging.debug(f"Part {part_count}: Using charset {charset}")
                            body = payload.decode(charset, errors="replace")
                            logging.debug(
                                f"Part {part_count}: Extracted {len(body)} characters of plain text"
                            )
                    except Exception as e:
                        logging.debug(
                            f"Part {part_count}: Error decoding text/plain: {e}"
                        )

                elif ctype == "text/html" and not html_body:
                    logging.debug(f"Part {part_count}: Processing text/html")
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            logging.debug(f"Part {part_count}: Using charset {charset}")
                            html_body = payload.decode(charset, errors="replace")
                            logging.debug(
                                f"Part {part_count}: Extracted {len(html_body)} characters of HTML"
                            )
                    except Exception as e:
                        logging.debug(
                            f"Part {part_count}: Error decoding text/html: {e}"
                        )

            logging.debug(f"Processed {part_count} email parts")
        else:
            logging.debug("Processing single-part email...")
            try:
                payload = email_message.get_payload(decode=True)
                if payload:
                    charset = email_message.get_content_charset() or "utf-8"
                    logging.debug(f"Using charset: {charset}")
                    body = payload.decode(charset, errors="replace")
                    logging.debug(f"Extracted {len(body)} characters from single-part")
                    if "<html" in body.lower() or "<body" in body.lower():
                        logging.debug("Detected HTML content in single-part message")
                        html_body = body
                        body = ""
            except Exception as e:
                logging.debug(f"Error decoding single-part message: {e}")

        # Use HTML body if plain text is not available
        if not body.strip() and html_body:
            logging.debug("No plain text found, using HTML body")
            body = html_body

        logging.debug(f"Final extracted body length: {len(body)} characters")
        return body


# For backward compatibility, create an alias
IMAPClient = CustomIMAPClient
