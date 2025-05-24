#!/usr/bin/env python3

import pytest
import os
import sys
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, Mock, MagicMock, call
from sqlalchemy.orm import Session

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from banktransactions.email_automation.workers.email_processor import (
    EmailProcessor,
    process_user_emails_standalone
)


class TestEmailProcessor:
    """Test cases for the EmailProcessor class."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def email_processor(self, mock_db_session):
        """Create an EmailProcessor instance with mocked dependencies."""
        return EmailProcessor(mock_db_session)

    @pytest.fixture
    def mock_email_config(self):
        """Create a mock EmailConfiguration object."""
        config = Mock()
        config.user_id = 1
        config.is_enabled = True
        config.app_password = "encrypted_password"
        config.imap_server = "imap.gmail.com"
        config.imap_port = 993
        config.email_address = "test@example.com"
        config.last_check_time = datetime.now(timezone.utc) - timedelta(hours=1)
        config.sample_emails = json.dumps([{"subject": "Test", "body": "Sample email"}])
        config.polling_interval = "hourly"
        return config

    @pytest.fixture
    def mock_email_data(self):
        """Create mock email data."""
        return [
            {
                "id": "email_1",
                "subject": "Transaction Alert",
                "body": "Your account XX1648 has been debited with Rs. 500.00",
                "from": "bank@example.com",
                "date": datetime.now(timezone.utc)
            },
            {
                "id": "email_2", 
                "subject": "Payment Confirmation",
                "body": "Payment of Rs. 250.00 to RESTAURANT",
                "from": "payments@example.com",
                "date": datetime.now(timezone.utc)
            }
        ]

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    def test_process_user_emails_success(self, mock_api_client_class, mock_imap_client_class, 
                                       mock_decrypt, mock_get_job, email_processor, 
                                       mock_email_config, mock_email_data):
        """Test successful email processing."""
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock database query
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_email_config
        
        # Mock IMAP client
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = mock_email_data
        
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.create_transaction.return_value = {"success": True}
        
        # Mock transaction data extraction
        with patch.object(email_processor, '_extract_transaction_data') as mock_extract:
            mock_extract.side_effect = [
                {"amount": 500.0, "account": "XX1648", "recipient": "RESTAURANT"},
                {"amount": 250.0, "account": "XX1648", "recipient": "SHOP"}
            ]
            
            result = email_processor.process_user_emails(1)
        
        # Assertions
        assert result["status"] == "success"
        assert result["processed_count"] == 2
        assert result["errors"] == []
        
        # Verify IMAP client was used correctly
        mock_imap_client.connect.assert_called_once()
        mock_imap_client.get_unread_emails.assert_called_once()
        assert mock_imap_client.mark_as_processed.call_count == 2
        mock_imap_client.disconnect.assert_called_once()
        
        # Verify API client was used correctly
        assert mock_api_client.create_transaction.call_count == 2
        
        # Verify database was updated
        email_processor.db.commit.assert_called_once()

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    def test_process_user_emails_no_job_context(self, mock_get_job, email_processor):
        """Test handling when no job context is found."""
        mock_get_job.return_value = None
        
        result = email_processor.process_user_emails(1)
        
        assert result["status"] == "error"
        assert "No job context found" in result["error"]

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    def test_process_user_emails_config_not_found(self, mock_get_job, email_processor):
        """Test handling when email configuration is not found."""
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        
        # Mock database query to return None
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = None
        
        result = email_processor.process_user_emails(1)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "configuration_not_found_or_disabled"

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    def test_process_user_emails_config_disabled(self, mock_get_job, email_processor, mock_email_config):
        """Test handling when email configuration is disabled."""
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_email_config.is_enabled = False
        
        # Mock database query
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_email_config
        
        result = email_processor.process_user_emails(1)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "configuration_not_found_or_disabled"

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    def test_process_user_emails_decrypt_failure(self, mock_decrypt, mock_get_job, 
                                                email_processor, mock_email_config):
        """Test handling when password decryption fails."""
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = None
        
        # Mock database query
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_email_config
        
        result = email_processor.process_user_emails(1)
        
        assert result["status"] == "error"
        assert "Failed to decrypt app password" in result["error"]

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    def test_process_user_emails_api_failure(self, mock_api_client_class, mock_imap_client_class,
                                           mock_decrypt, mock_get_job, email_processor,
                                           mock_email_config, mock_email_data):
        """Test handling when API call fails."""
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock database query
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_email_config
        
        # Mock IMAP client
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = mock_email_data[:1]  # Only one email
        
        # Mock API client to fail
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.create_transaction.return_value = {"success": False, "error": "API Error"}
        
        # Mock transaction data extraction
        with patch.object(email_processor, '_extract_transaction_data') as mock_extract:
            mock_extract.return_value = {"amount": 500.0, "account": "XX1648"}
            
            result = email_processor.process_user_emails(1)
        
        # Assertions
        assert result["status"] == "success"
        assert result["processed_count"] == 0
        assert len(result["errors"]) == 1
        assert "Failed to create transaction" in result["errors"][0]

    @patch('banktransactions.email_automation.workers.email_processor.extract_transaction_details_pure_llm')
    def test_extract_transaction_data_success(self, mock_extract_llm, email_processor, mock_email_config):
        """Test successful transaction data extraction."""
        email = {
            "id": "email_1",
            "subject": "Transaction Alert",
            "body": "Your account has been debited with Rs. 500.00",
            "from": "bank@example.com",
            "date": datetime.now(timezone.utc)
        }
        
        mock_extract_llm.return_value = {
            "amount": 500.0,
            "account": "XX1648",
            "recipient": "RESTAURANT"
        }
        
        result = email_processor._extract_transaction_data(email, mock_email_config)
        
        assert result is not None
        assert result["amount"] == 500.0
        assert result["email_id"] == "email_1"
        assert result["email_subject"] == "Transaction Alert"
        assert result["email_from"] == "bank@example.com"
        assert "email_date" in result

    @patch('banktransactions.email_automation.workers.email_processor.extract_transaction_details_pure_llm')
    def test_extract_transaction_data_with_sample_emails(self, mock_extract_llm, email_processor, mock_email_config):
        """Test transaction data extraction with sample emails."""
        email = {
            "id": "email_1",
            "body": "Transaction alert",
            "subject": "Alert",
            "from": "bank@example.com",
            "date": datetime.now(timezone.utc)
        }
        
        mock_extract_llm.return_value = {"amount": 500.0}
        
        result = email_processor._extract_transaction_data(email, mock_email_config)
        
        # Verify sample emails were passed to LLM
        mock_extract_llm.assert_called_once()
        call_args = mock_extract_llm.call_args
        assert call_args[1]["sample_emails"] == [{"subject": "Test", "body": "Sample email"}]

    @patch('banktransactions.email_automation.workers.email_processor.extract_transaction_details_pure_llm')
    def test_extract_transaction_data_invalid_sample_emails(self, mock_extract_llm, email_processor, mock_email_config):
        """Test transaction data extraction with invalid sample emails JSON."""
        email = {
            "id": "email_1",
            "body": "Transaction alert",
            "subject": "Alert",
            "from": "bank@example.com",
            "date": datetime.now(timezone.utc)
        }
        
        mock_email_config.sample_emails = "invalid json"
        mock_extract_llm.return_value = {"amount": 500.0}
        
        result = email_processor._extract_transaction_data(email, mock_email_config)
        
        # Should still work with empty sample emails
        mock_extract_llm.assert_called_once()
        call_args = mock_extract_llm.call_args
        assert call_args[1]["sample_emails"] == []

    @patch('banktransactions.email_automation.workers.email_processor.extract_transaction_details_pure_llm')
    def test_extract_transaction_data_exception(self, mock_extract_llm, email_processor, mock_email_config):
        """Test handling of exceptions in transaction data extraction."""
        email = {
            "id": "email_1",
            "body": "Transaction alert",
            "subject": "Alert",
            "from": "bank@example.com",
            "date": datetime.now(timezone.utc)
        }
        
        mock_extract_llm.side_effect = Exception("LLM Error")
        
        result = email_processor._extract_transaction_data(email, mock_email_config)
        
        assert result is None


class TestProcessUserEmailsStandalone:
    """Test cases for the process_user_emails_standalone function."""

    @patch('banktransactions.email_automation.workers.email_processor.create_engine')
    @patch('banktransactions.email_automation.workers.email_processor.sessionmaker')
    @patch('banktransactions.email_automation.workers.email_processor.EmailProcessor')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_process_user_emails_standalone_success(self, mock_processor_class, mock_sessionmaker, mock_create_engine):
        """Test successful standalone email processing."""
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session_class = Mock()
        mock_sessionmaker.return_value = mock_session_class
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_user_emails.return_value = {
            "status": "success",
            "processed_count": 2,
            "errors": []
        }
        
        result = process_user_emails_standalone(1)
        
        assert result["status"] == "success"
        assert result["processed_count"] == 2
        
        # Verify database session was created and closed
        mock_create_engine.assert_called_once_with('postgresql://test:test@localhost/test')
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        mock_session.close.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_process_user_emails_standalone_no_db_url(self):
        """Test handling when DATABASE_URL is not set."""
        result = process_user_emails_standalone(1)
        
        assert result["status"] == "error"
        assert "DATABASE_URL environment variable not set" in result["error"]

    @patch('banktransactions.email_automation.workers.email_processor.create_engine')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_process_user_emails_standalone_db_error(self, mock_create_engine):
        """Test handling of database connection errors."""
        mock_create_engine.side_effect = Exception("Database connection failed")
        
        result = process_user_emails_standalone(1)
        
        assert result["status"] == "error"
        assert "Database connection failed" in result["error"]

    @patch('banktransactions.email_automation.workers.email_processor.create_engine')
    @patch('banktransactions.email_automation.workers.email_processor.sessionmaker')
    @patch('banktransactions.email_automation.workers.email_processor.EmailProcessor')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_process_user_emails_standalone_processor_error(self, mock_processor_class, mock_sessionmaker, mock_create_engine):
        """Test handling when EmailProcessor raises an exception."""
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session_class = Mock()
        mock_sessionmaker.return_value = mock_session_class
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_user_emails.side_effect = Exception("Processing error")
        
        result = process_user_emails_standalone(1)
        
        assert result["status"] == "error"
        assert "Processing error" in result["error"]
        
        # Verify session was still closed
        mock_session.close.assert_called_once()

    @patch('banktransactions.email_automation.workers.email_processor.create_engine')
    @patch('banktransactions.email_automation.workers.email_processor.sessionmaker')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_process_user_emails_standalone_session_creation_error(self, mock_sessionmaker, mock_create_engine):
        """Test handling when session creation fails."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_sessionmaker.side_effect = Exception("Session creation failed")
        
        result = process_user_emails_standalone(1)
        
        assert result["status"] == "error"
        assert "Session creation failed" in result["error"] 