"""
Tests for config_manager utility module
"""

from unittest.mock import MagicMock, patch

import pytest

from app.models import GlobalConfiguration
from app.utils.config_manager import (
    configuration_exists,
    delete_configuration,
    get_all_configurations,
    get_configuration,
    get_gemini_api_token,
    is_gemini_api_configured,
    set_configuration,
    set_gemini_api_token,
    validate_gemini_api_token,
)


class TestConfigManager:
    """Test cases for config manager utility functions"""

    def test_get_configuration_existing_unencrypted(self, app, db_session):
        """Test getting existing unencrypted configuration"""
        # Create test config
        config = GlobalConfiguration(
            key="test_key",
            value="test_value",
            is_encrypted=False,
            description="Test configuration",
        )
        db_session.add(config)
        db_session.commit()

        with app.app_context():
            result = get_configuration("test_key")

        assert result == "test_value"

    def test_get_configuration_existing_encrypted(self, app, db_session):
        """Test getting existing encrypted configuration"""
        # Set a consistent encryption key for the test
        app.config["ENCRYPTION_KEY"] = "G27M7j58p9H2el6A5iJJX0RD0hAJsClDNalxOoI9zA8="

        with app.app_context():
            # Create encrypted config using the encryption utility
            from app.utils.encryption import encrypt_value

            encrypted_value = encrypt_value("secret_value")

            config = GlobalConfiguration(
                key="encrypted_key",
                value=encrypted_value,
                is_encrypted=True,
                description="Encrypted test configuration",
            )
            db_session.add(config)
            db_session.commit()

            result = get_configuration("encrypted_key")

        assert result == "secret_value"

    def test_get_configuration_nonexistent_with_default(self, app, db_session):
        """Test getting nonexistent configuration with default value"""
        with app.app_context():
            result = get_configuration("nonexistent_key", default="default_value")

        assert result == "default_value"

    def test_get_configuration_nonexistent_without_default(self, app, db_session):
        """Test getting nonexistent configuration without default value"""
        with app.app_context():
            result = get_configuration("nonexistent_key")

        assert result is None

    @patch("app.utils.config_manager.GlobalConfiguration")
    def test_get_configuration_database_error(self, mock_global_config, app):
        """Test getting configuration with database error"""
        mock_global_config.query.filter_by.side_effect = Exception("Database error")

        with app.app_context():
            result = get_configuration("error_key", default="fallback")

        assert result == "fallback"

    def test_get_gemini_api_token_exists(self, app, db_session):
        """Test getting Gemini API token when it exists"""
        # Set a consistent encryption key for the test
        app.config["ENCRYPTION_KEY"] = "G27M7j58p9H2el6A5iJJX0RD0hAJsClDNalxOoI9zA8="

        # Create Gemini token config
        with app.app_context():
            from app.utils.encryption import encrypt_value

            encrypted_token = encrypt_value("gemini_token_123")

            config = GlobalConfiguration(
                key="GEMINI_API_TOKEN",
                value=encrypted_token,
                is_encrypted=True,
                description="Gemini API Token",
            )
            db_session.add(config)
            db_session.commit()

            result = get_gemini_api_token()

        assert result == "gemini_token_123"

    def test_get_gemini_api_token_not_exists(self, app, db_session):
        """Test getting Gemini API token when it doesn't exist"""
        with app.app_context():
            result = get_gemini_api_token()

        assert result is None

    @patch("app.utils.config_manager.get_configuration")
    def test_get_gemini_api_token_database_error(self, mock_get_config, app):
        """Test getting Gemini API token with database error"""
        mock_get_config.side_effect = Exception("Database error")

        with app.app_context():
            result = get_gemini_api_token()

        assert result is None


