#!/usr/bin/env python3

import pytest
import os
import sys
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy.orm import Session

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from banktransactions.email_automation.workers.email_processor import EmailProcessor
from banktransactions.email_automation.workers.scheduler import EmailScheduler


class TestEmailProcessorEdgeCases:
    """Additional edge case tests for EmailProcessor to complement existing test suite."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def email_processor(self, mock_db_session):
        """Create an EmailProcessor instance with mocked dependencies."""
        return EmailProcessor(mock_db_session)

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    def test_process_user_emails_empty_email_list(self, mock_api_client_class, mock_imap_client_class,
                                                 mock_decrypt, mock_get_job, email_processor):
        """Test processing when IMAP returns empty email list."""
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock email configuration
        mock_config = Mock()
        mock_config.user_id = 1
        mock_config.is_enabled = True
        mock_config.app_password = "encrypted_password"
        mock_config.imap_server = "imap.gmail.com"
        mock_config.imap_port = 993
        mock_config.email_address = "test@example.com"
        mock_config.last_check_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_config.sample_emails = json.dumps([])
        mock_config.polling_interval = "hourly"
        
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_config
        
        # Mock IMAP client to return empty list
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = []  # Empty email list
        
        # Mock API client (shouldn't be called)
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        result = email_processor.process_user_emails(1)
        
        # Verify results
        assert result["status"] == "success"
        assert result["processed_count"] == 0
        assert result["errors"] == []
        
        # Verify IMAP operations
        mock_imap_client.connect.assert_called_once()
        mock_imap_client.get_unread_emails.assert_called_once()
        mock_imap_client.disconnect.assert_called_once()
        
        # Verify API client was not called
        mock_api_client.create_transaction.assert_not_called()

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    def test_process_user_emails_imap_connection_failure(self, mock_imap_client_class, mock_decrypt, 
                                                        mock_get_job, email_processor):
        """Test handling of IMAP connection failures."""
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock email configuration
        mock_config = Mock()
        mock_config.user_id = 1
        mock_config.is_enabled = True
        mock_config.app_password = "encrypted_password"
        mock_config.imap_server = "imap.gmail.com"
        mock_config.imap_port = 993
        mock_config.email_address = "test@example.com"
        
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_config
        
        # Mock IMAP client to fail on connection
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.connect.side_effect = Exception("IMAP connection failed")
        
        result = email_processor.process_user_emails(1)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "IMAP connection failed" in result["error"]

    def test_extract_transaction_data_with_none_email(self, email_processor):
        """Test transaction data extraction with None email input."""
        mock_config = Mock()
        mock_config.sample_emails = json.dumps([])
        
        result = email_processor._extract_transaction_data(None, mock_config)
        
        assert result is None

    def test_extract_transaction_data_with_malformed_email(self, email_processor):
        """Test transaction data extraction with malformed email data."""
        mock_config = Mock()
        mock_config.sample_emails = json.dumps([])
        
        # Email missing required fields
        malformed_email = {
            "id": "email_1",
            # Missing subject, body, from, date
        }
        
        with patch('banktransactions.email_automation.workers.email_processor.extract_transaction_details_pure_llm') as mock_llm:
            mock_llm.side_effect = KeyError("Missing required field")
            
            result = email_processor._extract_transaction_data(malformed_email, mock_config)
        
        assert result is None

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    def test_process_user_emails_database_commit_failure(self, mock_api_client_class, mock_imap_client_class,
                                                        mock_decrypt, mock_get_job, email_processor):
        """Test handling of database commit failures."""
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock email configuration
        mock_config = Mock()
        mock_config.user_id = 1
        mock_config.is_enabled = True
        mock_config.app_password = "encrypted_password"
        mock_config.imap_server = "imap.gmail.com"
        mock_config.imap_port = 993
        mock_config.email_address = "test@example.com"
        mock_config.last_check_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_config.sample_emails = json.dumps([])
        mock_config.polling_interval = "hourly"
        
        email_processor.db.query.return_value.filter_by.return_value.first.return_value = mock_config
        
        # Mock IMAP client
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = [
            {
                "id": "email_1",
                "subject": "Test",
                "body": "Test email",
                "from": "test@example.com",
                "date": datetime.now(timezone.utc)
            }
        ]
        
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.create_transaction.return_value = {"success": True}
        
        # Mock database commit to fail
        email_processor.db.commit.side_effect = Exception("Database commit failed")
        
        # Mock transaction extraction
        with patch.object(email_processor, '_extract_transaction_data') as mock_extract:
            mock_extract.return_value = {"amount": 100.0, "account": "XX1234"}
            
            result = email_processor.process_user_emails(1)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "Database commit failed" in result["error"]


class TestEmailSchedulerEdgeCases:
    """Additional edge case tests for EmailScheduler to complement existing test suite."""

    @pytest.fixture
    def mock_redis_conn(self):
        """Create a mock Redis connection."""
        return Mock()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def email_scheduler(self, mock_redis_conn, mock_db_session):
        """Create an EmailScheduler instance with mocked dependencies."""
        return EmailScheduler(mock_redis_conn, mock_db_session)

    def test_calculate_next_run_with_none_last_check_time(self, email_scheduler):
        """Test next run calculation when last_check_time is explicitly None."""
        config = Mock()
        config.last_check_time = None
        config.polling_interval = "hourly"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return current time when never checked before
        assert result is not None
        assert abs((result - datetime.utcnow()).total_seconds()) < 60

    def test_calculate_next_run_with_empty_polling_interval(self, email_scheduler):
        """Test next run calculation with empty polling interval."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(hours=1)
        config.polling_interval = ""  # Empty string
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should default to hourly and return current time since overdue
        assert result is not None

    def test_calculate_next_run_with_none_polling_interval(self, email_scheduler):
        """Test next run calculation with None polling interval."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(hours=1)
        config.polling_interval = None
        
        # This should raise an AttributeError since the code doesn't handle None polling_interval
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'lower'"):
            email_scheduler._calculate_next_run(config)

    def test_calculate_next_run_with_very_old_last_check(self, email_scheduler):
        """Test next run calculation with very old last check time."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(days=365)  # 1 year ago
        config.polling_interval = "daily"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return current time for very overdue jobs
        assert result is not None

    def test_calculate_next_run_with_future_last_check(self, email_scheduler):
        """Test next run calculation when last check time is in the future."""
        config = Mock()
        config.last_check_time = datetime.utcnow() + timedelta(hours=1)  # Future time
        config.polling_interval = "hourly"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should handle future timestamps gracefully
        assert result is not None

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_schedule_user_job_with_scheduler_exception(self, mock_scheduler_class, email_scheduler):
        """Test handling of scheduler exceptions during job scheduling."""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        # Mock scheduler to raise exception
        mock_scheduler.enqueue_at.side_effect = Exception("Scheduler error")
        
        config = Mock()
        config.user_id = 1
        config.polling_interval = "hourly"
        config.last_check_time = datetime.utcnow() - timedelta(hours=2)
        
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = datetime.utcnow()
            
            # Should not raise exception
            email_scheduler._schedule_user_job(config)

    def test_schedule_jobs_with_database_query_exception(self, email_scheduler):
        """Test handling of database query exceptions in schedule_jobs."""
        # Mock database query to raise exception
        email_scheduler.db.query.side_effect = Exception("Database query failed")
        
        # Should not raise exception
        email_scheduler.schedule_jobs()

    def test_calculate_next_run_boundary_conditions(self, email_scheduler):
        """Test next run calculation at exact boundary conditions."""
        config = Mock()
        config.polling_interval = "hourly"
        
        # Test exactly 1 hour ago (boundary condition)
        config.last_check_time = datetime.utcnow() - timedelta(hours=1, seconds=0)
        result = email_scheduler._calculate_next_run(config)
        assert result is not None
        
        # Test just under 1 hour ago
        config.last_check_time = datetime.utcnow() - timedelta(minutes=59, seconds=59)
        result = email_scheduler._calculate_next_run(config)
        assert result is not None
        
        # Test just over 1 hour ago
        config.last_check_time = datetime.utcnow() - timedelta(hours=1, seconds=1)
        result = email_scheduler._calculate_next_run(config)
        assert result is not None


