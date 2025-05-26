#!/usr/bin/env python3

import pytest
import os
import sys
from unittest.mock import patch, Mock

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from banktransactions.automation.run_scheduler import create_db_session, main


class TestRunScheduler:
    """Test cases for the run_scheduler.py script."""

    @patch("banktransactions.automation.run_scheduler.get_database_session")
    def test_create_db_session_success(self, mock_get_database_session):
        """Test successful database session creation."""
        mock_session_instance = Mock()
        mock_get_database_session.return_value = mock_session_instance

        result = create_db_session()

        # Should return the session instance
        assert result == mock_session_instance
        mock_get_database_session.assert_called_once()

    @patch("banktransactions.automation.run_scheduler.get_database_session")
    def test_create_db_session_error(self, mock_get_database_session):
        """Test handling of database session creation errors."""
        mock_get_database_session.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            create_db_session()

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    @patch("banktransactions.automation.run_scheduler.EmailScheduler")
    @patch("banktransactions.automation.run_scheduler.time.sleep")
    def test_main_success_single_iteration(
        self,
        mock_sleep,
        mock_scheduler_class,
        mock_create_db_session,
        mock_redis_from_url,
        mock_parser_class,
    ):
        """Test successful scheduler startup and single iteration."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.interval = 300
        mock_parser.parse_args.return_value = mock_args

        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        # Mock database session
        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session

        # Mock scheduler
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        # Mock sleep to raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        main()

        # Verify Redis connection was tested
        mock_redis_conn.ping.assert_called_once()

        # Verify scheduler was created with correct parameters
        mock_scheduler_class.assert_called_once_with(mock_redis_conn, mock_db_session)

        # Verify schedule_jobs was called
        mock_scheduler.schedule_jobs.assert_called_once()

        # Verify sleep was called with correct interval
        mock_sleep.assert_called_once_with(300)

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    def test_main_redis_connection_error(self, mock_redis_from_url, mock_parser_class):
        """Test handling of Redis connection errors."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_parser.parse_args.return_value = mock_args

        # Mock Redis connection to fail ping
        mock_redis_conn = Mock()
        mock_redis_conn.ping.side_effect = Exception("Redis connection failed")
        mock_redis_from_url.return_value = mock_redis_conn

        with pytest.raises(SystemExit):
            main()

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    def test_main_database_connection_error(
        self, mock_create_db_session, mock_redis_from_url, mock_parser_class
    ):
        """Test handling of database connection errors."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_parser.parse_args.return_value = mock_args

        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        # Mock database session creation to fail
        mock_create_db_session.side_effect = Exception("Database connection failed")

        with pytest.raises(SystemExit):
            main()

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    @patch("banktransactions.automation.run_scheduler.EmailScheduler")
    @patch("banktransactions.automation.run_scheduler.time.sleep")
    def test_main_keyboard_interrupt_immediate(
        self,
        mock_sleep,
        mock_scheduler_class,
        mock_create_db_session,
        mock_redis_from_url,
        mock_parser_class,
    ):
        """Test handling of immediate keyboard interrupt."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.interval = 300
        mock_parser.parse_args.return_value = mock_args

        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        # Mock database session
        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session

        # Mock scheduler to raise KeyboardInterrupt immediately
        mock_scheduler = Mock()
        mock_scheduler.schedule_jobs.side_effect = KeyboardInterrupt()
        mock_scheduler_class.return_value = mock_scheduler

        # Should not raise SystemExit for KeyboardInterrupt
        main()

        # Verify scheduler was created and called
        mock_scheduler_class.assert_called_once_with(mock_redis_conn, mock_db_session)
        mock_scheduler.schedule_jobs.assert_called_once()

        # Sleep should not be called if KeyboardInterrupt happens in schedule_jobs
        mock_sleep.assert_not_called()

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    @patch("banktransactions.automation.run_scheduler.EmailScheduler")
    @patch("banktransactions.automation.run_scheduler.time.sleep")
    def test_main_scheduler_exception_recovery(
        self,
        mock_sleep,
        mock_scheduler_class,
        mock_create_db_session,
        mock_redis_from_url,
        mock_parser_class,
    ):
        """Test that scheduler recovers from exceptions and continues."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.interval = 300
        mock_parser.parse_args.return_value = mock_args

        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        # Mock database session
        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session

        # Mock scheduler to fail first time, then succeed, then KeyboardInterrupt
        mock_scheduler = Mock()
        mock_scheduler.schedule_jobs.side_effect = [
            Exception("Scheduler error"),  # First call fails
            None,  # Second call succeeds
            KeyboardInterrupt(),  # Third call interrupted
        ]
        mock_scheduler_class.return_value = mock_scheduler

        # Mock sleep to not interrupt the first two iterations
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]

        main()

        # Verify scheduler was called multiple times (recovered from error)
        assert mock_scheduler.schedule_jobs.call_count == 3

        # Verify sleep was called for error recovery
        assert mock_sleep.call_count == 2

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    def test_main_argument_parsing(self, mock_parser_class):
        """Test that command line arguments are parsed correctly."""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock parse_args to raise SystemExit (simulating --help or invalid args)
        mock_parser.parse_args.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            main()

        # Verify parser was configured with expected arguments
        add_argument_calls = mock_parser.add_argument.call_args_list

        # Check that expected arguments were added
        arg_names = [call[0][0] for call in add_argument_calls]
        assert "--redis-url" in arg_names
        assert "--interval" in arg_names

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    @patch("banktransactions.automation.run_scheduler.EmailScheduler")
    @patch("banktransactions.automation.run_scheduler.time.sleep")
    def test_main_default_arguments(
        self,
        mock_sleep,
        mock_scheduler_class,
        mock_create_db_session,
        mock_redis_from_url,
        mock_parser_class,
    ):
        """Test that default arguments are used correctly."""
        # Mock argument parser with default values
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"  # Default value
        mock_args.interval = 300  # Default value (5 minutes)
        mock_parser.parse_args.return_value = mock_args

        # Mock other dependencies
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session

        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        # Mock sleep to raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        main()

        # Verify default interval was used
        mock_sleep.assert_called_once_with(300)

    @patch.dict(os.environ, {"REDIS_URL": "redis://custom:6379/1"})
    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    def test_main_environment_variable_defaults(self, mock_parser_class):
        """Test that environment variables are used for default values."""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Simulate argument parser setup
        mock_parser.parse_args.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            main()

        # Check that environment variable was used in argument setup
        add_argument_calls = mock_parser.add_argument.call_args_list

        # Find the redis-url argument call
        redis_url_call = None
        for call in add_argument_calls:
            if call[0][0] == "--redis-url":
                redis_url_call = call
                break

        assert redis_url_call is not None
        # The default should include the environment variable value
        assert "redis://custom:6379/1" in str(redis_url_call)

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    @patch("banktransactions.automation.run_scheduler.EmailScheduler")
    @patch("banktransactions.automation.run_scheduler.time.sleep")
    def test_main_custom_interval(
        self,
        mock_sleep,
        mock_scheduler_class,
        mock_create_db_session,
        mock_redis_from_url,
        mock_parser_class,
    ):
        """Test scheduler with custom interval."""
        # Mock argument parser with custom interval
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.interval = 600  # Custom 10-minute interval
        mock_parser.parse_args.return_value = mock_args

        # Mock other dependencies
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session

        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        # Mock sleep to raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        main()

        # Verify custom interval was used
        mock_sleep.assert_called_once_with(600)

    @patch("banktransactions.automation.run_scheduler.argparse.ArgumentParser")
    @patch("banktransactions.automation.run_scheduler.redis.from_url")
    @patch("banktransactions.automation.run_scheduler.create_db_session")
    @patch("banktransactions.automation.run_scheduler.EmailScheduler")
    @patch("banktransactions.automation.run_scheduler.time.sleep")
    def test_main_multiple_iterations(
        self,
        mock_sleep,
        mock_scheduler_class,
        mock_create_db_session,
        mock_redis_from_url,
        mock_parser_class,
    ):
        """Test scheduler running multiple iterations before stopping."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        mock_args = Mock()
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.interval = 100  # Short interval for testing
        mock_parser.parse_args.return_value = mock_args

        # Mock other dependencies
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn

        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session

        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        # Mock sleep to allow 3 iterations before KeyboardInterrupt
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]

        main()

        # Verify scheduler was called 3 times
        assert mock_scheduler.schedule_jobs.call_count == 3

        # Verify sleep was called 3 times (including the interrupted one)
        assert mock_sleep.call_count == 3