class TestConfigurationFunctions:
    """Test cases for configuration utility functions"""

    # Define constants for test API tokens
    VALID_TEST_GEMINI_TOKEN = (
        "AIzaSyDXKNQz1234567890abcdefghijklmnop"  # Example valid token structure
    )
    INVALID_PREFIX_TEST_GEMINI_TOKEN = (
        "InvalidPrefix1234567890abcdefghijklmnop"  # Example invalid prefix
    )
    SHORT_TEST_GEMINI_TOKEN = "AIzaSy123"  # Example short token
    INVALID_CHARS_TEST_GEMINI_TOKEN = (
        "AIzaSy!@#$%^&*()_+[]{};:'\",./<>?"  # Example token with invalid characters
    )

    def test_set_configuration_new(self, app, db_session):
        """Test setting new configuration"""
        with app.app_context():
            result = set_configuration(
                "new_key", "new_value", "New config", is_encrypted=False
            )

        assert result is True

        # Verify it was saved
        saved_config = (
            db_session.query(GlobalConfiguration).filter_by(key="new_key").first()
        )
        assert saved_config is not None
        assert saved_config.value == "new_value"
        assert saved_config.is_encrypted is False

    def test_set_configuration_encrypted(self, app, db_session):
        """Test setting encrypted configuration"""
        with app.app_context():
            result = set_configuration(
                "encrypted_key", "secret_value", "Encrypted config", is_encrypted=True
            )

        assert result is True

        # Verify it was saved and encrypted
        saved_config = (
            db_session.query(GlobalConfiguration).filter_by(key="encrypted_key").first()
        )
        assert saved_config is not None
        assert saved_config.is_encrypted is True
        assert saved_config.value != "secret_value"  # Should be encrypted

    def test_set_configuration_update_existing(self, app, db_session):
        """Test updating existing configuration"""
        # Create existing config
        config = GlobalConfiguration(
            key="update_key",
            value="old_value",
            is_encrypted=False,
            description="Old description",
        )
        db_session.add(config)
        db_session.commit()

        with app.app_context():
            result = set_configuration(
                "update_key", "new_value", "New description", is_encrypted=False
            )

        assert result is True

        # Verify it was updated
        updated_config = (
            db_session.query(GlobalConfiguration).filter_by(key="update_key").first()
        )
        assert updated_config.value == "new_value"
        assert updated_config.description == "New description"

    def test_delete_configuration_existing(self, app, db_session):
        """Test deleting existing configuration"""
        # Create test config
        config = GlobalConfiguration(
            key="delete_key",
            value="delete_value",
            is_encrypted=False,
            description="To be deleted",
        )
        db_session.add(config)
        db_session.commit()

        with app.app_context():
            result = delete_configuration("delete_key")

        assert result is True

        # Verify it was deleted
        deleted_config = (
            db_session.query(GlobalConfiguration).filter_by(key="delete_key").first()
        )
        assert deleted_config is None

    def test_delete_configuration_nonexistent(self, app, db_session):
        """Test deleting nonexistent configuration"""
        with app.app_context():
            result = delete_configuration("nonexistent_delete_key")

        assert result is False

    def test_validate_gemini_api_token_valid(self, app):
        """Test validating valid Gemini API token"""
        with app.app_context():
            is_valid, error = validate_gemini_api_token(self.VALID_TEST_GEMINI_TOKEN)

        assert is_valid is True
        assert error is None

    def test_validate_gemini_api_token_invalid_prefix(self, app):
        """Test validating token with invalid prefix"""
        with app.app_context():
            is_valid, error = validate_gemini_api_token(
                self.INVALID_PREFIX_TEST_GEMINI_TOKEN
            )

        assert is_valid is False
        assert "should start with 'AIzaSy'" in error

    def test_validate_gemini_api_token_too_short(self, app):
        """Test validating Gemini API token that is too short"""
        with app.app_context():
            is_valid, error_message = validate_gemini_api_token(
                self.SHORT_TEST_GEMINI_TOKEN
            )

        assert not is_valid
        assert (
            "API token appears to be too short" in error_message
        )  # Check for specific message

    def test_validate_gemini_api_token_invalid_characters(self, app):
        """Test validating Gemini API token with invalid characters"""
        with app.app_context():
            is_valid, error_message = validate_gemini_api_token(
                self.INVALID_CHARS_TEST_GEMINI_TOKEN
            )

        assert not is_valid
        assert "API token contains invalid characters" in error_message

    def test_validate_gemini_api_token_empty(self, app):
        """Test validating empty token"""
        with app.app_context():
            is_valid, error = validate_gemini_api_token("")

        assert is_valid is False
        assert "required" in error

    def test_validate_gemini_api_token_none(self, app):
        """Test validating None token"""
        with app.app_context():
            is_valid, error = validate_gemini_api_token(None)

        assert is_valid is False
        assert "required" in error

    def test_validate_gemini_api_token_non_string(self, app):
        """Test validating non-string token"""
        with app.app_context():
            is_valid, error = validate_gemini_api_token(12345)

        assert is_valid is False
        assert "must be a string" in error

    def test_set_gemini_api_token_valid(self, app, db_session):
        """Test setting valid Gemini API token"""
        with app.app_context():
            success, message = set_gemini_api_token(self.VALID_TEST_GEMINI_TOKEN)

        assert success is True
        assert message is None

        # Verify token is stored and encrypted
        token_config = (
            db_session.query(GlobalConfiguration)
            .filter_by(key="GEMINI_API_TOKEN")
            .first()
        )
        assert token_config is not None
        assert token_config.is_encrypted is True
        # Ensure the stored value is not the original token, implying encryption
        assert token_config.value != self.VALID_TEST_GEMINI_TOKEN

    def test_set_gemini_api_token_invalid(self, app, db_session):
        """Test setting invalid Gemini API token"""
        invalid_token = "invalid_token"

        with app.app_context():
            success, error = set_gemini_api_token(invalid_token)

        assert success is False
        assert error is not None

    def test_is_gemini_api_configured_true(self, app, db_session):
        """Test checking if Gemini API is configured (true case)"""
        # Set a consistent encryption key for the test
        app.config["ENCRYPTION_KEY"] = "G27M7j58p9H2el6A5iJJX0RD0hAJsClDNalxOoI9zA8="

        # Create Gemini token config
        with app.app_context():
            from app.utils.encryption import encrypt_value

            encrypted_token = encrypt_value("AIzaSyDXKNQz1234567890abcdefghijklmnop")

            config = GlobalConfiguration(
                key="GEMINI_API_TOKEN",
                value=encrypted_token,
                is_encrypted=True,
                description="Gemini API Token",
            )
            db_session.add(config)
            db_session.commit()

            result = is_gemini_api_configured()

        assert result is True

    def test_is_gemini_api_configured_false(self, app, db_session):
        """Test checking if Gemini API is configured (false case)"""
        with app.app_context():
            result = is_gemini_api_configured()

        assert result is False

    def test_get_all_configurations(self, app, db_session):
        """Test getting all configurations"""
        # Create multiple test configs
        configs = [
            GlobalConfiguration(
                key="list_key1",
                value="value1",
                is_encrypted=False,
                description="Config 1",
            ),
            GlobalConfiguration(
                key="list_key2",
                value="value2",
                is_encrypted=True,
                description="Config 2",
            ),
            GlobalConfiguration(
                key="list_key3",
                value="value3",
                is_encrypted=False,
                description="Config 3",
            ),
        ]
        db_session.add_all(configs)
        db_session.commit()

        with app.app_context():
            result = get_all_configurations()

        assert len(result) >= 3  # At least our test configs
        keys = [config["key"] for config in result]
        assert "list_key1" in keys
        assert "list_key2" in keys
        assert "list_key3" in keys

    def test_configuration_exists_true(self, app, db_session):
        """Test checking if configuration exists (true case)"""
        # Create test config
        config = GlobalConfiguration(
            key="exists_key",
            value="exists_value",
            is_encrypted=False,
            description="Exists test",
        )
        db_session.add(config)
        db_session.commit()

        with app.app_context():
            result = configuration_exists("exists_key")

        assert result is True

    def test_configuration_exists_false(self, app, db_session):
        """Test checking if configuration exists (false case)"""
        with app.app_context():
            result = configuration_exists("nonexistent_exists_key")

        assert result is False

    @patch("app.utils.config_manager.db.session")
    def test_database_error_handling(self, mock_session, app):
        """Test error handling with database errors"""
        mock_session.commit.side_effect = Exception("Database error")

        with app.app_context():
            # Test set with error
            result = set_configuration("error_key", "value", "desc")
            assert result is False

            # Test delete with error
            result = delete_configuration("error_key")
            assert result is False
