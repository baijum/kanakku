from flask import Blueprint, g, jsonify, request

from .extensions import api_token_required, db
from .models import GlobalConfiguration
from .utils.encryption import decrypt_value, encrypt_value
from .utils.logging_utils import log_api_call, log_business_logic, log_debug, log_error

settings = Blueprint("settings", __name__)


@settings.route("/api/v1/settings/global", methods=["GET"])
@api_token_required
def get_all_global_configs():
    """Get all global configuration settings - admin only"""
    user_id = g.current_user.id

    log_api_call(
        "/api/v1/settings/global",
        "GET",
        user_id=user_id,
        extra_data={
            "operation": "get_all_global_configs",
            "is_admin": g.current_user.is_admin,
        },
    )

    # Check if user is admin
    if not g.current_user.is_admin:
        log_debug(
            "Access denied: non-admin user attempted to access global configs",
            extra_data={"user_id": user_id},
            module_name="Settings",
        )
        return jsonify({"error": "Admin privileges required"}), 403

    log_debug(
        "Admin user accessing all global configurations",
        extra_data={"user_id": user_id},
        module_name="Settings",
    )

    # Query all configuration entries
    configs = GlobalConfiguration.query.all()

    log_debug(
        "Retrieved global configurations",
        extra_data={"user_id": user_id, "config_count": len(configs)},
        module_name="Settings",
    )

    # Convert to list of dictionaries
    config_list = [config.to_dict() for config in configs]

    return jsonify({"configurations": config_list}), 200


