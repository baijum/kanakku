import pytest
from flask import current_app
from unittest.mock import patch, MagicMock
import json
from app.utils.logging_utils import (
    log_request,
    log_response,
    log_function_call,
    log_error,
    log_db_error,
)
from app.utils.email_utils import send_password_reset_email
from app.models import User


class TestLoggingUtils:
    @pytest.fixture(autouse=True)
    def setup_app_context(self, app):
        """Setup app context for all tests in this class"""
        with app.app_context():
            yield  # This will run the test and then tear down

    def test_log_request(self, app, monkeypatch):
        # Setup a test client and context
        with app.test_request_context(
            "/api/test",
            json={"username": "test", "password": "secret"},
            headers={"Authorization": "Bearer token123"},
        ):
            # Mock the logger
            mock_logger = MagicMock()
            monkeypatch.setattr(current_app, "logger", mock_logger)

            # Test with default settings
            log_request()
            mock_logger.info.assert_called_once()
            log_data = json.loads(
                mock_logger.info.call_args[0][0].replace("Request: ", "")
            )
            assert log_data["method"] == "GET"
            assert log_data["path"] == "/api/test"
            assert "headers" not in log_data
            assert "body" not in log_data

            # Reset mock
            mock_logger.reset_mock()

            # Test with headers and body
            log_request(
                include_headers=True,
                include_body=True,
                sanitize_fields=["password"],
            )
            mock_logger.info.assert_called_once()
            log_data = json.loads(
                mock_logger.info.call_args[0][0].replace("Request: ", "")
            )
            assert "headers" in log_data
            assert log_data["headers"]["Authorization"] == "[REDACTED]"
            assert "body" in log_data
            assert log_data["body"]["username"] == "test"
            assert log_data["body"]["password"] == "[REDACTED]"

    def test_log_response(self, app, monkeypatch):
        # Setup a test client and context
        with app.test_request_context("/api/test"):
            # Create a mock response
            response = MagicMock()
            response.status_code = 200
            response.is_json = True
            response.get_data.return_value = json.dumps(
                {"status": "success", "data": "test"}
            )

            # Mock the logger
            mock_logger = MagicMock()
            monkeypatch.setattr(current_app, "logger", mock_logger)

            # Test without body
            result = log_response(response)
            mock_logger.info.assert_called_once()
            log_data = json.loads(
                mock_logger.info.call_args[0][0].replace("Response: ", "")
            )
            assert log_data["status_code"] == 200
            assert log_data["path"] == "/api/test"
            assert "body" not in log_data
            assert result == response  # Should return the response untouched

            # Reset mock
            mock_logger.reset_mock()

            # Test with body
            log_response(response, include_body=True)
            mock_logger.info.assert_called_once()
            log_data = json.loads(
                mock_logger.info.call_args[0][0].replace("Response: ", "")
            )
            assert "body" in log_data
            assert log_data["body"]["status"] == "success"

    def test_log_function_call(self, app, monkeypatch):
        # Mock the logger
        mock_logger = MagicMock()

        # Create a test function
        with app.app_context():
            monkeypatch.setattr(current_app, "logger", mock_logger)

            # Test without log_args
            @log_function_call
            def test_func():
                return "result"

            result = test_func()
            assert result == "result"
            assert mock_logger.debug.call_count == 2  # Entry and exit logs

            # Reset mock
            mock_logger.reset_mock()

            # Test with log_args and sensitive data
            @log_function_call(log_args=True)
            def test_func_with_args(arg1, password=None):
                return arg1

            result = test_func_with_args("test", password="secret")
            assert result == "test"
            assert mock_logger.debug.call_count == 2
            # Check that password was redacted
            assert "[REDACTED]" in mock_logger.debug.call_args_list[0][0][0]
            assert "secret" not in mock_logger.debug.call_args_list[0][0][0]

            # Reset mock
            mock_logger.reset_mock()

            # Test with exception
            @log_function_call
            def test_func_with_exception():
                raise ValueError("Test error")

            with pytest.raises(ValueError):
                test_func_with_exception()

            assert mock_logger.debug.call_count == 1  # Only entry log
            assert mock_logger.error.call_count == 1  # Error log

    def test_log_error(self, app, monkeypatch):
        # Mock the logger
        mock_logger = MagicMock()

        with app.app_context():
            monkeypatch.setattr(current_app, "logger", mock_logger)

            # Create a test error
            error = ValueError("Test error")

            # Test with default settings
            log_error(error)
            mock_logger.error.assert_called_once()
            assert "ValueError: Test error" in mock_logger.error.call_args[0][0]
            assert mock_logger.error.call_args[1]["exc_info"] is True

            # Reset mock
            mock_logger.reset_mock()

            # Test with different level
            log_error(error, level="warning")
            mock_logger.warning.assert_called_once()

            # Reset mock
            mock_logger.reset_mock()

            # Test without traceback
            log_error(error, include_traceback=False)
            mock_logger.error.assert_called_once()
            assert "exc_info" not in mock_logger.error.call_args[1]

    def test_log_db_error(self, app, monkeypatch):
        # Mock the logger
        mock_logger = MagicMock()

        with app.app_context():
            monkeypatch.setattr(current_app, "logger", mock_logger)

            # Create a test error
            error = Exception("Database connection failed")

            # Test with minimal context
            log_db_error(error)
            mock_logger.error.assert_called_once()
            assert "Database error" in mock_logger.error.call_args[0][0]

            # Reset mock
            mock_logger.reset_mock()

            # Test with operation and model
            log_db_error(error, operation="update", model="User")
            mock_logger.error.assert_called_once()
            assert "during update on User" in mock_logger.error.call_args[0][0]


class TestEmailUtils:
    @pytest.fixture(autouse=True)
    def setup_app_context(self, app):
        """Setup app context for all tests in this class"""
        with app.app_context():
            yield  # This will run the test and then tear down

    @patch("app.utils.email_utils.mail")
    def test_send_password_reset_email(self, mock_mail, app, monkeypatch):
        # Mock the logger
        mock_logger = MagicMock()
        monkeypatch.setattr(current_app, "logger", mock_logger)

        # Set FRONTEND_URL directly in app config rather than using current_app.config
        frontend_url = "http://localhost:5173"
        app.config["FRONTEND_URL"] = frontend_url

        # Create a test user
        user = MagicMock(spec=User)
        user.email = "test@example.com"

        # Create a token
        token = "test_token_12345"

        # Test successful email
        result = send_password_reset_email(user, token)

        # Verify mail.send was called
        mock_mail.send.assert_called_once()

        # Verify the message was constructed correctly
        message = mock_mail.send.call_args[0][0]
        assert message.subject == "Reset Your Kanakku Password"
        assert message.recipients == ["test@example.com"]
        assert "Reset Password" in message.html
        assert f"{frontend_url}/reset-password/{token}" in message.html

        # Verify success was logged
        assert mock_logger.info.call_count == 2
        assert (
            "Sending password reset email" in mock_logger.info.call_args_list[0][0][0]
        )
        assert (
            "Password reset email sent successfully"
            in mock_logger.info.call_args_list[1][0][0]
        )

        # Verify result
        assert result is True

        # Test with exception
        mock_mail.send.side_effect = Exception("SMTP error")
        mock_logger.reset_mock()

        with pytest.raises(Exception):
            send_password_reset_email(user, token)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert (
            "Failed to send password reset email" in mock_logger.error.call_args[0][0]
        )
