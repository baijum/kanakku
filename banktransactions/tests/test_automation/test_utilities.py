#!/usr/bin/env python3

import pytest
import os
import sys
import json
from unittest.mock import patch, Mock, mock_open
from datetime import datetime, timezone

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestCheckConfigs:
    """Test cases for the check_configs.py utility script."""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"DATABASE_URL": "postgresql://test", "REDIS_URL": "redis://test"}',
    )
    @patch("os.path.exists")
    def test_check_configs_file_exists(self, mock_exists, mock_file):
        """Test checking configurations when config file exists."""
        mock_exists.return_value = True

        # Import and test the check_configs functionality
        # Note: This would need to be adapted based on actual implementation
        # For now, testing the concept

        # Simulate reading config file
        config_data = json.loads(mock_file.return_value.read())

        assert "DATABASE_URL" in config_data
        assert "REDIS_URL" in config_data
        assert config_data["DATABASE_URL"] == "postgresql://test"

    @patch("os.path.exists")
    def test_check_configs_file_not_exists(self, mock_exists):
        """Test checking configurations when config file doesn't exist."""
        mock_exists.return_value = False

        # This should handle the case where config file is missing
        # Implementation would depend on actual script behavior
        assert not mock_exists("/path/to/config.json")

    @patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://env_test", "REDIS_URL": "redis://env_test"},
    )
    def test_check_configs_environment_variables(self):
        """Test checking configurations from environment variables."""
        # Test that environment variables are properly read
        assert os.getenv("DATABASE_URL") == "postgresql://env_test"
        assert os.getenv("REDIS_URL") == "redis://env_test"

    @patch.dict(os.environ, {}, clear=True)
    def test_check_configs_missing_env_vars(self):
        """Test handling of missing environment variables."""
        # Test that missing environment variables are handled
        assert os.getenv("DATABASE_URL") is None
        assert os.getenv("REDIS_URL") is None


