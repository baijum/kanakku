from flask import Blueprint, jsonify, request, g
from .models import GlobalConfiguration, db
from .auth import api_token_required
from .utils.encryption import encrypt_value, decrypt_value

settings = Blueprint("settings", __name__)


@settings.route("/api/v1/settings/global", methods=["GET"])
@api_token_required
def get_all_global_configs():
    """Get all global configuration settings - admin only"""
    # Check if user is admin
    if not g.current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    # Query all configuration entries
    configs = GlobalConfiguration.query.all()

    # Convert to list of dictionaries
    config_list = [config.to_dict() for config in configs]

    return jsonify({"configurations": config_list}), 200


@settings.route("/api/v1/settings/global/<string:key>", methods=["GET"])
@api_token_required
def get_global_config(key):
    """Get a specific global configuration setting - admin only"""
    # Check if user is admin
    if not g.current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    # Query the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()

    if not config:
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    return jsonify({"configuration": config.to_dict()}), 200


@settings.route("/api/v1/settings/global", methods=["POST"])
@api_token_required
def create_global_config():
    """Create a new global configuration setting - admin only"""
    # Check if user is admin
    if not g.current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    # Get request data
    data = request.get_json()

    # Validate required fields
    if not data.get("key") or not data.get("value"):
        return jsonify({"error": "Key and value are required fields"}), 400

    # Check for existing configuration with same key
    existing_config = GlobalConfiguration.query.filter_by(key=data["key"]).first()
    if existing_config:
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
        config_data["value"] = encrypt_value(data["value"])
    else:
        config_data["value"] = data["value"]

    # Create new configuration
    new_config = GlobalConfiguration(**config_data)

    # Save to database
    db.session.add(new_config)
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Configuration '{data['key']}' created successfully",
                "configuration": new_config.to_dict(),
            }
        ),
        201,
    )


@settings.route("/api/v1/settings/global/<string:key>", methods=["PUT"])
@api_token_required
def update_global_config(key):
    """Update an existing global configuration setting - admin only"""
    # Check if user is admin
    if not g.current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    # Get request data
    data = request.get_json()

    # Validate required fields
    if "value" not in data:
        return jsonify({"error": "Value is required"}), 400

    # Find the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()
    if not config:
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    # Update configuration
    if "description" in data:
        config.description = data["description"]

    if "is_encrypted" in data:
        config.is_encrypted = data["is_encrypted"]

    # Update and encrypt the value if needed
    if config.is_encrypted:
        config.value = encrypt_value(data["value"])
    else:
        config.value = data["value"]

    # Save to database
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Configuration '{key}' updated successfully",
                "configuration": config.to_dict(),
            }
        ),
        200,
    )


@settings.route("/api/v1/settings/global/<string:key>", methods=["DELETE"])
@api_token_required
def delete_global_config(key):
    """Delete a global configuration setting - admin only"""
    # Check if user is admin
    if not g.current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    # Find the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()
    if not config:
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    # Delete the configuration
    db.session.delete(config)
    db.session.commit()

    return jsonify({"message": f"Configuration '{key}' deleted successfully"}), 200


@settings.route("/api/v1/settings/global/<string:key>/value", methods=["GET"])
@api_token_required
def get_decrypted_value(key):
    """Get the decrypted value of a configuration setting - admin only"""
    # Check if user is admin
    if not g.current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    # Find the configuration
    config = GlobalConfiguration.query.filter_by(key=key).first()
    if not config:
        return jsonify({"error": f"Configuration with key '{key}' not found"}), 404

    # Return the decrypted value if encrypted
    if config.is_encrypted:
        decrypted_value = decrypt_value(config.value)
        if decrypted_value is None:
            return jsonify({"error": "Failed to decrypt value"}), 500
        value = decrypted_value
    else:
        value = config.value

    return jsonify({"key": key, "value": value}), 200
