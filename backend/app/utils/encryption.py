import base64
import logging
import os

from cryptography.fernet import Fernet
from flask import current_app


def get_encryption_key():
    """
    Get the encryption key from environment or create one if it doesn't exist.
    In production, this key should be set in environment variables.
    """
    key = current_app.config.get("ENCRYPTION_KEY")
    if not key:
        key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        # If no key is found, generate a warning but return a temporary key
        # This is not ideal for production as the key will change on restart
        current_app.logger.warning(
            "No encryption key found in environment. Using temporary key."
        )
        key = Fernet.generate_key().decode()
        return key

    # Ensure the key is properly formatted for Fernet
    if not key.endswith("="):
        # Pad the key if necessary
        key = key + "=" * (-len(key) % 4)

    try:
        # Attempt to decode and validate the key
        decoded_key = base64.urlsafe_b64decode(key)
        if len(decoded_key) != 32:
            raise ValueError("Invalid key length")
        return key
    except Exception as e:
        current_app.logger.error(f"Invalid encryption key: {str(e)}")
        # Generate a temporary key for this session
        key = Fernet.generate_key().decode()
        return key


def get_encryption_key_standalone():
    """
    Get the encryption key from environment variables without Flask context.
    """
    logger = logging.getLogger(__name__)
    logger.debug("Getting encryption key from environment variables")
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        logger.warning("No encryption key found in environment. Using temporary key.")
        logger.debug("Generating temporary encryption key")
        key = Fernet.generate_key().decode()

    # Ensure the key is properly formatted for Fernet
    if not key.endswith("="):
        logger.debug("Padding encryption key for proper formatting")
        # Pad the key if necessary
        key = key + "=" * (-len(key) % 4)

    try:
        # Attempt to decode and validate the key
        logger.debug("Validating encryption key format")
        decoded_key = base64.urlsafe_b64decode(key)
        if len(decoded_key) != 32:
            raise ValueError("Invalid key length")
        logger.debug("Encryption key validation successful")
    except Exception as e:
        logger.error(f"Invalid encryption key: {str(e)}")
        logger.debug("Generating new temporary key due to validation failure")
        # Generate a temporary key for this session
        key = Fernet.generate_key().decode()

    return key


def encrypt_value(value):
    """
    Encrypt a sensitive value using Fernet symmetric encryption.
    """
    if not value:
        return None

    key = get_encryption_key()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    encrypted_data = f.encrypt(value.encode())
    return encrypted_data.decode()


def decrypt_value(encrypted_value):
    """
    Decrypt an encrypted value using Fernet symmetric encryption.
    """
    if not encrypted_value:
        return None

    key = get_encryption_key()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    try:
        decrypted_data = f.decrypt(encrypted_value.encode())
        return decrypted_data.decode()
    except Exception as e:
        current_app.logger.error(f"Failed to decrypt value: {str(e)}")
        return None


def decrypt_value_standalone(encrypted_value):
    """
    Decrypt an encrypted value without Flask context.
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f"Attempting to decrypt value (length: {len(encrypted_value) if encrypted_value else 0})"
    )
    if not encrypted_value:
        logger.debug("No encrypted value provided, returning None")
        return None

    key = get_encryption_key_standalone()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    try:
        logger.debug("Decrypting value using Fernet")
        decrypted_data = f.decrypt(encrypted_value.encode())
        decrypted_result = decrypted_data.decode()
        logger.debug("Value decryption successful")
        return decrypted_result
    except Exception as e:
        logger.error(f"Failed to decrypt value: {str(e)}")
        logger.debug(
            f"Decryption failed with encrypted_value type: {type(encrypted_value)}"
        )
        return None
