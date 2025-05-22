import pytest
import json
from app.models import GlobalConfiguration, User, db
from app.utils.encryption import encrypt_value, decrypt_value
from cryptography.fernet import Fernet


class TestGlobalSettings:
    """Test suite for global configuration settings functionality."""

    def test_get_all_global_configs_admin_required(self, client, user):
        """Test that admin privileges are required to access global configurations."""
        # Make user non-admin
        user.is_admin = False
        db.session.commit()

        # Create access token for non-admin user
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user.id))  # Convert to string

        response = client.get(
            "/api/v1/settings/global",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Admin privileges required" in response.get_json()["error"]

    def test_get_all_global_configs_success(self, authenticated_client, app):
        """Test successful retrieval of all global configurations."""
        # Create test configurations
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            app.config['ENCRYPTION_KEY'] = Fernet.generate_key().decode()
            
            config1 = GlobalConfiguration(
                key="TEST_KEY_1",
                value="test_value_1",
                description="Test configuration 1",
                is_encrypted=False
            )
            config2 = GlobalConfiguration(
                key="GEMINI_API_TOKEN",
                value=encrypt_value("test_api_token_123"),
                description="Google Gemini API Token",
                is_encrypted=True
            )
            db.session.add_all([config1, config2])
            db.session.commit()

        response = authenticated_client.get("/api/v1/settings/global")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "configurations" in data
        assert len(data["configurations"]) == 2
        
        # Check that encrypted values are masked
        gemini_config = next(
            (c for c in data["configurations"] if c["key"] == "GEMINI_API_TOKEN"), 
            None
        )
        assert gemini_config is not None
        assert gemini_config["value"] == "[ENCRYPTED]"
        assert gemini_config["is_encrypted"] is True

    def test_get_specific_global_config(self, authenticated_client, app):
        """Test retrieval of a specific global configuration."""
        with app.app_context():
            config = GlobalConfiguration(
                key="TEST_SPECIFIC",
                value="specific_value",
                description="Specific test config",
                is_encrypted=False
            )
            db.session.add(config)
            db.session.commit()

        response = authenticated_client.get("/api/v1/settings/global/TEST_SPECIFIC")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "configuration" in data
        assert data["configuration"]["key"] == "TEST_SPECIFIC"
        assert data["configuration"]["value"] == "specific_value"

    def test_get_nonexistent_config(self, authenticated_client):
        """Test retrieval of a non-existent configuration."""
        response = authenticated_client.get("/api/v1/settings/global/NONEXISTENT")
        assert response.status_code == 404
        assert "not found" in response.get_json()["error"]

    def test_create_global_config_success(self, authenticated_client):
        """Test successful creation of a global configuration."""
        config_data = {
            "key": "NEW_CONFIG",
            "value": "new_value",
            "description": "A new configuration",
            "is_encrypted": False
        }

        response = authenticated_client.post(
            "/api/v1/settings/global",
            json=config_data
        )
        assert response.status_code == 201
        
        data = response.get_json()
        assert "message" in data
        assert "configuration" in data
        assert data["configuration"]["key"] == "NEW_CONFIG"

    def test_create_gemini_api_token(self, authenticated_client, app):
        """Test creation of Gemini API token configuration."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            app.config['ENCRYPTION_KEY'] = Fernet.generate_key().decode()
            
            config_data = {
                "key": "GEMINI_API_TOKEN",
                "value": "AIzaSyDummyTokenForTesting123456789",
                "description": "Google Gemini API Token for email processing",
                "is_encrypted": True
            }

            response = authenticated_client.post(
                "/api/v1/settings/global",
                json=config_data
            )
            assert response.status_code == 201
            
            data = response.get_json()
            assert data["configuration"]["key"] == "GEMINI_API_TOKEN"
            assert data["configuration"]["is_encrypted"] is True
            assert data["configuration"]["value"] == "[ENCRYPTED]"

    def test_create_config_missing_fields(self, authenticated_client):
        """Test creation with missing required fields."""
        # Missing value
        response = authenticated_client.post(
            "/api/v1/settings/global",
            json={"key": "INCOMPLETE"}
        )
        assert response.status_code == 400
        assert "Key and value are required" in response.get_json()["error"]

        # Missing key
        response = authenticated_client.post(
            "/api/v1/settings/global",
            json={"value": "incomplete"}
        )
        assert response.status_code == 400
        assert "Key and value are required" in response.get_json()["error"]

    def test_create_duplicate_config(self, authenticated_client, app):
        """Test creation of configuration with duplicate key."""
        with app.app_context():
            existing_config = GlobalConfiguration(
                key="DUPLICATE_KEY",
                value="existing_value",
                is_encrypted=False
            )
            db.session.add(existing_config)
            db.session.commit()

        config_data = {
            "key": "DUPLICATE_KEY",
            "value": "new_value",
            "is_encrypted": False
        }

        response = authenticated_client.post(
            "/api/v1/settings/global",
            json=config_data
        )
        assert response.status_code == 409
        assert "already exists" in response.get_json()["error"]

    def test_update_global_config(self, authenticated_client, app):
        """Test updating an existing global configuration."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            app.config['ENCRYPTION_KEY'] = Fernet.generate_key().decode()
            
            config = GlobalConfiguration(
                key="UPDATE_TEST",
                value="original_value",
                description="Original description",
                is_encrypted=False
            )
            db.session.add(config)
            db.session.commit()

        update_data = {
            "value": "updated_value",
            "description": "Updated description",
            "is_encrypted": True
        }

        response = authenticated_client.put(
            "/api/v1/settings/global/UPDATE_TEST",
            json=update_data
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert "updated successfully" in data["message"]

    def test_update_gemini_token(self, authenticated_client, app):
        """Test updating the Gemini API token."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            test_key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_KEY'] = test_key
            
            config = GlobalConfiguration(
                key="GEMINI_API_TOKEN",
                value=encrypt_value("old_token"),
                description="Old Gemini token",
                is_encrypted=True
            )
            db.session.add(config)
            db.session.commit()

        update_data = {
            "value": "AIzaSyNewGeminiToken987654321",
            "description": "Updated Gemini API Token",
            "is_encrypted": True
        }

        response = authenticated_client.put(
            "/api/v1/settings/global/GEMINI_API_TOKEN",
            json=update_data
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert "updated successfully" in data["message"]

    def test_update_nonexistent_config(self, authenticated_client):
        """Test updating a non-existent configuration."""
        response = authenticated_client.put(
            "/api/v1/settings/global/NONEXISTENT",
            json={"value": "test"}
        )
        assert response.status_code == 404
        assert "not found" in response.get_json()["error"]

    def test_delete_global_config(self, authenticated_client, app):
        """Test deleting a global configuration."""
        with app.app_context():
            config = GlobalConfiguration(
                key="DELETE_TEST",
                value="delete_value",
                is_encrypted=False
            )
            db.session.add(config)
            db.session.commit()

        response = authenticated_client.delete("/api/v1/settings/global/DELETE_TEST")
        assert response.status_code == 200
        assert "deleted successfully" in response.get_json()["message"]

    def test_delete_nonexistent_config(self, authenticated_client):
        """Test deleting a non-existent configuration."""
        response = authenticated_client.delete("/api/v1/settings/global/NONEXISTENT")
        assert response.status_code == 404

    def test_get_decrypted_value(self, authenticated_client, app):
        """Test getting the decrypted value of an encrypted configuration."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            test_key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_KEY'] = test_key
            
            test_value = "secret_encrypted_value"
            config = GlobalConfiguration(
                key="ENCRYPTED_TEST",
                value=encrypt_value(test_value),
                description="Encrypted test config",
                is_encrypted=True
            )
            db.session.add(config)
            db.session.commit()

        response = authenticated_client.get("/api/v1/settings/global/ENCRYPTED_TEST/value")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["key"] == "ENCRYPTED_TEST"
        assert data["value"] == test_value

    def test_get_decrypted_value_unencrypted_config(self, authenticated_client, app):
        """Test getting the value of an unencrypted configuration."""
        with app.app_context():
            test_value = "unencrypted_value"
            config = GlobalConfiguration(
                key="UNENCRYPTED_TEST",
                value=test_value,
                description="Unencrypted test config",
                is_encrypted=False
            )
            db.session.add(config)
            db.session.commit()

        response = authenticated_client.get("/api/v1/settings/global/UNENCRYPTED_TEST/value")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["key"] == "UNENCRYPTED_TEST"
        assert data["value"] == test_value

    def test_non_admin_cannot_access_endpoints(self, client, app):
        """Test that non-admin users cannot access any global configuration endpoints."""
        # Create a non-admin user
        with app.app_context():
            user = User(email="nonadmin@example.com", is_admin=False, is_active=True)
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

            # Create access token for non-admin user
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(user_id))  # Convert to string
            headers = {"Authorization": f"Bearer {token}"}

            # Test all endpoints return 403
            endpoints = [
                ("GET", "/api/v1/settings/global"),
                ("GET", "/api/v1/settings/global/TEST_KEY"),
                ("POST", "/api/v1/settings/global"),
                ("PUT", "/api/v1/settings/global/TEST_KEY"),
                ("DELETE", "/api/v1/settings/global/TEST_KEY"),
                ("GET", "/api/v1/settings/global/TEST_KEY/value"),
            ]

            for method, endpoint in endpoints:
                if method == "GET":
                    response = client.get(endpoint, headers=headers)
                elif method == "POST":
                    response = client.post(endpoint, headers=headers, json={"key": "test", "value": "test"})
                elif method == "PUT":
                    response = client.put(endpoint, headers=headers, json={"value": "test"})
                elif method == "DELETE":
                    response = client.delete(endpoint, headers=headers)
                
                assert response.status_code == 403, f"Endpoint {method} {endpoint} should require admin privileges"


class TestConfigManager:
    """Test suite for configuration manager utility functions."""

    def test_get_configuration_existing_unencrypted(self, app):
        """Test getting an existing unencrypted configuration."""
        with app.app_context():
            from app.utils.config_manager import get_configuration
            
            config = GlobalConfiguration(
                key="TEST_UNENCRYPTED",
                value="test_value",
                is_encrypted=False
            )
            db.session.add(config)
            db.session.commit()

            result = get_configuration("TEST_UNENCRYPTED")
            assert result == "test_value"

    def test_get_configuration_existing_encrypted(self, app):
        """Test getting an existing encrypted configuration."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            test_key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_KEY'] = test_key
            
            from app.utils.config_manager import get_configuration
            
            test_value = "encrypted_test_value"
            config = GlobalConfiguration(
                key="TEST_ENCRYPTED",
                value=encrypt_value(test_value),
                is_encrypted=True
            )
            db.session.add(config)
            db.session.commit()

            result = get_configuration("TEST_ENCRYPTED")
            assert result == test_value

    def test_get_configuration_nonexistent_with_default(self, app):
        """Test getting a non-existent configuration with default value."""
        with app.app_context():
            from app.utils.config_manager import get_configuration
            
            result = get_configuration("NONEXISTENT", "default_value")
            assert result == "default_value"

    def test_get_configuration_nonexistent_without_default(self, app):
        """Test getting a non-existent configuration without default value."""
        with app.app_context():
            from app.utils.config_manager import get_configuration
            
            result = get_configuration("NONEXISTENT")
            assert result is None

    def test_get_gemini_api_token_exists(self, app):
        """Test getting Gemini API token when it exists."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            test_key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_KEY'] = test_key
            
            from app.utils.config_manager import get_gemini_api_token
            
            test_token = "AIzaSyTestGeminiToken123456789"
            config = GlobalConfiguration(
                key="GEMINI_API_TOKEN",
                value=encrypt_value(test_token),
                is_encrypted=True
            )
            db.session.add(config)
            db.session.commit()

            result = get_gemini_api_token()
            assert result == test_token

    def test_get_gemini_api_token_not_exists(self, app):
        """Test getting Gemini API token when it doesn't exist."""
        with app.app_context():
            from app.utils.config_manager import get_gemini_api_token
            
            result = get_gemini_api_token()
            assert result is None


class TestEncryptionIntegration:
    """Test suite for encryption integration with global configurations."""

    def test_encryption_roundtrip(self, app):
        """Test that encryption and decryption work correctly."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            test_key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_KEY'] = test_key
            
            original_value = "test_secret_value"
            encrypted_value = encrypt_value(original_value)
            decrypted_value = decrypt_value(encrypted_value)
            
            assert encrypted_value != original_value
            assert decrypted_value == original_value

    def test_global_config_encryption_integration(self, app):
        """Test that global configuration encryption works end-to-end."""
        with app.app_context():
            # Set a proper test encryption key for consistent testing
            test_key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_KEY'] = test_key
            
            from app.utils.config_manager import get_configuration
            
            original_token = "AIzaSyTestTokenForEncryption987654321"
            
            # Create encrypted configuration
            config = GlobalConfiguration(
                key="TEST_ENCRYPTION_INTEGRATION",
                value=encrypt_value(original_token),
                description="Test encryption integration",
                is_encrypted=True
            )
            db.session.add(config)
            db.session.commit()

            # Retrieve and verify decryption
            decrypted_value = get_configuration("TEST_ENCRYPTION_INTEGRATION")
            assert decrypted_value == original_token 