#!/usr/bin/env python3

import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy.orm import Session

# Add banktransactions directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from banktransactions.email_automation.workers.scheduler import EmailScheduler


class TestEmailScheduler:
    """Test cases for the EmailScheduler class."""

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

    @pytest.fixture
    def mock_email_configs(self):
        """Create mock EmailConfiguration objects."""
        configs = []
        
        # Config 1: Hourly polling, last checked 2 hours ago
        config1 = Mock()
        config1.user_id = 1
        config1.is_enabled = True
        config1.polling_interval = "hourly"
        config1.last_check_time = datetime.utcnow() - timedelta(hours=2)
        configs.append(config1)
        
        # Config 2: Daily polling, last checked 2 days ago
        config2 = Mock()
        config2.user_id = 2
        config2.is_enabled = True
        config2.polling_interval = "daily"
        config2.last_check_time = datetime.utcnow() - timedelta(days=2)
        configs.append(config2)
        
        # Config 3: Never checked before
        config3 = Mock()
        config3.user_id = 3
        config3.is_enabled = True
        config3.polling_interval = "hourly"
        config3.last_check_time = None
        configs.append(config3)
        
        return configs

    def test_scheduler_initialization(self, mock_redis_conn, mock_db_session):
        """Test EmailScheduler initialization."""
        scheduler = EmailScheduler(mock_redis_conn, mock_db_session)
        
        assert scheduler.db == mock_db_session
        assert scheduler.scheduler is not None

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_schedule_jobs_success(self, mock_scheduler_class, email_scheduler, mock_email_configs):
        """Test successful scheduling of jobs for all enabled configurations."""
        # Mock the scheduler
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        # Mock database query
        email_scheduler.db.query.return_value.filter_by.return_value.all.return_value = mock_email_configs
        
        # Mock _schedule_user_job method
        with patch.object(email_scheduler, '_schedule_user_job') as mock_schedule_user:
            email_scheduler.schedule_jobs()
        
        # Verify all configs were processed
        assert mock_schedule_user.call_count == 3
        mock_schedule_user.assert_any_call(mock_email_configs[0])
        mock_schedule_user.assert_any_call(mock_email_configs[1])
        mock_schedule_user.assert_any_call(mock_email_configs[2])

    def test_schedule_jobs_no_configs(self, email_scheduler):
        """Test scheduling when no enabled configurations exist."""
        # Mock database query to return empty list
        email_scheduler.db.query.return_value.filter_by.return_value.all.return_value = []
        
        with patch.object(email_scheduler, '_schedule_user_job') as mock_schedule_user:
            email_scheduler.schedule_jobs()
        
        # Verify no jobs were scheduled
        mock_schedule_user.assert_not_called()

    def test_schedule_jobs_exception_handling(self, email_scheduler):
        """Test exception handling in schedule_jobs."""
        # Mock database query to raise exception
        email_scheduler.db.query.side_effect = Exception("Database error")
        
        # Should not raise exception
        email_scheduler.schedule_jobs()

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_schedule_user_job_hourly_overdue(self, mock_scheduler_class, email_scheduler):
        """Test scheduling a job for hourly polling that's overdue."""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        # Create config that's overdue for hourly check
        config = Mock()
        config.user_id = 1
        config.polling_interval = "hourly"
        config.last_check_time = datetime.utcnow() - timedelta(hours=2)
        
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = datetime.utcnow()
            email_scheduler._schedule_user_job(config)
        
        # Verify job was scheduled
        mock_scheduler.enqueue_at.assert_called_once()
        call_args = mock_scheduler.enqueue_at.call_args
        assert call_args[1]["queue_name"] == "email_processing"

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_schedule_user_job_daily_overdue(self, mock_scheduler_class, email_scheduler):
        """Test scheduling a job for daily polling that's overdue."""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        # Create config that's overdue for daily check
        config = Mock()
        config.user_id = 2
        config.polling_interval = "daily"
        config.last_check_time = datetime.utcnow() - timedelta(days=2)
        
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = datetime.utcnow()
            email_scheduler._schedule_user_job(config)
        
        # Verify job was scheduled
        mock_scheduler.enqueue_at.assert_called_once()

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_schedule_user_job_no_next_run(self, mock_scheduler_class, email_scheduler):
        """Test scheduling when _calculate_next_run returns None."""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        config = Mock()
        config.user_id = 1
        
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = None
            email_scheduler._schedule_user_job(config)
        
        # Verify no job was scheduled
        mock_scheduler.enqueue_at.assert_not_called()

    def test_schedule_user_job_exception_handling(self, email_scheduler):
        """Test exception handling in _schedule_user_job."""
        config = Mock()
        config.user_id = 1
        
        # Mock _calculate_next_run to raise exception
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.side_effect = Exception("Calculation error")
            
            # Should not raise exception
            email_scheduler._schedule_user_job(config)

    def test_calculate_next_run_hourly_overdue(self, email_scheduler):
        """Test calculating next run time for overdue hourly polling."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(hours=2)
        config.polling_interval = "hourly"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return current time since it's overdue
        assert result is not None
        assert abs((result - datetime.utcnow()).total_seconds()) < 60  # Within 1 minute

    def test_calculate_next_run_hourly_future(self, email_scheduler):
        """Test calculating next run time for hourly polling not yet due."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(minutes=30)
        config.polling_interval = "hourly"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return future time
        assert result is not None
        assert result > datetime.utcnow()

    def test_calculate_next_run_daily_overdue(self, email_scheduler):
        """Test calculating next run time for overdue daily polling."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(days=2)
        config.polling_interval = "daily"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return current time since it's overdue
        assert result is not None
        assert abs((result - datetime.utcnow()).total_seconds()) < 60  # Within 1 minute

    def test_calculate_next_run_daily_future(self, email_scheduler):
        """Test calculating next run time for daily polling not yet due."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(hours=12)
        config.polling_interval = "daily"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return future time
        assert result is not None
        assert result > datetime.utcnow()

    def test_calculate_next_run_no_last_check(self, email_scheduler):
        """Test calculating next run time when last_check_time is None."""
        config = Mock()
        config.last_check_time = None
        config.polling_interval = "hourly"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should return current time
        assert result is not None
        assert abs((result - datetime.utcnow()).total_seconds()) < 60  # Within 1 minute

    def test_calculate_next_run_unknown_interval(self, email_scheduler):
        """Test calculating next run time with unknown polling interval."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(hours=2)
        config.polling_interval = "unknown"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should default to hourly and return current time since overdue
        assert result is not None
        assert abs((result - datetime.utcnow()).total_seconds()) < 60  # Within 1 minute

    def test_calculate_next_run_case_insensitive(self, email_scheduler):
        """Test that polling interval comparison is case insensitive."""
        config = Mock()
        config.last_check_time = datetime.utcnow() - timedelta(hours=2)
        config.polling_interval = "HOURLY"
        
        result = email_scheduler._calculate_next_run(config)
        
        # Should handle uppercase interval
        assert result is not None

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_job_id_generation(self, mock_scheduler_class, email_scheduler):
        """Test that job IDs are generated correctly."""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        config = Mock()
        config.user_id = 123
        
        next_run = datetime.utcnow()
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = next_run
            email_scheduler._schedule_user_job(config)
        
        # Verify job ID format
        call_args = mock_scheduler.enqueue_at.call_args
        job_id = call_args[1]["job_id"]
        assert job_id.startswith("email_process_123_")
        assert str(next_run.timestamp()) in job_id

    @patch('banktransactions.email_automation.workers.scheduler.Scheduler')
    def test_function_reference_in_schedule(self, mock_scheduler_class, email_scheduler):
        """Test that the correct function is scheduled."""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        email_scheduler.scheduler = mock_scheduler
        
        config = Mock()
        config.user_id = 1
        
        with patch.object(email_scheduler, '_calculate_next_run') as mock_calc_next:
            mock_calc_next.return_value = datetime.utcnow()
            email_scheduler._schedule_user_job(config)
        
        # Verify the correct function and arguments are scheduled
        call_args = mock_scheduler.enqueue_at.call_args
        scheduled_function = call_args[0][1]  # Second positional argument
        user_id_arg = call_args[0][2]  # Third positional argument
        
        # Import the function to compare
        from banktransactions.email_automation.workers.email_processor import process_user_emails_standalone
        assert scheduled_function == process_user_emails_standalone
        assert user_id_arg == 1 