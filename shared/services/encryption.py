"""
Unified encryption service.

Provides a consistent interface for encryption/decryption operations
across backend and banktransactions modules.
"""

from typing import Optional
from .base import StatelessService, ServiceResult, log_service_call


class EncryptionService(StatelessService):
    """Service for encryption and decryption operations."""

    @log_service_call("encrypt_value")
    def encrypt_value(self, value: str) -> ServiceResult:
        """Encrypt a value using the configured encryption method."""
        try:
            from shared.imports import encrypt_value

            encrypted_value = encrypt_value(value)
            if encrypted_value is None:
                return ServiceResult.error_result(
                    "Failed to encrypt value", error_code="ENCRYPTION_FAILED"
                )

            return ServiceResult.success_result(
                data={"encrypted_value": encrypted_value}
            )

        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return ServiceResult.error_result(
                f"Encryption failed: {str(e)}", error_code="ENCRYPTION_ERROR"
            )

    @log_service_call("decrypt_value")
    def decrypt_value(self, encrypted_value: str) -> ServiceResult:
        """Decrypt a value using the configured encryption method."""
        try:
            from shared.imports import decrypt_value_standalone

            decrypted_value = decrypt_value_standalone(encrypted_value)
            if decrypted_value is None:
                return ServiceResult.error_result(
                    "Failed to decrypt value", error_code="DECRYPTION_FAILED"
                )

            return ServiceResult.success_result(
                data={"decrypted_value": decrypted_value}
            )

        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return ServiceResult.error_result(
                f"Decryption failed: {str(e)}", error_code="DECRYPTION_ERROR"
            )

    def encrypt_string(self, value: str) -> Optional[str]:
        """Convenience method to encrypt a string and return the result directly."""
        result = self.encrypt_value(value)
        if result.success:
            return result.data["encrypted_value"]
        return None

    def decrypt_string(self, encrypted_value: str) -> Optional[str]:
        """Convenience method to decrypt a string and return the result directly."""
        result = self.decrypt_value(encrypted_value)
        if result.success:
            return result.data["decrypted_value"]
        return None