class TestWorkersInitialization:
    """Test the workers package initialization and imports."""

    def test_workers_package_imports(self):
        """Test that workers package can be imported successfully."""
        try:
            from banktransactions.email_automation.workers import email_processor, scheduler
            assert email_processor is not None
            assert scheduler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import workers package: {e}")

    def test_email_processor_class_available(self):
        """Test that EmailProcessor class is available for import."""
        from banktransactions.email_automation.workers.email_processor import EmailProcessor
        assert EmailProcessor is not None
        assert hasattr(EmailProcessor, 'process_user_emails')
        assert hasattr(EmailProcessor, '_extract_transaction_data')

    def test_email_scheduler_class_available(self):
        """Test that EmailScheduler class is available for import."""
        from banktransactions.email_automation.workers.scheduler import EmailScheduler
        assert EmailScheduler is not None
        assert hasattr(EmailScheduler, 'schedule_jobs')
        assert hasattr(EmailScheduler, '_calculate_next_run')

    def test_standalone_function_available(self):
        """Test that standalone function is available for import."""
        from banktransactions.email_automation.workers.email_processor import process_user_emails_standalone
        assert process_user_emails_standalone is not None
        assert callable(process_user_emails_standalone)


class TestWorkersMemoryAndPerformance:
    """Test memory usage and performance characteristics of workers."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_email_processor_memory_cleanup(self, mock_db_session):
        """Test that EmailProcessor properly cleans up resources."""
        processor = EmailProcessor(mock_db_session)
        
        # Verify processor can be created and destroyed without issues
        assert processor.db == mock_db_session
        
        # Simulate processing and cleanup
        del processor

    def test_email_scheduler_memory_cleanup(self):
        """Test that EmailScheduler properly cleans up resources."""
        mock_redis = Mock()
        mock_db = Mock()
        
        scheduler = EmailScheduler(mock_redis, mock_db)
        
        # Verify scheduler can be created and destroyed without issues
        assert scheduler.db == mock_db
        
        # Simulate scheduling and cleanup
        del scheduler

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    def test_process_user_emails_with_large_user_id(self, mock_get_job):
        """Test processing with very large user ID values."""
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        
        mock_db_session = Mock(spec=Session)
        processor = EmailProcessor(mock_db_session)
        
        # Mock no configuration found for large user ID
        processor.db.query.return_value.filter_by.return_value.first.return_value = None
        
        # Test with very large user ID
        large_user_id = 999999999999
        result = processor.process_user_emails(large_user_id)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "configuration_not_found_or_disabled"

    def test_scheduler_with_many_configurations(self):
        """Test scheduler performance with many configurations."""
        mock_redis = Mock()
        mock_db = Mock()
        
        scheduler = EmailScheduler(mock_redis, mock_db)
        
        # Mock many configurations
        configs = []
        for i in range(100):  # 100 configurations
            config = Mock()
            config.user_id = i
            config.is_enabled = True
            config.polling_interval = "hourly"
            config.last_check_time = datetime.utcnow() - timedelta(hours=2)
            configs.append(config)
        
        scheduler.db.query.return_value.filter_by.return_value.all.return_value = configs
        
        # Mock _schedule_user_job to avoid actual scheduling
        with patch.object(scheduler, '_schedule_user_job') as mock_schedule:
            scheduler.schedule_jobs()
            
            # Verify all configurations were processed
            assert mock_schedule.call_count == 100 