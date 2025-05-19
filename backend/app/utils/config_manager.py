from flask import current_app
from ..models import GlobalConfiguration
from .encryption import decrypt_value


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


def get_gemini_api_token():
    """
    Helper function to retrieve the Google Gemini API token.
    Returns None if no token is configured.
    """
    return get_configuration("GEMINI_API_TOKEN")