@settings.route("/api/v1/settings/global/<string:key>", methods=["GET"])
@api_token_required
def get_global_config(key):
    """Get a specific global configuration setting - admin only"""
    user_id = g.current_user.id

    log_api_call(
        "/api/v1/settings/global/<key>",
        "GET",
        user_id=user_id,
        extra_data={
            "operation": "get_global_config",
            "key": key,
            "is_admin": g.current_user.is_admin,
        },
    )

    # Check if user is admin
    if not g.current_user.is_admin:
        log_debug(
            "Access denied: non-admin user attempted to access global config",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": "Admin privileges required"}), 403

    log_debug(
        "Admin user accessing specific global configuration",
        extra_data={"user_id": user_id, "key": key},
        module_name="Settings",
    )

    # Query the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()

    if not config:
        log_debug(
            "Global configuration not found",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    log_debug(
        "Global configuration found and returning",
        extra_data={
            "user_id": user_id,
            "key": key,
            "is_encrypted": config.is_encrypted,
        },
        module_name="Settings",
    )

    return jsonify({"configuration": config.to_dict()}), 200


@settings.route("/api/v1/settings/global", methods=["POST"])
@api_token_required
def create_global_config():
    """Create a new global configuration setting - admin only"""
    user_id = g.current_user.id
    data = request.get_json()

    log_api_call(
        "/api/v1/settings/global",
        "POST",
        user_id=user_id,
        extra_data={
            "operation": "create_global_config",
            "is_admin": g.current_user.is_admin,
            "key": data.get("key") if data else None,
        },
    )

    # Check if user is admin
    if not g.current_user.is_admin:
        log_debug(
            "Access denied: non-admin user attempted to create global config",
            extra_data={"user_id": user_id},
            module_name="Settings",
        )
        return jsonify({"error": "Admin privileges required"}), 403

    # Validate required fields
    if not data.get("key") or not data.get("value"):
        log_debug(
            "Validation failed: missing required fields",
            extra_data={
                "user_id": user_id,
                "has_key": bool(data.get("key")),
                "has_value": bool(data.get("value")),
            },
            module_name="Settings",
        )
        return jsonify({"error": "Key and value are required fields"}), 400

    log_debug(
        "Creating new global configuration",
        extra_data={
            "user_id": user_id,
            "key": data["key"],
            "is_encrypted": data.get("is_encrypted", True),
            "has_description": bool(data.get("description")),
        },
        module_name="Settings",
    )

    # Check for existing configuration with same key
    existing_config = GlobalConfiguration.query.filter_by(key=data["key"]).first()
    if existing_config:
        log_debug(
            "Configuration creation failed: key already exists",
            extra_data={"user_id": user_id, "key": data["key"]},
            module_name="Settings",
        )
        return (
            jsonify(
                {"error": f"Configuration with key '{data['key']}' already exists"}
            ),
            409,
        )

    # Prepare configuration data
    config_data = {
        "key": data["key"],
        "description": data.get("description"),
        "is_encrypted": data.get("is_encrypted", True),
    }

    # Encrypt the value if needed
    if config_data["is_encrypted"]:
        log_debug(
            "Encrypting configuration value",
            extra_data={"user_id": user_id, "key": data["key"]},
            module_name="Settings",
        )
        config_data["value"] = encrypt_value(data["value"])
    else:
        log_debug(
            "Storing configuration value as plain text",
            extra_data={"user_id": user_id, "key": data["key"]},
            module_name="Settings",
        )
        config_data["value"] = data["value"]

    # Create new configuration
    new_config = GlobalConfiguration(**config_data)

    try:
        # Save to database
        db.session.add(new_config)
        db.session.commit()

        log_business_logic(
            "Global configuration created successfully",
            extra_data={
                "user_id": user_id,
                "key": data["key"],
                "config_id": new_config.id,
            },
            module_name="Settings",
        )

        return (
            jsonify(
                {
                    "message": f"Configuration '{data['key']}' created successfully",
                    "configuration": new_config.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        log_error(e, module_name="Settings")
        return jsonify({"error": f"Failed to create configuration: {str(e)}"}), 500


@settings.route("/api/v1/settings/global/<string:key>", methods=["PUT"])
@api_token_required
def update_global_config(key):
    """Update an existing global configuration setting - admin only"""
    user_id = g.current_user.id
    data = request.get_json()

    log_api_call(
        "/api/v1/settings/global/<key>",
        "PUT",
        user_id=user_id,
        extra_data={
            "operation": "update_global_config",
            "key": key,
            "is_admin": g.current_user.is_admin,
            "fields_to_update": list(data.keys()) if data else [],
        },
    )

    # Check if user is admin
    if not g.current_user.is_admin:
        log_debug(
            "Access denied: non-admin user attempted to update global config",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": "Admin privileges required"}), 403

    # Validate required fields
    if "value" not in data:
        log_debug(
            "Validation failed: missing value field",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": "Value is required"}), 400

    # Find the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()
    if not config:
        log_debug(
            "Global configuration not found for update",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    log_debug(
        "Updating global configuration",
        extra_data={
            "user_id": user_id,
            "key": key,
            "config_id": config.id,
            "fields_to_update": list(data.keys()),
        },
        module_name="Settings",
    )

    # Update configuration
    if "description" in data:
        config.description = data["description"]

    if "is_encrypted" in data:
        config.is_encrypted = data["is_encrypted"]

    # Update and encrypt the value if needed
    if config.is_encrypted:
        log_debug(
            "Encrypting updated configuration value",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        config.value = encrypt_value(data["value"])
    else:
        log_debug(
            "Storing updated configuration value as plain text",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        config.value = data["value"]

    try:
        # Save to database
        db.session.commit()

        log_business_logic(
            "Global configuration updated successfully",
            extra_data={"user_id": user_id, "key": key, "config_id": config.id},
            module_name="Settings",
        )

        return (
            jsonify(
                {
                    "message": f"Configuration '{key}' updated successfully",
                    "configuration": config.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        log_error(e, module_name="Settings")
        return jsonify({"error": f"Failed to update configuration: {str(e)}"}), 500


@settings.route("/api/v1/settings/global/<string:key>", methods=["DELETE"])
@api_token_required
def delete_global_config(key):
    """Delete a global configuration setting - admin only"""
    user_id = g.current_user.id

    log_api_call(
        "/api/v1/settings/global/<key>",
        "DELETE",
        user_id=user_id,
        extra_data={
            "operation": "delete_global_config",
            "key": key,
            "is_admin": g.current_user.is_admin,
        },
    )

    # Check if user is admin
    if not g.current_user.is_admin:
        log_debug(
            "Access denied: non-admin user attempted to delete global config",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": "Admin privileges required"}), 403

    # Find the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()
    if not config:
        log_debug(
            "Global configuration not found for deletion",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    log_debug(
        "Deleting global configuration",
        extra_data={"user_id": user_id, "key": key, "config_id": config.id},
        module_name="Settings",
    )

    try:
        # Delete the configuration
        db.session.delete(config)
        db.session.commit()

        log_business_logic(
            "Global configuration deleted successfully",
            extra_data={"user_id": user_id, "key": key, "config_id": config.id},
            module_name="Settings",
        )

        return jsonify({"message": f"Configuration '{key}' deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        log_error(e, module_name="Settings")
        return jsonify({"error": f"Failed to delete configuration: {str(e)}"}), 500


@settings.route("/api/v1/settings/global/<string:key>/value", methods=["GET"])
@api_token_required
def get_decrypted_value(key):
    """Get the decrypted value of a configuration setting - admin only"""
    user_id = g.current_user.id

    log_api_call(
        "/api/v1/settings/global/<key>/value",
        "GET",
        user_id=user_id,
        extra_data={
            "operation": "get_decrypted_value",
            "key": key,
            "is_admin": g.current_user.is_admin,
        },
    )

    # Check if user is admin
    if not g.current_user.is_admin:
        log_debug(
            "Access denied: non-admin user attempted to access decrypted value",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": "Admin privileges required"}), 403

    # Find the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()
    if not config:
        log_debug(
            "Global configuration not found for decryption",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    log_debug(
        "Retrieving configuration value",
        extra_data={
            "user_id": user_id,
            "key": key,
            "is_encrypted": config.is_encrypted,
        },
        module_name="Settings",
    )

    # Return the decrypted value if encrypted
    if config.is_encrypted:
        log_debug(
            "Decrypting configuration value",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        decrypted_value = decrypt_value(config.value)
        if decrypted_value is None:
            log_error(
                Exception("Failed to decrypt configuration value"),
                module_name="Settings",
            )
            return jsonify({"error": "Failed to decrypt value"}), 500
        value = decrypted_value
    else:
        log_debug(
            "Returning plain text configuration value",
            extra_data={"user_id": user_id, "key": key},
            module_name="Settings",
        )
        value = config.value

    log_debug(
        "Configuration value retrieved successfully",
        extra_data={"user_id": user_id, "key": key},
        module_name="Settings",
    )

    return jsonify({"key": key, "value": value}), 200
