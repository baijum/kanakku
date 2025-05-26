"""
Unit tests for the unified service layer.

Tests the base service functionality, service result objects,
error handling, and logging.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from shared.services.auth import AuthService, UserManagementService
from shared.services.base import (
    BaseService,
    PermissionError,
    ServiceResult,
    StatelessService,
    log_service_call,
    require_user_context,
)
from shared.services.configuration import ConfigurationService
from shared.services.encryption import EncryptionService
from shared.services.transaction import TransactionService


class TestServiceResult:
    """Test ServiceResult class functionality."""

    def test_success_result_creation(self):
        """Test creating a successful result."""
        data = {"test": "value"}
        metadata = {"count": 1}
        result = ServiceResult.success_result(data=data, metadata=metadata)

        assert result.success is True
        assert result.data == data
        assert result.error is None
        assert result.error_code is None
        assert result.metadata == metadata
        assert isinstance(result.timestamp, datetime)

    def test_error_result_creation(self):
        """Test creating an error result."""
        error = "Test error"
        error_code = "TEST_ERROR"
        metadata = {"context": "test"}
        result = ServiceResult.error_result(
            error=error, error_code=error_code, metadata=metadata
        )

        assert result.success is False
        assert result.data is None
        assert result.error == error
        assert result.error_code == error_code
        assert result.metadata == metadata
        assert isinstance(result.timestamp, datetime)

    def test_to_dict_success(self):
        """Test converting successful result to dictionary."""
        data = {"test": "value"}
        metadata = {"count": 1}
        result = ServiceResult.success_result(data=data, metadata=metadata)

        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["data"] == data
        assert result_dict["metadata"] == metadata
        assert "timestamp" in result_dict
        assert "error" not in result_dict
        assert "error_code" not in result_dict

    def test_to_dict_error(self):
        """Test converting error result to dictionary."""
        error = "Test error"
        error_code = "TEST_ERROR"
        metadata = {"context": "test"}
        result = ServiceResult.error_result(
            error=error, error_code=error_code, metadata=metadata
        )

        result_dict = result.to_dict()

        assert result_dict["success"] is False
        assert result_dict["error"] == error
        assert result_dict["error_code"] == error_code
        assert result_dict["metadata"] == metadata
        assert "timestamp" in result_dict
        assert "data" not in result_dict


class TestBaseService:
    """Test BaseService class functionality."""

    def test_initialization_with_user_id(self):
        """Test service initialization with user ID."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        user_id = 123
        service = ConcreteService(user_id=user_id)

        assert service.user_id == user_id
        assert service._session is None
        assert hasattr(service, "logger")

    def test_initialization_with_session(self):
        """Test service initialization with session."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        mock_session = Mock()
        service = ConcreteService(session=mock_session)

        assert service._session == mock_session
        assert service.user_id is None

    @patch("shared.services.base.get_flask_or_standalone_session")
    def test_session_property_creates_session(self, mock_get_session):
        """Test that session property creates session when needed."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        mock_session = Mock()
        mock_get_session.return_value = mock_session

        service = ConcreteService()
        session = service.session

        assert session == mock_session
        mock_get_session.assert_called_once()

    def test_validate_user_access_success(self):
        """Test successful user access validation."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        user_id = 123
        service = ConcreteService(user_id=user_id)

        result = service.validate_user_access(user_id)
        assert result is True

    def test_validate_user_access_no_user_context(self):
        """Test user access validation without user context."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        service = ConcreteService()

        with pytest.raises(PermissionError, match="No user context available"):
            service.validate_user_access(123)

    def test_validate_user_access_wrong_user(self):
        """Test user access validation with wrong user."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        service = ConcreteService(user_id=123)

        with pytest.raises(PermissionError, match="User does not have access"):
            service.validate_user_access(456)

    def test_log_operation(self):
        """Test operation logging."""

        class ConcreteService(BaseService):
            def get_service_name(self) -> str:
                return "ConcreteService"

        service = ConcreteService(user_id=123)

        with patch.object(service.logger, "info") as mock_info:
            service.log_operation("test_operation", {"detail": "value"})

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Service operation: test_operation" in args[0]
            assert "extra" in kwargs
            assert kwargs["extra"]["service"] == "ConcreteService"
            assert kwargs["extra"]["operation"] == "test_operation"
            assert kwargs["extra"]["user_id"] == 123


class TestStatelessService:
    """Test StatelessService class functionality."""

    def test_initialization(self):
        """Test stateless service initialization."""
        service = StatelessService()

        assert hasattr(service, "logger")
        assert not hasattr(service, "user_id")
        assert not hasattr(service, "session")

    def test_log_operation(self):
        """Test operation logging in stateless service."""
        service = StatelessService()

        with patch.object(service.logger, "info") as mock_info:
            service.log_operation("test_operation", {"detail": "value"})

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Service operation: test_operation" in args[0]
            assert "extra" in kwargs
            assert kwargs["extra"]["service"] == "StatelessService"
            assert kwargs["extra"]["operation"] == "test_operation"


class TestServiceDecorators:
    """Test service decorators."""

    def test_require_user_context_success(self):
        """Test require_user_context decorator with valid user context."""

        class TestService(BaseService):
            def get_service_name(self) -> str:
                return "TestService"

            @require_user_context
            def test_method(self):
                return "success"

        service = TestService(user_id=123)
        result = service.test_method()
        assert result == "success"

    def test_require_user_context_failure(self):
        """Test require_user_context decorator without user context."""

        class TestService(BaseService):
            def get_service_name(self) -> str:
                return "TestService"

            @require_user_context
            def test_method(self):
                return "success"

        service = TestService()

        with pytest.raises(PermissionError, match="Operation requires user context"):
            service.test_method()

    def test_log_service_call_success(self):
        """Test log_service_call decorator on successful operation."""

        class TestService(StatelessService):
            @log_service_call("test_operation")
            def test_method(self):
                return "success"

        service = TestService()

        with patch.object(service, "log_operation") as mock_log:
            result = service.test_method()

            assert result == "success"
            assert mock_log.call_count == 2  # Start and success
            mock_log.assert_any_call(
                "test_operation", {"args_count": 0, "kwargs_keys": []}
            )
            mock_log.assert_any_call("test_operation_success")

    def test_log_service_call_error(self):
        """Test log_service_call decorator on error."""

        class TestService(StatelessService):
            @log_service_call("test_operation")
            def test_method(self):
                raise ValueError("Test error")

        service = TestService()

        with patch.object(service, "log_operation") as mock_log:
            with pytest.raises(ValueError, match="Test error"):
                service.test_method()

            assert mock_log.call_count == 2  # Start and error
            mock_log.assert_any_call(
                "test_operation", {"args_count": 0, "kwargs_keys": []}
            )
            mock_log.assert_any_call("test_operation_error", {"error": "Test error"})


class TestConfigurationService:
    """Test ConfigurationService functionality."""

    @patch("shared.database.get_database_session")
    @patch("shared.imports.GlobalConfiguration")
    def test_get_global_config_success(self, mock_config_model, mock_get_session):
        """Test successful global config retrieval."""
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_config = Mock()
        mock_config.value = "test_value"
        mock_config.is_encrypted = False
        mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_config
        )

        service = ConfigurationService()
        result = service.get_global_config("TEST_KEY", decrypt=False)

        assert result.success is True
        assert result.data["key"] == "TEST_KEY"
        assert result.data["value"] == "test_value"
        assert result.data["is_encrypted"] is False

    @patch("shared.database.get_database_session")
    @patch("shared.imports.GlobalConfiguration")
    def test_get_global_config_not_found(self, mock_config_model, mock_get_session):
        """Test global config retrieval when key not found."""
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter_by.return_value.first.return_value = None

        service = ConfigurationService()
        result = service.get_global_config("MISSING_KEY")

        assert result.success is False
        assert result.error_code == "CONFIG_NOT_FOUND"
        assert "not found" in result.error


class TestEncryptionService:
    """Test EncryptionService functionality."""

    @patch("shared.imports.encrypt_value")
    def test_encrypt_value_success(self, mock_encrypt):
        """Test successful value encryption."""
        mock_encrypt.return_value = "encrypted_value"

        service = EncryptionService()
        result = service.encrypt_value("test_value")

        assert result.success is True
        assert result.data["encrypted_value"] == "encrypted_value"
        mock_encrypt.assert_called_once_with("test_value")

    @patch("shared.imports.encrypt_value")
    def test_encrypt_value_failure(self, mock_encrypt):
        """Test encryption failure."""
        mock_encrypt.return_value = None

        service = EncryptionService()
        result = service.encrypt_value("test_value")

        assert result.success is False
        assert result.error_code == "ENCRYPTION_FAILED"

    @patch("shared.imports.decrypt_value_standalone")
    def test_decrypt_value_success(self, mock_decrypt):
        """Test successful value decryption."""
        mock_decrypt.return_value = "decrypted_value"

        service = EncryptionService()
        result = service.decrypt_value("encrypted_value")

        assert result.success is True
        assert result.data["decrypted_value"] == "decrypted_value"
        mock_decrypt.assert_called_once_with("encrypted_value")

    @patch("shared.imports.decrypt_value_standalone")
    def test_decrypt_value_failure(self, mock_decrypt):
        """Test decryption failure."""
        mock_decrypt.return_value = None

        service = EncryptionService()
        result = service.decrypt_value("encrypted_value")

        assert result.success is False
        assert result.error_code == "DECRYPTION_FAILED"

    @patch("shared.imports.encrypt_value")
    def test_encrypt_string_convenience_method(self, mock_encrypt):
        """Test encrypt_string convenience method."""
        mock_encrypt.return_value = "encrypted_value"

        service = EncryptionService()
        result = service.encrypt_string("test_value")

        assert result == "encrypted_value"

    @patch("shared.imports.decrypt_value_standalone")
    def test_decrypt_string_convenience_method(self, mock_decrypt):
        """Test decrypt_string convenience method."""
        mock_decrypt.return_value = "decrypted_value"

        service = EncryptionService()
        result = service.decrypt_string("encrypted_value")

        assert result == "decrypted_value"


class TestTransactionService:
    """Test TransactionService functionality."""

    def test_initialization_with_user_id(self):
        """Test transaction service initialization with user ID."""
        user_id = 123
        service = TransactionService(user_id=user_id)

        assert service.user_id == user_id
        assert hasattr(service, "logger")

    def test_validate_transaction_data_success(self):
        """Test successful transaction data validation."""
        service = TransactionService(user_id=123)

        transaction_data = {"amount": "100.50", "description": "Test transaction"}

        result = service._validate_transaction_data(transaction_data)
        assert result.success is True

    def test_validate_transaction_data_missing_fields(self):
        """Test transaction data validation with missing fields."""
        service = TransactionService(user_id=123)

        transaction_data = {
            "amount": "100.50"
            # Missing description
        }

        result = service._validate_transaction_data(transaction_data)
        assert result.success is False
        assert result.error_code == "VALIDATION_FAILED"
        assert "description" in result.error

    def test_validate_transaction_data_invalid_amount(self):
        """Test transaction data validation with invalid amount."""
        service = TransactionService(user_id=123)

        transaction_data = {"amount": "invalid", "description": "Test transaction"}

        result = service._validate_transaction_data(transaction_data)
        assert result.success is False
        assert result.error_code == "INVALID_AMOUNT_FORMAT"

    def test_validate_transaction_data_zero_amount(self):
        """Test transaction data validation with zero amount."""
        service = TransactionService(user_id=123)

        transaction_data = {"amount": "0", "description": "Test transaction"}

        result = service._validate_transaction_data(transaction_data)
        assert result.success is False
        assert result.error_code == "INVALID_AMOUNT"


class TestAuthService:
    """Test AuthService functionality."""

    def test_initialization(self):
        """Test auth service initialization."""
        service = AuthService()

        assert hasattr(service, "logger")
        assert not hasattr(service, "user_id")

    @patch("shared.database.get_database_session")
    @patch("shared.imports.User")
    def test_authenticate_user_success(self, mock_user_model, mock_get_session):
        """Test successful user authentication."""
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        mock_user = Mock()
        mock_user.id = 123
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.is_active = True
        mock_user.last_login = None
        mock_user.check_password.return_value = True

        mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_user
        )

        service = AuthService()
        result = service.authenticate_user("test@example.com", "password123")

        assert result.success is True
        assert result.data["user_id"] == 123
        assert result.data["email"] == "test@example.com"
        assert result.metadata["authentication_method"] == "password"

    @patch("shared.database.get_database_session")
    @patch("shared.imports.User")
    def test_authenticate_user_invalid_credentials(
        self, mock_user_model, mock_get_session
    ):
        """Test authentication with invalid credentials."""
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter_by.return_value.first.return_value = None

        service = AuthService()
        result = service.authenticate_user("test@example.com", "wrongpassword")

        assert result.success is False
        assert result.error_code == "AUTHENTICATION_FAILED"

    @patch("shared.database.database_session")
    @patch("shared.imports.User")
    @patch("shared.imports.Book")
    def test_create_user_success(
        self, mock_book_model, mock_user_model, mock_db_session
    ):
        """Test successful user creation."""
        # Setup mocks
        mock_session = Mock()
        mock_db_session.return_value.__enter__.return_value = mock_session

        # Mock existing user check (no existing user)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None

        # Mock new user creation
        mock_user = Mock()
        mock_user.id = 123
        mock_user.email = "newuser@example.com"
        mock_user.name = "New User"
        mock_user.is_active = True
        mock_user_model.return_value = mock_user

        # Mock book creation
        mock_book = Mock()
        mock_book.id = 456
        mock_book_model.return_value = mock_book

        service = AuthService()
        result = service.create_user("newuser@example.com", "password123", "New User")

        assert result.success is True
        assert result.data["user_id"] == 123
        assert result.data["email"] == "newuser@example.com"
        assert result.metadata["operation"] == "created"


class TestUserManagementService:
    """Test UserManagementService functionality."""

    def test_initialization_with_user_id(self):
        """Test user management service initialization with user ID."""
        user_id = 123
        service = UserManagementService(user_id=user_id)

        assert service.user_id == user_id
        assert hasattr(service, "logger")

    def test_require_user_context_decorator(self):
        """Test that user management methods require user context."""
        service = UserManagementService()  # No user_id

        with pytest.raises(PermissionError, match="Operation requires user context"):
            service.update_profile({"name": "New Name"})
