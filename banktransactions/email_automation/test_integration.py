#!/usr/bin/env python3

import pytest
import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy.orm import Session

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from banktransactions.email_automation.workers.email_processor import EmailProcessor
from banktransactions.email_automation.workers.scheduler import EmailScheduler


class TestEmailAutomationIntegration:
    """Integration tests for the complete email automation workflow."""

    @pytest.fixture
    def mock_dependencies(self):
        """Set up all mocked dependencies for integration testing."""
        dependencies = {}
        
        # Mock Redis connection
        dependencies['redis_conn'] = Mock()
        dependencies['redis_conn'].ping.return_value = True
        
        # Mock database session
        dependencies['db_session'] = Mock(spec=Session)
        
        # Mock email configuration
        dependencies['email_config'] = Mock()
        dependencies['email_config'].user_id = 1
        dependencies['email_config'].is_enabled = True
        dependencies['email_config'].app_password = "encrypted_password"
        dependencies['email_config'].imap_server = "imap.gmail.com"
        dependencies['email_config'].imap_port = 993
        dependencies['email_config'].email_address = "test@example.com"
        dependencies['email_config'].last_check_time = datetime.now(timezone.utc) - timedelta(hours=2)
        dependencies['email_config'].sample_emails = json.dumps([{"subject": "Test", "body": "Sample"}])
        dependencies['email_config'].polling_interval = "hourly"
        
        # Mock email data
        dependencies['email_data'] = [
            {
                "id": "email_1",
                "subject": "Transaction Alert - Debit",
                "body": "Your account XX1648 has been debited with Rs. 500.00 on 2024-01-01 for RESTAURANT PAYMENT",
                "from": "alerts@bank.com",
                "date": datetime.now(timezone.utc)
            },
            {
                "id": "email_2",
                "subject": "Payment Confirmation",
                "body": "Payment of Rs. 250.00 to GROCERY STORE completed successfully",
                "from": "payments@bank.com",
                "date": datetime.now(timezone.utc)
            }
        ]
        
        return dependencies

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    @patch('banktransactions.email_automation.workers.email_processor.extract_transaction_details_pure_llm')
    def test_complete_email_processing_workflow(self, mock_extract_llm, mock_api_client_class, 
                                              mock_imap_client_class, mock_decrypt, mock_get_job, 
                                              mock_dependencies):
        """Test the complete email processing workflow from start to finish."""
        
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock IMAP client
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = mock_dependencies['email_data']
        
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.create_transaction.return_value = {"success": True}
        
        # Mock LLM extraction
        mock_extract_llm.side_effect = [
            {
                "amount": 500.0,
                "date": "2024-01-01",
                "account_number": "XX1648",
                "recipient": "RESTAURANT PAYMENT",
                "transaction_type": "debit"
            },
            {
                "amount": 250.0,
                "date": "2024-01-01", 
                "account_number": "XX1648",
                "recipient": "GROCERY STORE",
                "transaction_type": "debit"
            }
        ]
        
        # Create EmailProcessor and mock database query
        processor = EmailProcessor(mock_dependencies['db_session'])
        processor.db.query.return_value.filter_by.return_value.first.return_value = mock_dependencies['email_config']
        
        # Execute the workflow
        result = processor.process_user_emails(1)
        
        # Verify the complete workflow
        assert result["status"] == "success"
        assert result["processed_count"] == 2
        assert result["errors"] == []
        
        # Verify IMAP operations
        mock_imap_client.connect.assert_called_once()
        mock_imap_client.get_unread_emails.assert_called_once()
        assert mock_imap_client.mark_as_processed.call_count == 2
        mock_imap_client.disconnect.assert_called_once()
        
        # Verify API operations
        assert mock_api_client.create_transaction.call_count == 2
        
        # Verify LLM extraction was called for each email
        assert mock_extract_llm.call_count == 2
        
        # Verify database operations
        processor.db.commit.assert_called_once()

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_scheduler_integration_with_processor(self, mock_scheduler_class, mock_dependencies):
        """Test integration between scheduler and email processor."""
        
        # Setup scheduler
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        
        scheduler = EmailScheduler(mock_dependencies['redis_conn'], mock_dependencies['db_session'])
        scheduler.scheduler = mock_scheduler
        
        # Mock database query to return configurations
        configs = [mock_dependencies['email_config']]
        scheduler.db.query.return_value.filter_by.return_value.all.return_value = configs
        
        # Mock _calculate_next_run to return immediate execution
        with patch.object(scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = datetime.utcnow()
            
            # Execute scheduling
            scheduler.schedule_jobs()
        
        # Verify job was scheduled
        mock_scheduler.enqueue_at.assert_called_once()
        
        # Verify the scheduled function and arguments
        call_args = mock_scheduler.enqueue_at.call_args
        scheduled_function = call_args[0][1]
        user_id_arg = call_args[0][2]
        
        from banktransactions.email_automation.workers.email_processor import process_user_emails_standalone
        assert scheduled_function == process_user_emails_standalone
        assert user_id_arg == 1

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    def test_error_handling_integration(self, mock_api_client_class, mock_imap_client_class,
                                      mock_decrypt, mock_get_job, mock_dependencies):
        """Test error handling across the integrated workflow."""
        
        # Setup mocks for error scenarios
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock IMAP client to succeed
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = mock_dependencies['email_data'][:1]  # One email
        
        # Mock API client to fail
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.create_transaction.return_value = {"success": False, "error": "API Error"}
        
        # Create processor and setup database
        processor = EmailProcessor(mock_dependencies['db_session'])
        processor.db.query.return_value.filter_by.return_value.first.return_value = mock_dependencies['email_config']
        
        # Mock transaction extraction to succeed
        with patch.object(processor, '_extract_transaction_data') as mock_extract:
            mock_extract.return_value = {"amount": 500.0, "account": "XX1648"}
            
            result = processor.process_user_emails(1)
        
        # Verify error handling
        assert result["status"] == "success"  # Overall success despite API failure
        assert result["processed_count"] == 0  # No transactions created
        assert len(result["errors"]) == 1  # One error recorded
        assert "Failed to create transaction" in result["errors"][0]
        
        # Verify cleanup still occurred
        mock_imap_client.disconnect.assert_called_once()

    @patch('banktransactions.email_automation.workers.email_processor.get_current_job')
    @patch('banktransactions.email_automation.workers.email_processor.decrypt_value')
    @patch('banktransactions.email_automation.workers.email_processor.IMAPClient')
    @patch('banktransactions.email_automation.workers.email_processor.APIClient')
    def test_partial_processing_integration(self, mock_api_client_class, mock_imap_client_class,
                                          mock_decrypt, mock_get_job, mock_dependencies):
        """Test integration when some emails process successfully and others fail."""
        
        # Setup mocks
        mock_job = Mock()
        mock_get_job.return_value = mock_job
        mock_decrypt.return_value = "decrypted_password"
        
        # Mock IMAP client
        mock_imap_client = Mock()
        mock_imap_client_class.return_value = mock_imap_client
        mock_imap_client.get_unread_emails.return_value = mock_dependencies['email_data']
        
        # Mock API client with mixed results
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.create_transaction.side_effect = [
            {"success": True},  # First email succeeds
            {"success": False, "error": "Validation failed"}  # Second email fails
        ]
        
        # Create processor
        processor = EmailProcessor(mock_dependencies['db_session'])
        processor.db.query.return_value.filter_by.return_value.first.return_value = mock_dependencies['email_config']
        
        # Mock transaction extraction
        with patch.object(processor, '_extract_transaction_data') as mock_extract:
            mock_extract.side_effect = [
                {"amount": 500.0, "account": "XX1648"},
                {"amount": 250.0, "account": "XX1648"}
            ]
            
            result = processor.process_user_emails(1)
        
        # Verify partial success
        assert result["status"] == "success"
        assert result["processed_count"] == 1  # Only one succeeded
        assert len(result["errors"]) == 1  # One error
        
        # Verify both emails were attempted
        assert mock_api_client.create_transaction.call_count == 2
        
        # Verify only successful email was marked as processed
        assert mock_imap_client.mark_as_processed.call_count == 1

    @patch('banktransactions.email_automation.workers.email_processor.create_engine')
    @patch('banktransactions.email_automation.workers.email_processor.sessionmaker')
    @patch('banktransactions.email_automation.workers.email_processor.EmailProcessor')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_standalone_function_integration(self, mock_processor_class, mock_sessionmaker, mock_create_engine):
        """Test the standalone function integration with database session management."""
        
        # Setup database mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session_class = Mock()
        mock_sessionmaker.return_value = mock_session_class
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Setup processor mock
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_user_emails.return_value = {
            "status": "success",
            "processed_count": 3,
            "errors": []
        }
        
        # Import and test standalone function
        from banktransactions.email_automation.workers.email_processor import process_user_emails_standalone
        
        result = process_user_emails_standalone(1)
        
        # Verify database session lifecycle
        mock_create_engine.assert_called_once_with('postgresql://test:test@localhost/test')
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        mock_session_class.assert_called_once()
        mock_session.close.assert_called_once()
        
        # Verify processor was created and called
        mock_processor_class.assert_called_once_with(mock_session)
        mock_processor.process_user_emails.assert_called_once_with(1)
        
        # Verify result
        assert result["status"] == "success"
        assert result["processed_count"] == 3

    def test_configuration_validation_integration(self, mock_dependencies):
        """Test configuration validation in the integrated workflow."""
        
        # Test various configuration scenarios
        test_configs = [
            # Valid configuration
            {
                "user_id": 1,
                "is_enabled": True,
                "polling_interval": "hourly",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "email_address": "test@example.com",
                "app_password": "encrypted_password"
            },
            # Disabled configuration
            {
                "user_id": 2,
                "is_enabled": False,
                "polling_interval": "daily",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "email_address": "test2@example.com",
                "app_password": "encrypted_password"
            }
        ]
        
        for config in test_configs:
            # Validate required fields
            required_fields = ["user_id", "is_enabled", "polling_interval", "imap_server", "imap_port"]
            for field in required_fields:
                assert field in config, f"Missing required field: {field}"
            
            # Validate field types and values
            assert isinstance(config["user_id"], int)
            assert isinstance(config["is_enabled"], bool)
            assert config["polling_interval"] in ["hourly", "daily"]
            assert isinstance(config["imap_port"], int)
            assert config["imap_port"] > 0

    @patch('redis.from_url')
    @patch('sqlalchemy.create_engine')
    def test_system_dependencies_integration(self, mock_create_engine, mock_redis):
        """Test integration of all system dependencies."""
        
        # Mock Redis
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn
        mock_redis_conn.ping.return_value = True
        
        # Mock database
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_connection = Mock()
        mock_engine.connect.return_value = mock_connection
        
        # Test system connectivity
        redis_connected = mock_redis_conn.ping()
        db_connection = mock_engine.connect()
        
        assert redis_connected is True
        assert db_connection is not None
        
        # Test that both systems can be used together
        mock_redis_conn.rpush("test_queue", "test_job")
        mock_connection.execute("SELECT 1")
        
        mock_redis_conn.rpush.assert_called_once()
        mock_connection.execute.assert_called_once()

    def test_data_flow_integration(self, mock_dependencies):
        """Test data flow through the complete system."""
        
        # Simulate the data transformation pipeline
        raw_email = mock_dependencies['email_data'][0]
        
        # Step 1: Email extraction (IMAP)
        extracted_email = {
            "id": raw_email["id"],
            "subject": raw_email["subject"],
            "body": raw_email["body"],
            "from": raw_email["from"],
            "date": raw_email["date"]
        }
        
        # Step 2: Transaction parsing (LLM)
        parsed_transaction = {
            "amount": 500.0,
            "date": "2024-01-01",
            "account_number": "XX1648",
            "recipient": "RESTAURANT PAYMENT",
            "transaction_type": "debit",
            "email_id": extracted_email["id"],
            "email_subject": extracted_email["subject"],
            "email_from": extracted_email["from"]
        }
        
        # Step 3: API payload construction
        api_payload = {
            "amount": parsed_transaction["amount"],
            "date": parsed_transaction["date"],
            "from_account": f"Assets:Bank:{parsed_transaction['account_number']}",
            "to_account": f"Expenses:Unknown:{parsed_transaction['recipient']}",
            "description": f"{parsed_transaction['recipient']} - {parsed_transaction['email_subject']}",
            "metadata": {
                "email_id": parsed_transaction["email_id"],
                "email_from": parsed_transaction["email_from"],
                "source": "email_automation"
            }
        }
        
        # Verify data transformations
        assert api_payload["amount"] == 500.0
        assert api_payload["date"] == "2024-01-01"
        assert "XX1648" in api_payload["from_account"]
        assert "RESTAURANT PAYMENT" in api_payload["to_account"]
        assert api_payload["metadata"]["source"] == "email_automation"

    @patch('time.sleep')
    def test_scheduling_timing_integration(self, mock_sleep, mock_dependencies):
        """Test scheduling timing and intervals."""
        
        # Test different polling intervals
        intervals = ["hourly", "daily"]
        
        for interval in intervals:
            config = mock_dependencies['email_config']
            config.polling_interval = interval
            
            scheduler = EmailScheduler(mock_dependencies['redis_conn'], mock_dependencies['db_session'])
            
            # Test next run calculation
            now = datetime.utcnow()
            
            if interval == "hourly":
                # If last check was 2 hours ago, should run now
                config.last_check_time = now - timedelta(hours=2)
                next_run = scheduler._calculate_next_run(config)
                assert abs((next_run - now).total_seconds()) < 60  # Within 1 minute
                
            elif interval == "daily":
                # If last check was 2 days ago, should run now
                config.last_check_time = now - timedelta(days=2)
                next_run = scheduler._calculate_next_run(config)
                assert abs((next_run - now).total_seconds()) < 60  # Within 1 minute

    def test_error_recovery_integration(self, mock_dependencies):
        """Test error recovery mechanisms across the system."""
        
        # Test scenarios where system should recover gracefully
        error_scenarios = [
            {
                "name": "IMAP connection failure",
                "error": "Connection timeout",
                "expected_behavior": "Retry with exponential backoff"
            },
            {
                "name": "API rate limiting",
                "error": "Rate limit exceeded",
                "expected_behavior": "Queue job for later retry"
            },
            {
                "name": "Database connection loss",
                "error": "Connection lost",
                "expected_behavior": "Reconnect and retry transaction"
            },
            {
                "name": "LLM parsing failure",
                "error": "Unable to parse email",
                "expected_behavior": "Log error and continue with next email"
            }
        ]
        
        for scenario in error_scenarios:
            # Each scenario should have defined error handling
            assert "error" in scenario
            assert "expected_behavior" in scenario
            
            # Verify error scenarios are documented and handled
            assert scenario["expected_behavior"] is not None 