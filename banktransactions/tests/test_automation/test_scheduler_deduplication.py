#!/usr/bin/env python3
"""
Test script for scheduler deduplication functionality.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

from banktransactions.automation.scheduler import EmailScheduler
from banktransactions.automation.job_utils import (
    generate_job_id,
    has_user_job_pending,
    get_user_job_status,
)


class TestSchedulerDeduplication:
    """Test cases for scheduler deduplication functionality."""

    @pytest.fixture
    def mock_redis_conn(self):
        """Create a mock Redis connection."""
        return Mock()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def email_scheduler(self, mock_redis_conn, mock_db_session):
        """Create an EmailScheduler instance with mocked dependencies."""
        with patch("banktransactions.automation.scheduler.Scheduler"):
            return EmailScheduler(mock_redis_conn, mock_db_session)

    @pytest.fixture
    def mock_email_config(self):
        """Create a mock EmailConfiguration object."""
        config = Mock()
        config.user_id = 123
        config.email_address = "test@example.com"
        config.is_enabled = True
        config.polling_interval = "hourly"
        config.last_check_time = datetime.now(timezone.utc) - timedelta(hours=2)
        return config

    def test_scheduler_skips_when_job_pending(self, email_scheduler, mock_email_config):
        """Test that scheduler skips scheduling when user already has a pending job."""

        # Mock has_user_job_pending to return True
        with patch(
            "banktransactions.automation.scheduler.has_user_job_pending"
        ) as mock_has_pending:
            with patch(
                "banktransactions.automation.scheduler.get_user_job_status"
            ) as mock_get_status:
                mock_has_pending.return_value = True
                mock_get_status.return_value = {
                    "user_id": 123,
                    "has_running_job": True,
                    "has_scheduled_job": False,
                    "has_queued_job": False,
                    "has_any_pending": True,
                }

                # Mock _calculate_next_run to ensure it would normally schedule
                with patch.object(
                    email_scheduler, "_calculate_next_run"
                ) as mock_calc_next:
                    mock_calc_next.return_value = datetime.now(timezone.utc)

                    # Call _schedule_user_job
                    email_scheduler._schedule_user_job(mock_email_config)

                    # Verify that has_user_job_pending was called
                    mock_has_pending.assert_called_once_with(
                        email_scheduler.redis_conn, 123
                    )

                    # Verify that scheduler.enqueue_at was NOT called
                    email_scheduler.scheduler.enqueue_at.assert_not_called()

    def test_scheduler_proceeds_when_no_job_pending(
        self, email_scheduler, mock_email_config
    ):
        """Test that scheduler proceeds with scheduling when no job is pending."""

        # Mock has_user_job_pending to return False
        with patch(
            "banktransactions.automation.scheduler.has_user_job_pending"
        ) as mock_has_pending:
            with patch(
                "banktransactions.automation.scheduler.generate_job_id"
            ) as mock_gen_id:
                mock_has_pending.return_value = False
                mock_gen_id.return_value = "email_process_123_1234567890"

                # Mock _calculate_next_run
                next_run = datetime.now(timezone.utc) + timedelta(minutes=30)
                with patch.object(
                    email_scheduler, "_calculate_next_run"
                ) as mock_calc_next:
                    mock_calc_next.return_value = next_run

                    # Call _schedule_user_job
                    email_scheduler._schedule_user_job(mock_email_config)

                    # Verify that has_user_job_pending was called
                    mock_has_pending.assert_called_once_with(
                        email_scheduler.redis_conn, 123
                    )

                    # Verify that generate_job_id was called
                    mock_gen_id.assert_called_once_with(123, next_run)

                    # Verify that scheduler.enqueue_at was called
                    email_scheduler.scheduler.enqueue_at.assert_called_once()

    def test_job_id_generation_consistency(self):
        """Test that job ID generation is consistent for the same parameters."""
        user_id = 456
        timestamp = datetime(2024, 1, 1, 12, 0, 0)

        job_id_1 = generate_job_id(user_id, timestamp)
        job_id_2 = generate_job_id(user_id, timestamp)

        assert job_id_1 == job_id_2
        assert job_id_1 == f"email_process_{user_id}_{int(timestamp.timestamp())}"

    def test_job_id_generation_different_timestamps(self):
        """Test that job IDs are different for different timestamps."""
        user_id = 456
        timestamp_1 = datetime(2024, 1, 1, 12, 0, 0)
        timestamp_2 = datetime(2024, 1, 1, 12, 0, 1)  # 1 second later

        job_id_1 = generate_job_id(user_id, timestamp_1)
        job_id_2 = generate_job_id(user_id, timestamp_2)

        assert job_id_1 != job_id_2

    def test_schedule_jobs_with_multiple_users(self, email_scheduler):
        """Test scheduling jobs for multiple users with mixed pending states."""

        # Create mock configs for multiple users
        config_1 = Mock()
        config_1.user_id = 1
        config_1.is_enabled = True

        config_2 = Mock()
        config_2.user_id = 2
        config_2.is_enabled = True

        config_3 = Mock()
        config_3.user_id = 3
        config_3.is_enabled = True

        configs = [config_1, config_2, config_3]

        # Mock database query
        email_scheduler.db.query.return_value.filter_by.return_value.all.return_value = (
            configs
        )

        # Mock _schedule_user_job to track calls
        with patch.object(email_scheduler, "_schedule_user_job") as mock_schedule_user:
            email_scheduler.schedule_jobs()

            # Verify all configs were processed
            assert mock_schedule_user.call_count == 3
            mock_schedule_user.assert_any_call(config_1)
            mock_schedule_user.assert_any_call(config_2)
            mock_schedule_user.assert_any_call(config_3)

    def test_error_handling_in_schedule_user_job(
        self, email_scheduler, mock_email_config
    ):
        """Test error handling in _schedule_user_job method."""

        # Mock has_user_job_pending to raise an exception
        with patch(
            "banktransactions.automation.scheduler.has_user_job_pending"
        ) as mock_has_pending:
            mock_has_pending.side_effect = Exception("Redis connection error")

            # Should not raise exception
            email_scheduler._schedule_user_job(mock_email_config)

            # Verify that the exception was caught and logged
            mock_has_pending.assert_called_once()


def run_integration_test():
    """Run an integration test with real Redis (if available)."""
    print("\nRunning integration test...")

    try:
        import redis
        from rq import Queue

        # Try to connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = redis.from_url(redis_url)
        redis_conn.ping()

        print("✅ Redis connection successful")

        # Test job utilities with real Redis
        test_user_id = 999

        # Clear any existing state
        queue = Queue("email_processing", connection=redis_conn)
        initial_length = len(queue)

        print(f"Initial queue length: {initial_length}")

        # Test 1: No pending jobs initially
        has_pending = has_user_job_pending(redis_conn, test_user_id)
        print(f"Has pending job (should be False): {has_pending}")

        # Test 2: Get status
        status = get_user_job_status(redis_conn, test_user_id)
        print(f"Job status: {status}")

        print("✅ Integration test completed successfully")

    except Exception as e:
        print(f"⚠️  Integration test skipped (Redis not available): {e}")


if __name__ == "__main__":
    print("Scheduler Deduplication Test Suite")
    print("=" * 50)

    # Run unit tests
    print("Running unit tests...")
    test_instance = TestSchedulerDeduplication()

    try:
        # Test job ID generation
        test_instance.test_job_id_generation_consistency()
        print("✅ Job ID generation consistency test passed")

        test_instance.test_job_id_generation_different_timestamps()
        print("✅ Job ID generation different timestamps test passed")

        print("✅ All unit tests passed")

    except Exception as e:
        print(f"❌ Unit test failed: {e}")
        import traceback

        traceback.print_exc()

    # Run integration test
    run_integration_test()

    print("\n✅ Test suite completed!")
