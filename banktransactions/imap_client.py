#!/usr/bin/env python3

import logging
import email
from imapclient import IMAPClient
from datetime import datetime, timedelta

# Import from our other modules
from email_parser import decode_str, extract_transaction_details_pure_llm
from api_client import send_transaction_to_api

from transaction_data import construct_transaction_data


def get_bank_emails(
    username, password, bank_email_list=None, processed_gmail_msgids=None
):
    """
    Retrieve bank transaction emails from Gmail and send to API

    Parameters:
    - username: Gmail username
    - password: Gmail password or app password
    - bank_email_list: List of bank email addresses to filter by
    - processed_gmail_msgids: Set of already processed Gmail Message IDs
    """
    if bank_email_list is None:
        bank_email_list = ["alerts@axisbank.com"]  # Default example
    if processed_gmail_msgids is None:
        processed_gmail_msgids = set()

    newly_processed_count = 0
    two_months_ago = datetime.now() - timedelta(days=60)
    since_date_str = two_months_ago.strftime("%d-%b-%Y")

    try:
        with IMAPClient("imap.gmail.com", ssl=True) as server:
            # Anonymize the email address in logs
            masked_username = (
                username.split("@")[0][:3] + "***@" + username.split("@")[1]
            )
            logging.info(f"Connecting to Gmail for {masked_username}...")
            server.login(username, password)
            server.select_folder("INBOX")

            for bank_email in bank_email_list:
                logging.info(
                    f"\nSearching for emails from {bank_email} since {since_date_str}..."
                )
                search_criteria = ["FROM", bank_email, "SINCE", since_date_str]

                try:
                    messages = server.search(search_criteria)
                    logging.info(
                        f"Found {len(messages)} potentially matching messages from {bank_email} in the last ~2 months"
                    )
                except Exception as search_err:
                    logging.error(
                        f"Error searching messages for {bank_email}: {search_err}"
                    )
                    continue

                if not messages:
                    continue

                fetch_items = [
                    "X-GM-MSGID",
                    "BODY.PEEK[]",
                    "ENVELOPE",
                ]

                try:
                    fetched_data = server.fetch(messages, fetch_items)
                except Exception as fetch_err:
                    logging.error(
                        f"Error fetching message details for {bank_email}: {fetch_err}"
                    )
                    continue

                logging.info(f"Processing {len(fetched_data)} fetched messages...")

                for msg_id, msg_data in fetched_data.items():
                    try:
                        if b"X-GM-MSGID" not in msg_data:
                            logging.warning(
                                f"X-GM-MSGID not found for message ID {msg_id}. Skipping."
                            )
                            continue

                        gmail_msgid = str(msg_data[b"X-GM-MSGID"])

                        if gmail_msgid in processed_gmail_msgids:
                            logging.debug(
                                f"Skipping already processed email Gmail Message ID: {gmail_msgid}"
                            )
                            continue

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
                            continue

                        try:
                            email_message = email.message_from_bytes(raw_email)
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
                        except Exception as envelope_err:
                            logging.warning(
                                f"Error decoding envelope subject/date for {gmail_msgid}: {envelope_err}. Skipping."
                            )
                            continue

                        body = ""
                        html_body = ""

                        if email_message.is_multipart():
                            logging.debug(
                                f"--- Debugging Parts for Gmail Message ID: {gmail_msgid} ---"
                            )
                            for i, part in enumerate(email_message.walk()):
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
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body = payload.decode(
                                                part.get_content_charset() or "utf-8",
                                                errors="replace",
                                            )
                                    except Exception as decode_err:
                                        logging.warning(
                                            f"Could not decode text/plain part for Gmail Message ID {gmail_msgid}: {decode_err}"
                                        )

                                elif ctype == "text/html" and not html_body:
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            html_body = payload.decode(
                                                part.get_content_charset() or "utf-8",
                                                errors="replace",
                                            )
                                    except Exception as decode_err:
                                        logging.warning(
                                            f"Could not decode text/html part for Gmail Message ID {gmail_msgid}: {decode_err}"
                                        )

                        else:
                            try:
                                payload = email_message.get_payload(decode=True)
                                if payload:
                                    charset = (
                                        email_message.get_content_charset() or "utf-8"
                                    )
                                    body = payload.decode(charset, errors="replace")
                                    if (
                                        "<html" in body.lower()
                                        or "<body" in body.lower()
                                    ):
                                        html_body = body
                                        if "<plaintext>" not in body.lower():
                                            body = ""
                            except Exception as decode_err:
                                logging.warning(
                                    f"Could not decode non-multipart body for Gmail Message ID {gmail_msgid}: {decode_err}"
                                )

                        if not body.strip() and html_body:
                            logging.debug(
                                f"Using text/html body for Gmail Message ID {gmail_msgid} as text/plain was empty."
                            )
                            body = html_body

                        if not body:
                            logging.warning(
                                f"Could not extract text/plain or text/html body for Gmail Message ID {gmail_msgid}. Skipping."
                            )
                            continue

                        details = extract_transaction_details_pure_llm(body)

                        transaction = construct_transaction_data(details)

                        api_success = send_transaction_to_api(transaction)

                        if api_success:
                            processed_gmail_msgids.add(gmail_msgid)
                            newly_processed_count += 1
                            logging.info(
                                f"Successfully processed and sent transaction for Gmail Message ID: {gmail_msgid}"
                            )
                        else:
                            logging.warning(
                                f"Failed to send transaction for Gmail Message ID {gmail_msgid} to API. Will retry on next run. Details: {details}"
                            )
                        print("-" * 50)

                    except Exception as processing_err:
                        logging.error(
                            f"Error processing message ID {msg_id} (Gmail Message ID {msg_data.get(b'X-GM-MSGID', 'N/A')}): {processing_err}",
                            exc_info=True,
                        )
                        continue

            return processed_gmail_msgids, newly_processed_count

    except IMAPClient.LoginError as e:
        logging.critical(
            f"IMAP Login Failed for {username}: {e}. Check credentials and App Password setup."
        )
        return processed_gmail_msgids, newly_processed_count
    except Exception as e:
        logging.critical(
            f"Error connecting to mail server or during processing: {e}", exc_info=True
        )
        return processed_gmail_msgids, newly_processed_count
