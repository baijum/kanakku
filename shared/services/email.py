"""
Unified email processing service.

Consolidates email automation logic from both backend and banktransactions
modules into a single, reusable service.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from .base import (
    BaseService,
    StatelessService,
    ServiceResult,
    require_user_context,
    log_service_call,
)


class EmailProcessingService(BaseService):
    """Unified service for email processing and automation."""

    @require_user_context
    @log_service_call("process_user_emails")
    def process_user_emails(self) -> ServiceResult:
        """
        Process emails for the current user.
        Consolidates logic from banktransactions/automation/email_processor.py
        """
        try:
            # Get user's email configuration
            config = self._get_user_email_config()
            if not config or not config.is_enabled:
                return ServiceResult.error_result(
                    "Email configuration not found or disabled",
                    error_code="CONFIG_DISABLED",
                )

            # Decrypt credentials
            credentials = self._decrypt_email_credentials(config)
            if not credentials:
                return ServiceResult.error_result(
                    "Failed to decrypt email credentials", error_code="DECRYPT_FAILED"
                )

            # Load processed message IDs
            processed_msgids = self._load_processed_message_ids()

            # Get bank emails from configuration
            bank_emails = self._extract_bank_emails(config)

            # Process emails
            result = self._process_emails_with_imap(
                credentials, bank_emails, processed_msgids
            )

            # Update last check time
            self._update_last_check_time(config)

            return ServiceResult.success_result(
                data=result,
                metadata={
                    "processed_count": result.get("processed_count", 0),
                    "bank_emails": bank_emails,
                },
            )

        except Exception as e:
            self.logger.error(f"Email processing failed: {e}")
            return ServiceResult.error_result(
                f"Email processing failed: {str(e)}", error_code="PROCESSING_FAILED"
            )

    @require_user_context
    def get_email_configuration(self) -> ServiceResult:
        """Get user's email automation configuration."""
        try:
            from shared.imports import EmailConfiguration

            config = (
                self.session.query(EmailConfiguration)
                .filter_by(user_id=self.user_id)
                .first()
            )

            if not config:
                return ServiceResult.success_result(data=None)

            # Return config without sensitive data
            config_dict = config.to_dict()
            config_dict.pop("app_password", None)

            return ServiceResult.success_result(data=config_dict)

        except Exception as e:
            self.logger.error(f"Failed to get email configuration: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve email configuration",
                error_code="CONFIG_RETRIEVAL_FAILED",
            )

    @require_user_context
    def update_email_configuration(self, config_data: Dict) -> ServiceResult:
        """Update user's email automation configuration."""
        try:
            # Validate configuration data
            validation_result = self._validate_email_config(config_data)
            if not validation_result.success:
                return validation_result

            # Update or create configuration
            with self.transaction_scope():
                config = self._update_or_create_config(config_data)

                return ServiceResult.success_result(
                    data=config.to_dict(),
                    metadata={"operation": "updated" if config.id else "created"},
                )

        except Exception as e:
            self.logger.error(f"Failed to update email configuration: {e}")
            return ServiceResult.error_result(
                "Failed to update email configuration",
                error_code="CONFIG_UPDATE_FAILED",
            )

    @require_user_context
    def test_email_connection(self, credentials: Dict) -> ServiceResult:
        """Test email connection with provided credentials."""
        try:
            from shared.imports import CustomIMAPClient

            imap_client = CustomIMAPClient(
                server=credentials.get("imap_server", "imap.gmail.com"),
                port=credentials.get("imap_port", 993),
                username=credentials["email_address"],
                password=credentials["app_password"],
            )

            # Test connection
            imap_client.connect()
            imap_client.disconnect()

            return ServiceResult.success_result(
                data={"connection_test": "successful"},
                metadata={"server": credentials.get("imap_server", "imap.gmail.com")},
            )

        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return ServiceResult.error_result(
                f"Connection test failed: {str(e)}", error_code="CONNECTION_TEST_FAILED"
            )

    # Private helper methods
    def _get_user_email_config(self):
        """Get user's email configuration from database."""
        from shared.imports import EmailConfiguration

        return (
            self.session.query(EmailConfiguration)
            .filter_by(user_id=self.user_id)
            .first()
        )

    def _decrypt_email_credentials(self, config) -> Optional[Dict]:
        """Decrypt email credentials from configuration."""
        try:
            from shared.imports import decrypt_value_standalone

            decrypted_password = decrypt_value_standalone(config.app_password)
            if not decrypted_password:
                return None

            return {
                "email_address": config.email_address,
                "app_password": decrypted_password,
                "imap_server": config.imap_server,
                "imap_port": config.imap_port,
            }
        except Exception as e:
            self.logger.error(f"Failed to decrypt credentials: {e}")
            return None

    def _load_processed_message_ids(self) -> Set[str]:
        """Load processed Gmail message IDs for user."""
        try:
            from shared.imports import load_processed_gmail_msgids

            return load_processed_gmail_msgids(user_id=self.user_id)
        except Exception as e:
            self.logger.error(f"Failed to load processed message IDs: {e}")
            return set()

    def _extract_bank_emails(self, config) -> List[str]:
        """Extract bank email addresses from configuration."""
        bank_emails = ["alerts@axisbank.com"]  # Default

        if config.sample_emails:
            try:
                sample_emails = json.loads(config.sample_emails)
                bank_emails_from_samples = []
                for sample in sample_emails:
                    if isinstance(sample, dict) and "from" in sample:
                        bank_emails_from_samples.append(sample["from"])
                if bank_emails_from_samples:
                    bank_emails = list(set(bank_emails_from_samples))
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Failed to parse sample emails for user {self.user_id}"
                )

        return bank_emails

    def _process_emails_with_imap(
        self, credentials: Dict, bank_emails: List[str], processed_msgids: Set[str]
    ) -> Dict:
        """Process emails using IMAP client."""
        try:
            from shared.imports import get_bank_emails, save_processed_gmail_msgid

            # Create callback for saving message IDs
            def save_msgid_callback(gmail_message_id):
                return save_processed_gmail_msgid(
                    gmail_message_id, user_id=self.user_id
                )

            # Process emails
            updated_msgids, newly_processed_count = get_bank_emails(
                username=credentials["email_address"],
                password=credentials["app_password"],
                bank_email_list=bank_emails,
                processed_gmail_msgids=processed_msgids,
                save_msgid_callback=save_msgid_callback,
            )

            return {
                "processed_count": newly_processed_count,
                "total_processed": len(updated_msgids),
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"IMAP processing failed: {e}")
            raise

    def _update_last_check_time(self, config):
        """Update the last check time for email configuration."""
        try:
            config.last_check_time = datetime.now(timezone.utc)
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to update last check time: {e}")

    def _validate_email_config(self, config_data: Dict) -> ServiceResult:
        """Validate email configuration data."""
        required_fields = ["email_address", "app_password"]
        missing_fields = [
            field for field in required_fields if not config_data.get(field)
        ]

        if missing_fields:
            return ServiceResult.error_result(
                f"Missing required fields: {', '.join(missing_fields)}",
                error_code="VALIDATION_FAILED",
            )

        return ServiceResult.success_result()

    def _update_or_create_config(self, config_data: Dict):
        """Update existing or create new email configuration."""
        from shared.imports import EmailConfiguration, encrypt_value

        config = (
            self.session.query(EmailConfiguration)
            .filter_by(user_id=self.user_id)
            .first()
        )

        if config:
            # Update existing
            config.is_enabled = config_data.get("is_enabled", False)
            config.imap_server = config_data.get("imap_server", "imap.gmail.com")
            config.imap_port = config_data.get("imap_port", 993)
            config.email_address = config_data["email_address"]
            config.app_password = encrypt_value(config_data["app_password"])
            config.polling_interval = config_data.get("polling_interval", "hourly")
            config.sample_emails = json.dumps(config_data.get("sample_emails", []))
            config.updated_at = datetime.now(timezone.utc)
        else:
            # Create new
            config = EmailConfiguration(
                user_id=self.user_id,
                is_enabled=config_data.get("is_enabled", False),
                imap_server=config_data.get("imap_server", "imap.gmail.com"),
                imap_port=config_data.get("imap_port", 993),
                email_address=config_data["email_address"],
                app_password=encrypt_value(config_data["app_password"]),
                polling_interval=config_data.get("polling_interval", "hourly"),
                sample_emails=json.dumps(config_data.get("sample_emails", [])),
            )
            self.session.add(config)

        return config


class EmailParsingService(StatelessService):
    """Service for parsing email content and extracting transaction details."""

    @log_service_call("extract_transaction_details")
    def extract_transaction_details(self, email_body: str) -> ServiceResult:
        """
        Extract transaction details from email body.
        Consolidates logic from banktransactions/core/email_parser.py
        """
        try:
            from shared.imports import extract_transaction_details

            details = extract_transaction_details(email_body)

            return ServiceResult.success_result(
                data=details, metadata={"extraction_method": "llm_with_fallback"}
            )

        except Exception as e:
            self.logger.error(f"Transaction extraction failed: {e}")
            return ServiceResult.error_result(
                f"Failed to extract transaction details: {str(e)}",
                error_code="EXTRACTION_FAILED",
            )
