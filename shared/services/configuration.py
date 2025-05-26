"""
Unified configuration management service.

Provides centralized access to global and user-specific configurations
with encryption support.
"""

from typing import Any, Optional

from .base import BaseService, ServiceResult, StatelessService, log_service_call


class ConfigurationService(StatelessService):
    """Service for managing global and user configurations."""

    @log_service_call("get_global_config")
    def get_global_config(self, key: str, decrypt: bool = True) -> ServiceResult:
        """Get a global configuration value."""
        try:
            from shared.imports import GlobalConfiguration, decrypt_value_standalone

            from ..database import get_database_session

            with get_database_session() as session:
                config = session.query(GlobalConfiguration).filter_by(key=key).first()

                if not config:
                    return ServiceResult.error_result(
                        f"Configuration key '{key}' not found",
                        error_code="CONFIG_NOT_FOUND",
                    )

                value = config.value
                if decrypt and config.is_encrypted:
                    value = decrypt_value_standalone(value)
                    if value is None:
                        return ServiceResult.error_result(
                            f"Failed to decrypt configuration key '{key}'",
                            error_code="DECRYPT_FAILED",
                        )

                return ServiceResult.success_result(
                    data={
                        "key": key,
                        "value": value,
                        "is_encrypted": config.is_encrypted,
                    }
                )

        except Exception as e:
            self.logger.error(f"Failed to get global config '{key}': {e}")
            return ServiceResult.error_result(
                "Failed to retrieve configuration", error_code="CONFIG_RETRIEVAL_FAILED"
            )

    @log_service_call("set_global_config")
    def set_global_config(
        self, key: str, value: str, encrypt: bool = False
    ) -> ServiceResult:
        """Set a global configuration value."""
        try:
            from shared.imports import GlobalConfiguration, encrypt_value

            from ..database import database_session

            with database_session() as session:
                config = session.query(GlobalConfiguration).filter_by(key=key).first()

                # Encrypt value if requested
                stored_value = encrypt_value(value) if encrypt else value

                if config:
                    # Update existing
                    config.value = stored_value
                    config.is_encrypted = encrypt
                    operation = "updated"
                else:
                    # Create new
                    config = GlobalConfiguration(
                        key=key, value=stored_value, is_encrypted=encrypt
                    )
                    session.add(config)
                    operation = "created"

                return ServiceResult.success_result(
                    data={"key": key, "operation": operation},
                    metadata={"is_encrypted": encrypt},
                )

        except Exception as e:
            self.logger.error(f"Failed to set global config '{key}': {e}")
            return ServiceResult.error_result(
                "Failed to save configuration", error_code="CONFIG_SAVE_FAILED"
            )

    def get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from configuration."""
        result = self.get_global_config("GEMINI_API_TOKEN", decrypt=True)
        if result.success:
            return result.data["value"]
        return None

    def get_exchange_rate_api_key(self) -> Optional[str]:
        """Get Exchange Rate API key from configuration."""
        result = self.get_global_config("EXCHANGE_RATE_API_KEY", decrypt=True)
        if result.success:
            return result.data["value"]
        return None


class UserConfigurationService(BaseService):
    """Service for managing user-specific configurations."""

    def __init__(self, user_id: int, session=None):
        super().__init__(user_id=user_id, session=session)

    def get_service_name(self) -> str:
        """Return the name of the service for logging purposes."""
        return "UserConfigurationService"

    @log_service_call("get_user_preference")
    def get_user_preference(self, key: str, default: Any = None) -> ServiceResult:
        """Get a user preference value."""
        # Implementation would depend on user preferences model
        # This is a placeholder for future user preference system
        return ServiceResult.success_result(data=default)

    @log_service_call("set_user_preference")
    def set_user_preference(self, key: str, value: Any) -> ServiceResult:
        """Set a user preference value."""
        # Implementation would depend on user preferences model
        # This is a placeholder for future user preference system
        return ServiceResult.success_result(data={"key": key, "value": value})