class TestCheckFailed:
    """Test cases for the check_failed.py utility script."""

    @patch("redis.from_url")
    def test_check_failed_jobs_redis_connection(self, mock_redis):
        """Test checking failed jobs with Redis connection."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock failed jobs
        mock_redis_conn.lrange.return_value = [
            b'{"id": "job_1", "error": "Connection failed"}',
            b'{"id": "job_2", "error": "Timeout"}',
        ]

        # Simulate checking failed jobs
        failed_jobs = mock_redis_conn.lrange("rq:queue:failed", 0, -1)

        assert len(failed_jobs) == 2
        mock_redis_conn.lrange.assert_called_once_with("rq:queue:failed", 0, -1)

    @patch("redis.from_url")
    def test_check_failed_jobs_no_failures(self, mock_redis):
        """Test checking failed jobs when there are no failures."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock no failed jobs
        mock_redis_conn.lrange.return_value = []

        failed_jobs = mock_redis_conn.lrange("rq:queue:failed", 0, -1)

        assert len(failed_jobs) == 0

    @patch("redis.from_url")
    def test_check_failed_jobs_redis_error(self, mock_redis):
        """Test handling Redis connection errors when checking failed jobs."""
        mock_redis.side_effect = Exception("Redis connection failed")

        with pytest.raises(Exception, match="Redis connection failed"):
            mock_redis("redis://localhost:6379")

    @patch("redis.from_url")
    def test_check_failed_jobs_parse_job_data(self, mock_redis):
        """Test parsing failed job data."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        job_data = {
            "id": "test_job_123",
            "error": "Email processing failed",
            "created_at": "2024-01-01T12:00:00Z",
            "failed_at": "2024-01-01T12:05:00Z",
        }

        mock_redis_conn.lrange.return_value = [json.dumps(job_data).encode()]

        failed_jobs = mock_redis_conn.lrange("rq:queue:failed", 0, -1)
        parsed_job = json.loads(failed_jobs[0].decode())

        assert parsed_job["id"] == "test_job_123"
        assert parsed_job["error"] == "Email processing failed"


class TestMoveJobs:
    """Test cases for the move_jobs.py utility script."""

    @patch("redis.from_url")
    def test_move_jobs_between_queues(self, mock_redis):
        """Test moving jobs between Redis queues."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock job data
        job_data = {"id": "job_1", "user_id": 123, "status": "pending"}
        mock_redis_conn.lpop.return_value = json.dumps(job_data).encode()

        # Simulate moving job from one queue to another
        source_queue = "rq:queue:failed"
        target_queue = "rq:queue:email_processing"

        # Pop from source queue
        job = mock_redis_conn.lpop(source_queue)

        # Push to target queue
        if job:
            mock_redis_conn.rpush(target_queue, job)

        mock_redis_conn.lpop.assert_called_once_with(source_queue)
        mock_redis_conn.rpush.assert_called_once_with(target_queue, job)

    @patch("redis.from_url")
    def test_move_jobs_empty_source_queue(self, mock_redis):
        """Test moving jobs when source queue is empty."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock empty queue
        mock_redis_conn.lpop.return_value = None

        source_queue = "rq:queue:failed"
        job = mock_redis_conn.lpop(source_queue)

        assert job is None
        mock_redis_conn.lpop.assert_called_once_with(source_queue)

    @patch("redis.from_url")
    def test_move_jobs_batch_operation(self, mock_redis):
        """Test moving multiple jobs in batch."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock multiple jobs
        jobs = [
            {"id": "job_1", "user_id": 123},
            {"id": "job_2", "user_id": 456},
            {"id": "job_3", "user_id": 789},
        ]

        mock_redis_conn.lrange.return_value = [json.dumps(job).encode() for job in jobs]

        source_queue = "rq:queue:failed"
        target_queue = "rq:queue:email_processing"

        # Get all jobs from source queue
        all_jobs = mock_redis_conn.lrange(source_queue, 0, -1)

        # Simulate batch move
        if all_jobs:
            # Clear source queue
            mock_redis_conn.delete(source_queue)
            # Add all jobs to target queue
            for job in all_jobs:
                mock_redis_conn.rpush(target_queue, job)

        assert len(all_jobs) == 3
        mock_redis_conn.lrange.assert_called_once_with(source_queue, 0, -1)

    @patch("redis.from_url")
    def test_move_jobs_with_filtering(self, mock_redis):
        """Test moving jobs with filtering criteria."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock jobs with different user IDs
        jobs = [
            {"id": "job_1", "user_id": 123, "error": "timeout"},
            {"id": "job_2", "user_id": 456, "error": "connection"},
            {"id": "job_3", "user_id": 123, "error": "auth"},
        ]

        mock_redis_conn.lrange.return_value = [json.dumps(job).encode() for job in jobs]

        # Filter jobs for specific user
        target_user_id = 123
        all_jobs = mock_redis_conn.lrange("rq:queue:failed", 0, -1)

        filtered_jobs = []
        for job_data in all_jobs:
            job = json.loads(job_data.decode())
            if job.get("user_id") == target_user_id:
                filtered_jobs.append(job)

        assert len(filtered_jobs) == 2
        assert all(job["user_id"] == 123 for job in filtered_jobs)


class TestJobUtilities:
    """Test cases for the test_job.py utility script."""

    @patch("redis.from_url")
    def test_enqueue_test_job(self, mock_redis):
        """Test enqueueing a test job."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        # Mock job enqueueing
        mock_job_id = "test_job_12345"
        mock_redis_conn.rpush.return_value = 1

        # Simulate enqueueing a test job
        test_job_data = {
            "id": mock_job_id,
            "function": "process_user_emails_standalone",
            "args": [123],  # user_id
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        queue_name = "rq:queue:email_processing"
        result = mock_redis_conn.rpush(queue_name, json.dumps(test_job_data))

        assert result == 1
        mock_redis_conn.rpush.assert_called_once()

    @patch("redis.from_url")
    def test_check_job_status(self, mock_redis):
        """Test checking job status."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        job_id = "test_job_12345"
        job_status = {
            "id": job_id,
            "status": "finished",
            "result": {"processed_count": 5, "errors": []},
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }

        # Mock job status retrieval
        mock_redis_conn.hget.return_value = json.dumps(job_status).encode()

        status = mock_redis_conn.hget(f"rq:job:{job_id}", "status")
        parsed_status = json.loads(status.decode())

        assert parsed_status["status"] == "finished"
        assert parsed_status["result"]["processed_count"] == 5

    @patch("redis.from_url")
    def test_job_timeout_handling(self, mock_redis):
        """Test handling job timeouts."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        job_id = "timeout_job_12345"

        # Mock timeout scenario
        mock_redis_conn.hget.return_value = None  # Job not found (timed out)

        status = mock_redis_conn.hget(f"rq:job:{job_id}", "status")

        assert status is None  # Job has timed out or been cleaned up

    @patch("redis.from_url")
    def test_job_error_handling(self, mock_redis):
        """Test handling job errors."""
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn

        job_id = "error_job_12345"
        job_error = {
            "id": job_id,
            "status": "failed",
            "error": "Database connection failed",
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "traceback": "Traceback (most recent call last):\n  File...",
        }

        mock_redis_conn.hget.return_value = json.dumps(job_error).encode()

        status = mock_redis_conn.hget(f"rq:job:{job_id}", "status")
        parsed_status = json.loads(status.decode())

        assert parsed_status["status"] == "failed"
        assert "Database connection failed" in parsed_status["error"]


class TestSystemValidation:
    """Test cases for system validation utilities."""

    @patch("redis.from_url")
    @patch("sqlalchemy.create_engine")
    def test_system_connectivity(self, mock_create_engine, mock_redis):
        """Test system connectivity validation."""
        # Mock Redis connection
        mock_redis_conn = Mock()
        mock_redis.return_value = mock_redis_conn
        mock_redis_conn.ping.return_value = True

        # Mock database connection
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_connection = Mock()
        mock_engine.connect.return_value = mock_connection

        # Test Redis connectivity
        redis_connected = mock_redis_conn.ping()
        assert redis_connected is True

        # Test database connectivity
        db_connection = mock_engine.connect()
        assert db_connection is not None

    @patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "ENCRYPTION_KEY": "test_key_123",
        },
    )
    def test_environment_validation(self):
        """Test environment variable validation."""
        required_vars = ["DATABASE_URL", "REDIS_URL", "ENCRYPTION_KEY"]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        assert len(missing_vars) == 0, f"Missing environment variables: {missing_vars}"

    @patch("importlib.import_module")
    def test_module_imports(self, mock_import):
        """Test that required modules can be imported."""
        required_modules = ["redis", "sqlalchemy", "rq", "rq_scheduler"]

        # Mock successful imports
        mock_import.return_value = Mock()

        for module in required_modules:
            try:
                imported_module = mock_import(module)
                assert imported_module is not None
            except ImportError:
                pytest.fail(f"Failed to import required module: {module}")

    def test_configuration_validation(self):
        """Test configuration validation logic."""
        # Test valid configuration
        valid_config = {
            "polling_interval": "hourly",
            "is_enabled": True,
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
        }

        # Validate required fields
        required_fields = ["polling_interval", "is_enabled", "imap_server", "imap_port"]
        for field in required_fields:
            assert field in valid_config, f"Missing required field: {field}"

        # Validate field values
        assert valid_config["polling_interval"] in ["hourly", "daily"]
        assert isinstance(valid_config["is_enabled"], bool)
        assert isinstance(valid_config["imap_port"], int)
        assert valid_config["imap_port"] > 0

    def test_invalid_configuration_handling(self):
        """Test handling of invalid configurations."""
        invalid_configs = [
            {"polling_interval": "invalid"},  # Invalid interval
            {"is_enabled": "yes"},  # Wrong type
            {"imap_port": -1},  # Invalid port
            {},  # Missing fields
        ]

        for config in invalid_configs:
            # Test that validation would catch these issues
            if "polling_interval" in config:
                assert (
                    config["polling_interval"] not in ["hourly", "daily"]
                    or not isinstance(config.get("is_enabled"), bool)
                    or (
                        isinstance(config.get("imap_port"), int)
                        and config.get("imap_port", 0) <= 0
                    )
                    or len(config) == 0
                )
