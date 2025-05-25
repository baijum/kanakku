#!/usr/bin/env python3

import pytest
import os
import sys
import argparse
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy.orm import Session

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from banktransactions.email_automation.run_worker import create_db_session, main


class TestRunWorker:
    """Test cases for the run_worker.py script."""

    @patch('banktransactions.email_automation.run_worker.create_engine')
    @patch('banktransactions.email_automation.run_worker.sessionmaker')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_create_db_session_success(self, mock_sessionmaker, mock_create_engine):
        """Test successful database session creation."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session_class = Mock()
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance
        mock_sessionmaker.return_value = mock_session_class
        
        result = create_db_session()
        
        # Should return the session instance
        assert result == mock_session_instance
        mock_create_engine.assert_called_once_with('postgresql://test:test@localhost/test')
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        mock_session_class.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_create_db_session_no_url(self):
        """Test database session creation when DATABASE_URL is not set."""
        with pytest.raises(ValueError, match="DATABASE_URL environment variable not set"):
            create_db_session()

    @patch('banktransactions.email_automation.run_worker.create_engine')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'})
    def test_create_db_session_engine_error(self, mock_create_engine):
        """Test handling of database engine creation errors."""
        mock_create_engine.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            create_db_session()

    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
    @patch('banktransactions.email_automation.run_worker.redis.from_url')
    @patch('banktransactions.email_automation.run_worker.create_db_session')
    @patch('banktransactions.email_automation.run_worker.Queue')
    @patch('banktransactions.email_automation.run_worker.Worker')
    @patch('banktransactions.email_automation.run_worker.Connection')
    def test_main_success(self, mock_connection, mock_worker_class, mock_queue_class,
                         mock_create_db_session, mock_redis_from_url, mock_parser_class):
        """Test successful worker startup and execution."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        mock_args = Mock()
        mock_args.queue_name = "email_processing"
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.worker_name = "test_worker"
        mock_parser.parse_args.return_value = mock_args
        
        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn
        
        # Mock database session
        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session
        
        # Mock queue
        mock_queue = Mock()
        mock_queue_class.return_value = mock_queue
        
        # Mock worker
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        # Mock connection context manager
        mock_connection_context = Mock()
        mock_connection.return_value.__enter__ = Mock(return_value=mock_connection_context)
        mock_connection.return_value.__exit__ = Mock(return_value=None)
        
        main()
        
        # Verify Redis connection was tested
        mock_redis_conn.ping.assert_called_once()
        
        # Verify queue was created with correct parameters
        mock_queue_class.assert_called_once_with("email_processing", connection=mock_redis_conn)
        
        # Verify worker was created and started
        mock_worker_class.assert_called_once_with([mock_queue], connection=mock_redis_conn, name="test_worker")
        mock_worker.work.assert_called_once()

    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
    @patch('banktransactions.email_automation.run_worker.redis.from_url')
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

    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
    @patch('banktransactions.email_automation.run_worker.redis.from_url')
    @patch('banktransactions.email_automation.run_worker.create_db_session')
    def test_main_database_connection_error(self, mock_create_db_session, mock_redis_from_url, mock_parser_class):
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

    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
    @patch('banktransactions.email_automation.run_worker.redis.from_url')
    @patch('banktransactions.email_automation.run_worker.create_db_session')
    @patch('banktransactions.email_automation.run_worker.Queue')
    @patch('banktransactions.email_automation.run_worker.Worker')
    @patch('banktransactions.email_automation.run_worker.Connection')
    def test_main_keyboard_interrupt(self, mock_connection, mock_worker_class, mock_queue_class,
                                   mock_create_db_session, mock_redis_from_url, mock_parser_class):
        """Test handling of keyboard interrupt (Ctrl+C)."""
        # Mock argument parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        mock_args = Mock()
        mock_args.queue_name = "email_processing"
        mock_args.redis_url = "redis://localhost:6379/0"
        mock_args.worker_name = None  # Test auto-generated name
        mock_parser.parse_args.return_value = mock_args
        
        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn
        
        # Mock database session
        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session
        
        # Mock queue
        mock_queue = Mock()
        mock_queue_class.return_value = mock_queue
        
        # Mock worker to raise KeyboardInterrupt
        mock_worker = Mock()
        mock_worker.work.side_effect = KeyboardInterrupt()
        mock_worker_class.return_value = mock_worker
        
        # Mock connection context manager
        mock_connection_context = Mock()
        mock_connection.return_value.__enter__ = Mock(return_value=mock_connection_context)
        mock_connection.return_value.__exit__ = Mock(return_value=None)
        
        # Should not raise SystemExit for KeyboardInterrupt
        main()
        
        # Verify worker was created with auto-generated name
        worker_call_args = mock_worker_class.call_args
        worker_name = worker_call_args[1]["name"]
        assert worker_name.startswith("email_worker_")

    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
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
        assert "--queue-name" in arg_names
        assert "--redis-url" in arg_names
        assert "--worker-name" in arg_names

    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
    @patch('banktransactions.email_automation.run_worker.redis.from_url')
    @patch('banktransactions.email_automation.run_worker.create_db_session')
    @patch('banktransactions.email_automation.run_worker.Queue')
    @patch('banktransactions.email_automation.run_worker.Worker')
    @patch('banktransactions.email_automation.run_worker.Connection')
    def test_main_default_arguments(self, mock_connection, mock_worker_class, mock_queue_class,
                                  mock_create_db_session, mock_redis_from_url, mock_parser_class):
        """Test that default arguments are used correctly."""
        # Mock argument parser with default values
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        mock_args = Mock()
        mock_args.queue_name = "email_processing"  # Default value
        mock_args.redis_url = "redis://localhost:6379/0"  # Default value
        mock_args.worker_name = None  # Default value (auto-generated)
        mock_parser.parse_args.return_value = mock_args
        
        # Mock other dependencies
        mock_redis_conn = Mock()
        mock_redis_from_url.return_value = mock_redis_conn
        
        mock_db_session = Mock()
        mock_create_db_session.return_value = mock_db_session
        
        mock_queue = Mock()
        mock_queue_class.return_value = mock_queue
        
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        mock_connection_context = Mock()
        mock_connection.return_value.__enter__ = Mock(return_value=mock_connection_context)
        mock_connection.return_value.__exit__ = Mock(return_value=None)
        
        main()
        
        # Verify default queue name was used
        mock_queue_class.assert_called_once_with("email_processing", connection=mock_redis_conn)
        
        # Verify auto-generated worker name was used
        worker_call_args = mock_worker_class.call_args
        worker_name = worker_call_args[1]["name"]
        assert worker_name.startswith("email_worker_")

    @patch.dict(os.environ, {'REDIS_URL': 'redis://custom:6379/1'})
    @patch('banktransactions.email_automation.run_worker.argparse.ArgumentParser')
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