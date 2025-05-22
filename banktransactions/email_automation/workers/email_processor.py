import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from rq import get_current_job
from sqlalchemy.orm import Session

from email_automation.models.email_config import EmailConfiguration
from imap_client import IMAPClient
from email_parser import (
    extract_transaction_details_pure_llm,
    detect_currency,
    convert_currency,
)
from api_client import APIClient

logger = logging.getLogger(__name__)


class EmailProcessor:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.imap_client = None
        self.api_client = None

    def process_user_emails(self, user_id: int) -> Dict:
        """
        Main method to process emails for a user.
        This will be called by the RQ worker.
        """
        try:
            # Get the current job
            job = get_current_job()
            if not job:
                raise Exception("No job context found")

            # Get user's email configuration
            config = (
                self.db.query(EmailConfiguration).filter_by(user_id=user_id).first()
            )
            if not config or not config.is_enabled:
                return {
                    "status": "skipped",
                    "reason": "configuration_not_found_or_disabled",
                }

            # Initialize clients
            self.imap_client = IMAPClient(
                server=config.imap_server,
                port=config.imap_port,
                username=config.email_address,
                password=config.app_password,
            )
            self.api_client = APIClient()

            # Connect to email server
            self.imap_client.connect()

            # Get unread emails since last check
            last_check = config.last_check_time or datetime.min
            emails = self.imap_client.get_unread_emails(since=last_check)

            processed_count = 0
            errors = []

            for email in emails:
                try:
                    # Extract transaction details using the improved LLM-based parser
                    transaction_data = self._extract_transaction_data(email)

                    if transaction_data and transaction_data.get("amount") != "Unknown":
                        # Create transaction via API
                        response = self.api_client.create_transaction(
                            user_id=user_id, transaction_data=transaction_data
                        )

                        if response.get("success"):
                            processed_count += 1
                            # Mark email as processed
                            self.imap_client.mark_as_processed(email["id"])
                            logger.info(
                                f"Successfully processed email {email['id']} for user {user_id}"
                            )
                        else:
                            error_msg = f"Failed to create transaction for email {email['id']}: {response.get('error', 'Unknown error')}"
                            logger.error(error_msg)
                            errors.append(error_msg)
                    else:
                        logger.info(
                            f"Skipping email {email['id']} - no valid transaction data found"
                        )

                except Exception as e:
                    logger.error(f"Error processing email {email['id']}: {str(e)}")
                    errors.append(f"Error processing email {email['id']}: {str(e)}")

            # Update last check time
            config.last_check_time = datetime.utcnow()
            self.db.commit()

            return {
                "status": "success",
                "processed_count": processed_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Error in process_user_emails: {str(e)}")
            return {"status": "error", "error": str(e)}
        finally:
            if self.imap_client:
                self.imap_client.disconnect()

    def _extract_transaction_data(self, email: Dict) -> Optional[Dict]:
        """Extract transaction data from email using the improved LLM-based parser."""
        try:
            # Clean the email body
            body = email["body"]

            # Use the improved LLM-based parser
            transaction_data = extract_transaction_details_pure_llm(body)

            # Add additional metadata
            transaction_data.update(
                {
                    "email_id": email["id"],
                    "email_date": (
                        email["date"].isoformat() if email.get("date") else None
                    ),
                    "email_subject": email.get("subject", ""),
                    "email_from": email.get("from", ""),
                }
            )

            return transaction_data

        except Exception as e:
            logger.error(f"Error in _extract_transaction_data: {str(e)}")
            return None
