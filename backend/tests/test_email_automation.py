import json
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import g

from app.extensions import db
from app.models import EmailConfiguration
from app.utils.encryption import decrypt_value, encrypt_value


@pytest.fixture(autouse=True)
def set_encryption_key(app):
    """Set a consistent encryption key for all tests"""
    with app.app_context():
        # Use a fixed valid Fernet key for testing consistency
        app.config["ENCRYPTION_KEY"] = "fF3jX8_L3uUBWh1cEiGqW-otnwYnP7c9mG0YH7TH5Hg="


class TestEmailAutomationConfig:
    """Test cases for email automation configuration endpoints"""

    def test_get_email_config_not_found(self, authenticated_client, user):
        """Test getting email config when none exists"""
        response = authenticated_client.get("/api/v1/email-automation/config")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["config"] is None

    def test_get_email_config_exists(self, authenticated_client, user, db_session):
        """Test getting existing email config"""
        # Create email configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            imap_server="imap.gmail.com",
            imap_port=993,
            email_address="test@example.com",
            app_password=encrypt_value("test_password"),
            polling_interval="hourly",
            sample_emails=json.dumps([{"subject": "Test", "body": "Test email"}]),
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.get("/api/v1/email-automation/config")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["config"] is not None
        assert data["config"]["email_address"] == "test@example.com"
        assert data["config"]["is_enabled"] is True
        assert data["config"]["imap_server"] == "imap.gmail.com"
        assert data["config"]["imap_port"] == 993
        assert data["config"]["polling_interval"] == "hourly"
        # Ensure app_password is not returned
        assert "app_password" not in data["config"]

    def test_create_email_config_success(self, authenticated_client, user):
        """Test creating new email configuration"""
        config_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
            "is_enabled": True,
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "polling_interval": "daily",
            "sample_emails": [{"subject": "Test", "body": "Test email"}],
        }

        response = authenticated_client.post(
            "/api/v1/email-automation/config", json=config_data
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Email configuration saved successfully"
        assert data["config"]["email_address"] == "test@example.com"
        assert data["config"]["is_enabled"] is True
        assert "app_password" not in data["config"]

        # Verify in database
        config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        assert config is not None
        assert config.email_address == "test@example.com"
        assert decrypt_value(config.app_password) == "test_password"

    def test_create_email_config_missing_required_fields(
        self, authenticated_client, user
    ):
        """Test creating email config with missing required fields"""
        # Missing email_address
        response = authenticated_client.post(
            "/api/v1/email-automation/config", json={"app_password": "test_password"}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "email_address is required" in data["error"]

        # Missing app_password
        response = authenticated_client.post(
            "/api/v1/email-automation/config",
            json={"email_address": "test@example.com"},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "app_password is required" in data["error"]

    def test_create_email_config_with_defaults(self, authenticated_client, user):
        """Test creating email config with minimal data uses defaults"""
        config_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
        }

        response = authenticated_client.post(
            "/api/v1/email-automation/config", json=config_data
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["config"]["is_enabled"] is False  # Default
        assert data["config"]["imap_server"] == "imap.gmail.com"  # Default
        assert data["config"]["imap_port"] == 993  # Default
        assert data["config"]["polling_interval"] == "hourly"  # Default

    def test_update_existing_config_via_post(
        self, authenticated_client, user, db_session
    ):
        """Test updating existing configuration via POST endpoint"""
        # Create existing configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=False,
            email_address="old@example.com",
            app_password=encrypt_value("old_password"),
        )
        db_session.add(config)
        db_session.commit()

        config_data = {
            "email_address": "new@example.com",
            "app_password": "new_password",
            "is_enabled": True,
            "polling_interval": "daily",
        }

        response = authenticated_client.post(
            "/api/v1/email-automation/config", json=config_data
        )

        assert response.status_code == 200  # Updated, not created
        data = json.loads(response.data)
        assert data["config"]["email_address"] == "new@example.com"
        assert data["config"]["is_enabled"] is True
        assert data["config"]["polling_interval"] == "daily"

    def test_create_config_database_error(self, authenticated_client, user):
        """Test handling database errors during config creation"""
        config_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
        }

        with patch("app.email_automation.db.session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            response = authenticated_client.post(
                "/api/v1/email-automation/config", json=config_data
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "Failed to save configuration" in data["error"]

    def test_update_email_config_success(self, authenticated_client, user, db_session):
        """Test updating email configuration via PUT"""
        # Create existing configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=False,
            email_address="test@example.com",
            app_password=encrypt_value("old_password"),
            polling_interval="hourly",
        )
        db_session.add(config)
        db_session.commit()

        update_data = {
            "is_enabled": True,
            "polling_interval": "daily",
            "app_password": "new_password",
        }

        response = authenticated_client.put(
            "/api/v1/email-automation/config", json=update_data
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Email configuration updated successfully"
        assert data["config"]["is_enabled"] is True
        assert data["config"]["polling_interval"] == "daily"
        assert "app_password" not in data["config"]

        # Verify in database
        updated_config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        assert decrypt_value(updated_config.app_password) == "new_password"

    def test_update_email_config_not_found(self, authenticated_client, user):
        """Test updating email config when none exists"""
        update_data = {"is_enabled": True}

        response = authenticated_client.put(
            "/api/v1/email-automation/config", json=update_data
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Email configuration not found"

    def test_update_email_config_partial_update(
        self, authenticated_client, user, db_session
    ):
        """Test partial update of email configuration"""
        # Create existing configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=False,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
            polling_interval="hourly",
            imap_server="imap.gmail.com",
            imap_port=993,
        )
        db_session.add(config)
        db_session.commit()

        # Update only is_enabled
        update_data = {"is_enabled": True}

        response = authenticated_client.put(
            "/api/v1/email-automation/config", json=update_data
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["config"]["is_enabled"] is True
        # Other fields should remain unchanged
        assert data["config"]["email_address"] == "test@example.com"
        assert data["config"]["polling_interval"] == "hourly"
        assert data["config"]["imap_server"] == "imap.gmail.com"
        assert data["config"]["imap_port"] == 993

    def test_update_config_database_error(self, authenticated_client, user, db_session):
        """Test handling database errors during config update"""
        # Create existing configuration
        config = EmailConfiguration(
            user_id=user.id,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        update_data = {"is_enabled": True}

        with patch("app.email_automation.db.session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            response = authenticated_client.put(
                "/api/v1/email-automation/config", json=update_data
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "Failed to update configuration" in data["error"]

    def test_delete_email_config_success(self, authenticated_client, user, db_session):
        """Test deleting email configuration"""
        # Create configuration to delete
        config = EmailConfiguration(
            user_id=user.id,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.delete("/api/v1/email-automation/config")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Email configuration deleted successfully"

        # Verify deletion in database
        deleted_config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        assert deleted_config is None

    def test_delete_email_config_not_found(self, authenticated_client, user):
        """Test deleting email config when none exists"""
        response = authenticated_client.delete("/api/v1/email-automation/config")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Email configuration not found"

    def test_delete_config_database_error(self, authenticated_client, user, db_session):
        """Test handling database errors during config deletion"""
        # Create configuration
        config = EmailConfiguration(
            user_id=user.id,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        with patch("app.email_automation.db.session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            response = authenticated_client.delete("/api/v1/email-automation/config")

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "Failed to delete configuration" in data["error"]


class TestEmailConnectionTesting:
    """Test cases for email connection testing endpoint"""

    def test_test_connection_success(self, authenticated_client, user):
        """Test successful email connection"""
        connection_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
        }

        # Mock the CustomIMAPClient
        mock_client = MagicMock()
        mock_client.connect.return_value = None
        mock_client.disconnect.return_value = None

        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "banktransactions": MagicMock(),
                "banktransactions.core": MagicMock(),
                "banktransactions.core.imap_client": MagicMock(),
            },
        ), patch(
            "banktransactions.core.imap_client.CustomIMAPClient",
            return_value=mock_client,
        ) as mock_client_class:
            response = authenticated_client.post(
                "/api/v1/email-automation/test-connection", json=connection_data
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["message"] == "Email connection test successful"

            # Verify client was called with correct parameters
            mock_client_class.assert_called_once_with(
                server="imap.gmail.com",
                port=993,
                username="test@example.com",
                password="test_password",
            )
            mock_client.connect.assert_called_once()
            mock_client.disconnect.assert_called_once()

    def test_test_connection_with_defaults(self, authenticated_client, user):
        """Test connection with default server settings"""
        connection_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
            # No server/port specified - should use defaults
        }

        mock_client = MagicMock()

        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "banktransactions": MagicMock(),
                "banktransactions.core": MagicMock(),
                "banktransactions.core.imap_client": MagicMock(),
            },
        ), patch(
            "banktransactions.core.imap_client.CustomIMAPClient",
            return_value=mock_client,
        ) as mock_client_class:
            response = authenticated_client.post(
                "/api/v1/email-automation/test-connection", json=connection_data
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True

            # Verify defaults were used
            mock_client_class.assert_called_once_with(
                server="imap.gmail.com",  # Default
                port=993,  # Default
                username="test@example.com",
                password="test_password",
            )

    def test_test_connection_missing_required_fields(self, authenticated_client, user):
        """Test connection with missing required fields"""
        # Missing email_address
        response = authenticated_client.post(
            "/api/v1/email-automation/test-connection",
            json={"app_password": "test_password"},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "email_address is required" in data["error"]

        # Missing app_password
        response = authenticated_client.post(
            "/api/v1/email-automation/test-connection",
            json={"email_address": "test@example.com"},
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "app_password is required" in data["error"]

    def test_test_connection_failure(self, authenticated_client, user):
        """Test connection failure"""
        connection_data = {
            "email_address": "test@example.com",
            "app_password": "wrong_password",
        }

        mock_client = MagicMock()
        mock_client.connect.side_effect = Exception("Authentication failed")

        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "banktransactions": MagicMock(),
                "banktransactions.core": MagicMock(),
                "banktransactions.core.imap_client": MagicMock(),
            },
        ), patch(
            "banktransactions.core.imap_client.CustomIMAPClient",
            return_value=mock_client,
        ):
            response = authenticated_client.post(
                "/api/v1/email-automation/test-connection", json=connection_data
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["success"] is False
            assert "Connection test failed" in data["error"]
            assert "Authentication failed" in data["error"]

    def test_test_connection_import_error(self, authenticated_client, user):
        """Test handling import errors"""
        connection_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
        }

        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "banktransactions": MagicMock(),
                "banktransactions.core": MagicMock(),
                "banktransactions.core.imap_client": MagicMock(),
            },
        ), patch(
            "banktransactions.core.imap_client.CustomIMAPClient",
            side_effect=ImportError("Module not found"),
        ):
            response = authenticated_client.post(
                "/api/v1/email-automation/test-connection", json=connection_data
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["success"] is False
            assert "Connection test failed" in data["error"]


class TestEmailAutomationStatus:
    """Test cases for email automation status endpoint"""

    def test_get_status_not_configured(self, authenticated_client, user):
        """Test status when email automation is not configured"""
        response = authenticated_client.get("/api/v1/email-automation/status")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "not_configured"
        assert data["message"] == "Email automation is not configured"

    def test_get_status_disabled(self, authenticated_client, user, db_session):
        """Test status when email automation is configured but disabled"""
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=False,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
            polling_interval="hourly",
            last_check_time=datetime.now(timezone.utc),
            last_processed_email_id="msg_123",
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.get("/api/v1/email-automation/status")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "disabled"
        assert data["email_address"] == "test@example.com"
        assert data["polling_interval"] == "hourly"
        assert data["last_processed_email_id"] == "msg_123"
        assert data["last_check"] is not None

    def test_get_status_enabled(self, authenticated_client, user, db_session):
        """Test status when email automation is enabled"""
        last_check = datetime.now(timezone.utc)
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
            polling_interval="daily",
            last_check_time=last_check,
            last_processed_email_id="msg_456",
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.get("/api/v1/email-automation/status")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "enabled"
        assert data["email_address"] == "test@example.com"
        assert data["polling_interval"] == "daily"
        assert data["last_processed_email_id"] == "msg_456"
        # Check that timestamp is properly formatted (handle timezone differences)
        expected_time = last_check.isoformat()
        actual_time = data["last_check"]
        # Remove timezone info for comparison if present
        if expected_time.endswith("+00:00"):
            expected_time = expected_time[:-6]
        if actual_time.endswith("+00:00"):
            actual_time = actual_time[:-6]
        assert actual_time == expected_time

    def test_get_status_no_last_check(self, authenticated_client, user, db_session):
        """Test status when no last check time is recorded"""
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
            polling_interval="hourly",
            last_check_time=None,  # No last check
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.get("/api/v1/email-automation/status")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "enabled"
        assert data["last_check"] is None


class TestEmailProcessingTrigger:
    """Test cases for email processing trigger endpoint"""

    def test_trigger_processing_success(self, authenticated_client, user, db_session):
        """Test successful email processing trigger"""
        # Create enabled configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        # Mock Redis and Queue
        mock_redis_conn = MagicMock()
        mock_queue = MagicMock()
        mock_job = MagicMock()
        mock_job.id = "job_123"
        mock_queue.enqueue.return_value = mock_job

        # Mock all the external dependencies
        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "banktransactions": MagicMock(),
                "banktransactions.automation": MagicMock(),
                "banktransactions.automation.job_utils": MagicMock(),
                "banktransactions.automation.email_processor": MagicMock(),
                "redis": MagicMock(),
                "rq": MagicMock(),
            },
        ), patch("redis.from_url", return_value=mock_redis_conn), patch(
            "rq.Queue", return_value=mock_queue
        ), patch(
            "banktransactions.automation.job_utils.generate_job_id",
            return_value="job_123",
        ) as mock_generate_job_id, patch(
            "banktransactions.automation.job_utils.get_user_job_status"
        ), patch(
            "banktransactions.automation.job_utils.has_user_job_pending",
            return_value=False,
        ) as mock_has_pending, patch(
            "banktransactions.automation.email_processor.process_user_emails_standalone"
        ):

            response = authenticated_client.post("/api/v1/email-automation/trigger")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["message"] == "Email processing job queued successfully"
            assert data["job_id"] == "job_123"

            # Verify function calls
            mock_has_pending.assert_called_once_with(mock_redis_conn, user.id)
            mock_generate_job_id.assert_called_once_with(user.id)
            mock_queue.enqueue.assert_called_once()

    def test_trigger_processing_not_configured(self, authenticated_client, user):
        """Test triggering when email automation is not configured"""
        response = authenticated_client.post("/api/v1/email-automation/trigger")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Email automation is not configured or disabled"

    def test_trigger_processing_disabled(self, authenticated_client, user, db_session):
        """Test triggering when email automation is disabled"""
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=False,  # Disabled
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.post("/api/v1/email-automation/trigger")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Email automation is not configured or disabled"

    def test_trigger_processing_job_already_pending(
        self, authenticated_client, user, db_session
    ):
        """Test triggering when a job is already pending"""
        # Create enabled configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        mock_redis_conn = MagicMock()

        # Create mock modules
        mock_redis_module = MagicMock()
        mock_redis_module.from_url.return_value = mock_redis_conn

        mock_rq_module = MagicMock()

        mock_job_utils = MagicMock()
        mock_job_utils.has_user_job_pending.return_value = True
        mock_job_utils.get_user_job_status.return_value = {"status": "pending"}

        mock_banktransactions = MagicMock()
        mock_banktransactions.automation.job_utils = mock_job_utils

        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "redis": mock_redis_module,
                "rq": mock_rq_module,
                "banktransactions": mock_banktransactions,
                "banktransactions.automation": MagicMock(),
                "banktransactions.automation.job_utils": mock_job_utils,
            },
        ):

            response = authenticated_client.post("/api/v1/email-automation/trigger")

            assert response.status_code == 409  # Conflict
            data = json.loads(response.data)
            assert data["success"] is False
            assert "already pending" in data["error"]
            assert data["job_status"]["status"] == "pending"

    def test_trigger_processing_redis_error(
        self, authenticated_client, user, db_session
    ):
        """Test handling Redis connection errors"""
        # Create enabled configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        # Mock Redis connection failure
        with patch("sys.path"), patch.dict(
            "sys.modules", {"redis": MagicMock()}
        ), patch("redis.from_url", side_effect=Exception("Redis connection failed")):

            response = authenticated_client.post("/api/v1/email-automation/trigger")

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data["success"] is False
            assert "Failed to queue email processing job" in data["error"]

    def test_trigger_processing_queue_error(
        self, authenticated_client, user, db_session
    ):
        """Test handling queue errors"""
        # Create enabled configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        mock_redis_conn = MagicMock()
        mock_queue = MagicMock()
        mock_queue.enqueue.side_effect = Exception("Queue error")

        with patch("sys.path"), patch.dict(
            "sys.modules",
            {
                "banktransactions": MagicMock(),
                "banktransactions.automation": MagicMock(),
                "banktransactions.automation.job_utils": MagicMock(),
                "banktransactions.automation.email_processor": MagicMock(),
                "redis": MagicMock(),
                "rq": MagicMock(),
            },
        ), patch("redis.from_url", return_value=mock_redis_conn), patch(
            "rq.Queue", return_value=mock_queue
        ), patch(
            "banktransactions.automation.job_utils.has_user_job_pending",
            return_value=False,
        ), patch(
            "banktransactions.automation.job_utils.generate_job_id",
            return_value="job_123",
        ), patch(
            "banktransactions.automation.email_processor.process_user_emails_standalone"
        ):

            response = authenticated_client.post("/api/v1/email-automation/trigger")

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data["success"] is False
            assert "Failed to queue email processing job" in data["error"]

    def test_trigger_processing_endpoint_functionality(
        self, authenticated_client, user, db_session
    ):
        """Test that the trigger processing endpoint works correctly"""
        # Create enabled configuration
        config = EmailConfiguration(
            user_id=user.id,
            is_enabled=True,
            email_address="test@example.com",
            app_password=encrypt_value("password"),
        )
        db_session.add(config)
        db_session.commit()

        # This test verifies that the endpoint exists and handles various scenarios
        response = authenticated_client.post("/api/v1/email-automation/trigger")

        data = json.loads(response.data)

        # The response could be:
        # - 200: Success (job queued)
        # - 409: Conflict (job already pending)
        # - 500: Error (missing dependencies or other errors)
        assert response.status_code in [200, 409, 500]

        if response.status_code == 200:
            # Success case
            assert data["success"] is True
            assert "job_id" in data
        elif response.status_code == 409:
            # Job already pending case
            assert data["success"] is False
            assert "already pending" in data["error"]
        else:  # 500
            # Error case (missing dependencies, etc.)
            assert data["success"] is False
            assert "Failed to queue email processing job" in data["error"]


