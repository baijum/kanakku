"""
Tests for encryption utility module
"""

import base64
import os
from unittest.mock import MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from app.utils.encryption import decrypt_value, encrypt_value, get_encryption_key

# Define a constant for the test encryption key
TEST_ENCRYPTION_KEY = (
    "G27M7j58p9H2el6A5iJJX0RD0hAJsClDNalxOoI9zA8="  # Dummy key for testing
)


class TestEncryption:
    """Test cases for encryption utility functions"""

    def test_get_encryption_key_from_config(self, app):
        """Test getting encryption key from app config"""
        test_key = Fernet.generate_key().decode()
        app.config["ENCRYPTION_KEY"] = test_key

        with app.app_context():
            key = get_encryption_key()

        assert key == test_key

    @patch.dict(os.environ, {"ENCRYPTION_KEY": TEST_ENCRYPTION_KEY})
    def test_get_encryption_key_from_environment(self, app):
        """Test getting encryption key from environment variable"""
        # Clear config key to force environment lookup
        app.config.pop("ENCRYPTION_KEY", None)

        with app.app_context():
            key = get_encryption_key()

        assert key == TEST_ENCRYPTION_KEY

    def test_get_encryption_key_generates_temporary(self, app):
        """Test generating temporary key when none configured"""
        # Clear both config and environment
        app.config.pop("ENCRYPTION_KEY", None)

        with app.app_context():
            with patch.dict(os.environ, {}, clear=True):
                key = get_encryption_key()

        # Should be a valid Fernet key
        assert key is not None
        assert len(key) > 0
        # Should be able to create Fernet instance
        f = Fernet(key.encode())
        assert f is not None

    def test_get_encryption_key_pads_key(self, app):
        """Test key padding for improperly formatted keys"""
        # Key without proper padding
        test_key = "test_key_without_padding"
        app.config["ENCRYPTION_KEY"] = test_key

        with app.app_context():
            key = get_encryption_key()

        # Should have padding added
        assert key.endswith("=")

    def test_get_encryption_key_invalid_key_generates_new(self, app):
        """Test generating new key when existing key is invalid"""
        # Invalid key (too short)
        app.config["ENCRYPTION_KEY"] = "invalid_key"

        with app.app_context():
            key = get_encryption_key()

        # Should generate a new valid key
        assert key is not None
        # Should be able to create Fernet instance
        f = Fernet(key.encode())
        assert f is not None

    def test_encrypt_value_success(self, app):
        """Test successful value encryption"""
        test_value = "secret_password_123"

        with app.app_context():
            encrypted = encrypt_value(test_value)

        assert encrypted is not None
        assert encrypted != test_value
        assert len(encrypted) > 0

    def test_encrypt_value_none(self, app):
        """Test encrypting None value"""
        with app.app_context():
            encrypted = encrypt_value(None)

        assert encrypted is None

    def test_encrypt_value_empty_string(self, app):
        """Test encrypting empty string"""
        with app.app_context():
            encrypted = encrypt_value("")

        assert encrypted is None

    def test_decrypt_value_success(self, app):
        """Test successful value decryption"""
        test_value = "secret_password_123"

        # Set a consistent encryption key for the test
        app.config["ENCRYPTION_KEY"] = TEST_ENCRYPTION_KEY

        with app.app_context():
            encrypted = encrypt_value(test_value)
            decrypted = decrypt_value(encrypted)

        assert decrypted == test_value

    def test_decrypt_value_none(self, app):
        """Test decrypting None value"""
        with app.app_context():
            decrypted = decrypt_value(None)

        assert decrypted is None

    def test_decrypt_value_empty_string(self, app):
        """Test decrypting empty string"""
        with app.app_context():
            decrypted = decrypt_value("")

        assert decrypted is None

    def test_decrypt_value_invalid_data(self, app):
        """Test decrypting invalid encrypted data"""
        invalid_encrypted = "invalid_encrypted_data"

        with app.app_context():
            decrypted = decrypt_value(invalid_encrypted)

        assert decrypted is None

    def test_encrypt_decrypt_roundtrip(self, app):
        """Test complete encrypt/decrypt roundtrip"""
        test_values = [
            "simple_password",
            "complex_password_with_symbols!@#$%^&*()",
            "unicode_password_ñáéíóú",
            "very_long_password_" + "x" * 100,
            "123456789",
            "password with spaces",
        ]

        # Set a consistent encryption key for the test
        app.config["ENCRYPTION_KEY"] = TEST_ENCRYPTION_KEY

        with app.app_context():
            for test_value in test_values:
                encrypted = encrypt_value(test_value)
                decrypted = decrypt_value(encrypted)
                assert decrypted == test_value, f"Failed for value: {test_value}"

    def test_encryption_key_consistency(self, app):
        """Test that encryption key remains consistent within app context"""
        # Set a consistent encryption key for the test
        app.config["ENCRYPTION_KEY"] = TEST_ENCRYPTION_KEY

        with app.app_context():
            key1 = get_encryption_key()
            key2 = get_encryption_key()

        assert key1 == key2

    def test_different_keys_produce_different_encryption(self, app):
        """Test that different keys produce different encrypted values"""
        test_value = "test_password"

        # First encryption with one key
        app.config["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        with app.app_context():
            encrypted1 = encrypt_value(test_value)

        # Second encryption with different key
        app.config["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        with app.app_context():
            encrypted2 = encrypt_value(test_value)

        assert encrypted1 != encrypted2

    @patch("app.utils.encryption.Fernet")
    def test_decrypt_value_exception_handling(self, mock_fernet, app):
        """Test exception handling in decrypt_value"""
        # Mock Fernet to raise exception on decrypt
        mock_fernet_instance = MagicMock()
        mock_fernet_instance.decrypt.side_effect = Exception("Decryption failed")
        mock_fernet.return_value = mock_fernet_instance

        with app.app_context():
            result = decrypt_value("some_encrypted_data")

        assert result is None

    def test_key_validation_with_base64_decode_error(self, app):
        """Test key validation when base64 decode fails"""
        # Invalid base64 key
        app.config["ENCRYPTION_KEY"] = "invalid_base64_key!"

        with app.app_context():
            key = get_encryption_key()

        # Should generate a new valid key
        assert key is not None
        # Should be able to create Fernet instance
        f = Fernet(key.encode())
        assert f is not None
