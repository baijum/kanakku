from flask import current_app
from ..models import GlobalConfiguration, db
from .encryption import encrypt_value, decrypt_value
import re


def get_configuration(key, default=None):
    """
    Get a configuration value by key.
    Returns the decrypted value for encrypted configurations.
    If the key doesn't exist, returns the default value.
    """
    try:
        # Query the configuration
        config = GlobalConfiguration.query.filter_by(key=key).first()

        if not config:
            current_app.logger.debug(
                f"Configuration '{key}' not found, using default value"
            )
            return default

        # If the value is encrypted, decrypt it
        if config.is_encrypted:
            decrypted_value = decrypt_value(config.value)
            if decrypted_value is None:
                current_app.logger.error(
                    f"Failed to decrypt configuration value for '{key}'"
                )
                return default
            return decrypted_value
        else:
            return config.value
    except Exception as e:
        current_app.logger.error(f"Error retrieving configuration '{key}': {str(e)}")
        return default


def set_configuration(key, value, description=None, is_encrypted=True):
    """
    Set a configuration value by key.
    Creates a new configuration if it doesn't exist, updates if it does.

    Args:
        key (str): Configuration key
        value (str): Configuration value
        description (str, optional): Description of the configuration
        is_encrypted (bool): Whether to encrypt the value (default: True)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if configuration already exists
        config = GlobalConfiguration.query.filter_by(key=key).first()

        if config:
            # Update existing configuration
            if is_encrypted:
                config.value = encrypt_value(value)
            else:
                config.value = value

            if description is not None:
                config.description = description
            config.is_encrypted = is_encrypted

            current_app.logger.info(f"Updated configuration '{key}'")
        else:
            # Create new configuration
            config_data = {
                "key": key,
                "description": description,
                "is_encrypted": is_encrypted,
            }

            if is_encrypted:
                config_data["value"] = encrypt_value(value)
            else:
                config_data["value"] = value

            config = GlobalConfiguration(**config_data)
            db.session.add(config)

            current_app.logger.info(f"Created new configuration '{key}'")

        db.session.commit()
        return True

    except Exception as e:
        current_app.logger.error(f"Error setting configuration '{key}': {str(e)}")
        db.session.rollback()
        return False


def delete_configuration(key):
    """
    Delete a configuration by key.

    Args:
        key (str): Configuration key to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config = GlobalConfiguration.query.filter_by(key=key).first()
        if config:
            db.session.delete(config)
            db.session.commit()
            current_app.logger.info(f"Deleted configuration '{key}'")
            return True
        else:
            current_app.logger.warning(f"Configuration '{key}' not found for deletion")
            return False
    except Exception as e:
        current_app.logger.error(f"Error deleting configuration '{key}': {str(e)}")
        db.session.rollback()
        return False


def validate_gemini_api_token(token):
    """
    Validate the format of a Google Gemini API token.

    Args:
        token (str): The API token to validate

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not token:
        return False, "API token is required"

    if not isinstance(token, str):
        return False, "API token must be a string"

    # Basic format validation for Gemini API tokens
    if not token.startswith("AIzaSy"):
        return False, "Gemini API tokens should start with 'AIzaSy'"

    # Check minimum length (Gemini tokens are typically 39 characters)
    if len(token) < 30:
        return False, "API token appears to be too short"

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r"^[A-Za-z0-9_-]+$", token):
        return False, "API token contains invalid characters"

    return True, None


def get_gemini_api_token():
    """
    Helper function to retrieve the Google Gemini API token.
    Returns None if no token is configured.
    """
    return get_configuration("GEMINI_API_TOKEN")


def set_gemini_api_token(token, description=None):
    """
    Helper function to set the Google Gemini API token with validation.

    Args:
        token (str): The Gemini API token
        description (str, optional): Description for the token

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Validate the token format
    is_valid, error_message = validate_gemini_api_token(token)
    if not is_valid:
        return False, error_message

    # Set default description if none provided
    if description is None:
        description = "Google Gemini API Token for email processing"

    # Set the configuration
    success = set_configuration(
        key="GEMINI_API_TOKEN", value=token, description=description, is_encrypted=True
    )

    if success:
        return True, None
    else:
        return False, "Failed to save API token to database"


def is_gemini_api_configured():
    """
    Check if the Gemini API token is configured and available.

    Returns:
        bool: True if token is configured and accessible, False otherwise
    """
    token = get_gemini_api_token()
    return token is not None and len(token.strip()) > 0


def get_all_configurations():
    """
    Get all global configurations (for admin use).

    Returns:
        list: List of configuration dictionaries
    """
    try:
        configs = GlobalConfiguration.query.all()
        return [config.to_dict() for config in configs]
    except Exception as e:
        current_app.logger.error(f"Error retrieving all configurations: {str(e)}")
        return []


def configuration_exists(key):
    """
    Check if a configuration with the given key exists.

    Args:
        key (str): Configuration key to check

    Returns:
        bool: True if configuration exists, False otherwise
    """
    try:
        config = GlobalConfiguration.query.filter_by(key=key).first()
        return config is not None
    except Exception as e:
        current_app.logger.error(
            f"Error checking configuration existence '{key}': {str(e)}"
        )
        return False