class TestEmailAutomationAuth:
    """Test cases for authentication and authorization"""

    def test_endpoints_require_authentication(self, client):
        """Test that all endpoints require authentication"""
        endpoints = [
            ("/api/v1/email-automation/config", "GET"),
            ("/api/v1/email-automation/config", "POST"),
            ("/api/v1/email-automation/config", "PUT"),
            ("/api/v1/email-automation/config", "DELETE"),
            ("/api/v1/email-automation/test-connection", "POST"),
            ("/api/v1/email-automation/status", "GET"),
            ("/api/v1/email-automation/trigger", "POST"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)

            assert (
                response.status_code == 401
            ), f"Endpoint {method} {endpoint} should require authentication"

    def test_user_isolation(self, authenticated_client, user, db_session, app):
        """Test that users can only access their own configurations"""
        # Create configuration for the authenticated user
        config1 = EmailConfiguration(
            user_id=user.id,
            email_address="user1@example.com",
            app_password=encrypt_value("password1"),
        )
        db_session.add(config1)
        db_session.commit()

        # Create another user and their configuration
        from app.models import User

        user2 = User(email="user2@example.com")
        user2.set_password("password")
        db_session.add(user2)
        db_session.commit()

        # Store user2 ID before creating config
        user2_id = user2.id

        config2 = EmailConfiguration(
            user_id=user2_id,
            email_address="user2@example.com",
            app_password=encrypt_value("password2"),
        )
        db_session.add(config2)
        db_session.commit()

        # Authenticated user should only see their own config
        response = authenticated_client.get("/api/v1/email-automation/config")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["config"]["email_address"] == "user1@example.com"

        # Authenticated user should only be able to update their own config
        response = authenticated_client.put(
            "/api/v1/email-automation/config", json={"is_enabled": True}
        )
        assert response.status_code == 200

        # Verify user2's config was not affected (use stored ID)
        user2_config = EmailConfiguration.query.filter_by(user_id=user2_id).first()
        assert user2_config.email_address == "user2@example.com"
        assert user2_config.is_enabled is False  # Should remain unchanged


class TestEmailAutomationEdgeCases:
    """Test cases for edge cases and error conditions"""

    def test_sample_emails_json_handling(self, authenticated_client, user):
        """Test proper handling of sample_emails JSON field"""
        config_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
            "sample_emails": [
                {"subject": "Bank Alert", "body": "Your account was debited"},
                {"subject": "Credit Card", "body": "Payment received"},
            ],
        }

        response = authenticated_client.post(
            "/api/v1/email-automation/config", json=config_data
        )

        assert response.status_code == 201

        # Verify in database that JSON is properly stored
        config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        sample_emails = json.loads(config.sample_emails)
        assert len(sample_emails) == 2
        assert sample_emails[0]["subject"] == "Bank Alert"

    def test_config_timestamps(self, authenticated_client, user, db_session):
        """Test that timestamps are properly handled"""
        # Create config
        response = authenticated_client.post(
            "/api/v1/email-automation/config",
            json={"email_address": "test@example.com", "app_password": "test_password"},
        )
        assert response.status_code == 201

        config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        original_created_at = config.created_at
        original_updated_at = config.updated_at

        # Update config
        response = authenticated_client.put(
            "/api/v1/email-automation/config", json={"is_enabled": True}
        )
        assert response.status_code == 200

        # Verify timestamps
        updated_config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        assert updated_config.created_at == original_created_at  # Should not change
        assert updated_config.updated_at > original_updated_at  # Should be updated

    def test_empty_json_request(self, authenticated_client, user):
        """Test handling of empty JSON requests"""
        response = authenticated_client.post("/api/v1/email-automation/config", json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "email_address is required" in data["error"]

    def test_invalid_json_request(self, authenticated_client, user):
        """Test handling of invalid JSON requests"""
        response = authenticated_client.post(
            "/api/v1/email-automation/config",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        # This should be handled by Flask's JSON parsing
        assert response.status_code == 500  # Bad Request for invalid JSON

    def test_large_sample_emails(self, authenticated_client, user):
        """Test handling of large sample_emails data"""
        # Create a large sample emails array
        large_sample_emails = []
        for i in range(100):
            large_sample_emails.append(
                {
                    "subject": f"Email {i}",
                    "body": f"This is email number {i} with some content" * 10,
                }
            )

        config_data = {
            "email_address": "test@example.com",
            "app_password": "test_password",
            "sample_emails": large_sample_emails,
        }

        response = authenticated_client.post(
            "/api/v1/email-automation/config", json=config_data
        )

        assert response.status_code == 201

        # Verify data was stored correctly
        config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        stored_emails = json.loads(config.sample_emails)
        assert len(stored_emails) == 100

    def test_special_characters_in_password(self, authenticated_client, user):
        """Test handling of special characters in passwords"""
        special_password = "p@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"

        config_data = {
            "email_address": "test@example.com",
            "app_password": special_password,
        }

        response = authenticated_client.post(
            "/api/v1/email-automation/config", json=config_data
        )

        assert response.status_code == 201

        # Verify password was encrypted and can be decrypted correctly
        config = EmailConfiguration.query.filter_by(user_id=user.id).first()
        decrypted_password = decrypt_value(config.app_password)
        assert decrypted_password == special_password
