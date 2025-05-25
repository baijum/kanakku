import json
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from .auth import api_token_required
from .models import EmailConfiguration, db
from .utils.encryption import encrypt_value

email_automation = Blueprint("email_automation", __name__)


@email_automation.route("/api/v1/email-automation/config", methods=["GET"])
@api_token_required
def get_email_config():
    """Get the current user's email automation configuration"""
    user_id = g.current_user.id

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config:
        return jsonify({"config": None}), 200

    # Return config without sensitive data
    config_dict = config.to_dict()
    # Don't return the actual app password
    config_dict.pop("app_password", None)

    return jsonify({"config": config_dict}), 200


@email_automation.route("/api/v1/email-automation/config", methods=["POST"])
@api_token_required
def create_email_config():
    """Create or update the current user's email automation configuration"""
    user_id = g.current_user.id
    data = request.get_json()

    # Validate required fields
    required_fields = ["email_address", "app_password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # Check if configuration already exists
    existing_config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if existing_config:
        # Update existing configuration
        existing_config.is_enabled = data.get("is_enabled", False)
        existing_config.imap_server = data.get("imap_server", "imap.gmail.com")
        existing_config.imap_port = data.get("imap_port", 993)
        existing_config.email_address = data["email_address"]
        existing_config.app_password = encrypt_value(data["app_password"])
        existing_config.polling_interval = data.get("polling_interval", "hourly")
        existing_config.sample_emails = json.dumps(data.get("sample_emails", []))
        existing_config.updated_at = datetime.now(timezone.utc)

        config = existing_config
    else:
        # Create new configuration
        config = EmailConfiguration(
            user_id=user_id,
            is_enabled=data.get("is_enabled", False),
            imap_server=data.get("imap_server", "imap.gmail.com"),
            imap_port=data.get("imap_port", 993),
            email_address=data["email_address"],
            app_password=encrypt_value(data["app_password"]),
            polling_interval=data.get("polling_interval", "hourly"),
            sample_emails=json.dumps(data.get("sample_emails", [])),
        )
        db.session.add(config)

    try:
        db.session.commit()

        # Return config without sensitive data
        config_dict = config.to_dict()
        config_dict.pop("app_password", None)

        return jsonify(
            {"message": "Email configuration saved successfully", "config": config_dict}
        ), (201 if not existing_config else 200)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save configuration: {str(e)}"}), 500


@email_automation.route("/api/v1/email-automation/config", methods=["PUT"])
@api_token_required
def update_email_config():
    """Update the current user's email automation configuration"""
    user_id = g.current_user.id
    data = request.get_json()

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config:
        return jsonify({"error": "Email configuration not found"}), 404

    # Update fields if provided
    if "is_enabled" in data:
        config.is_enabled = data["is_enabled"]
    if "imap_server" in data:
        config.imap_server = data["imap_server"]
    if "imap_port" in data:
        config.imap_port = data["imap_port"]
    if "email_address" in data:
        config.email_address = data["email_address"]
    if "app_password" in data:
        config.app_password = encrypt_value(data["app_password"])
    if "polling_interval" in data:
        config.polling_interval = data["polling_interval"]
    if "sample_emails" in data:
        config.sample_emails = json.dumps(data["sample_emails"])

    config.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()

        # Return config without sensitive data
        config_dict = config.to_dict()
        config_dict.pop("app_password", None)

        return (
            jsonify(
                {
                    "message": "Email configuration updated successfully",
                    "config": config_dict,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update configuration: {str(e)}"}), 500


@email_automation.route("/api/v1/email-automation/config", methods=["DELETE"])
@api_token_required
def delete_email_config():
    """Delete the current user's email automation configuration"""
    user_id = g.current_user.id

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config:
        return jsonify({"error": "Email configuration not found"}), 404

    try:
        db.session.delete(config)
        db.session.commit()

        return jsonify({"message": "Email configuration deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete configuration: {str(e)}"}), 500


@email_automation.route("/api/v1/email-automation/test-connection", methods=["POST"])
@api_token_required
def test_email_connection():
    """Test the email connection with provided credentials"""
    data = request.get_json()

    required_fields = ["email_address", "app_password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    try:
        # Add banktransactions module to Python path
        import os
        import sys

        banktransactions_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        if banktransactions_path not in sys.path:
            sys.path.append(banktransactions_path)

        # Import here to avoid circular imports
        from banktransactions.core.imap_client import CustomIMAPClient

        imap_client = CustomIMAPClient(
            server=data.get("imap_server", "imap.gmail.com"),
            port=data.get("imap_port", 993),
            username=data["email_address"],
            password=data["app_password"],
        )

        # Test connection
        imap_client.connect()
        imap_client.disconnect()

        return (
            jsonify({"success": True, "message": "Email connection test successful"}),
            200,
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Connection test failed: {str(e)}"}),
            400,
        )


@email_automation.route("/api/v1/email-automation/status", methods=["GET"])
@api_token_required
def get_automation_status():
    """Get the current status of email automation for the user"""
    user_id = g.current_user.id

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config:
        return (
            jsonify(
                {
                    "status": "not_configured",
                    "message": "Email automation is not configured",
                }
            ),
            200,
        )

    status = {
        "status": "enabled" if config.is_enabled else "disabled",
        "last_check": (
            config.last_check_time.isoformat() if config.last_check_time else None
        ),
        "polling_interval": config.polling_interval,
        "email_address": config.email_address,
        "last_processed_email_id": config.last_processed_email_id,
    }

    return jsonify(status), 200


@email_automation.route("/api/v1/email-automation/trigger", methods=["POST"])
@api_token_required
def trigger_email_processing():
    """Manually trigger email processing for the current user"""
    user_id = g.current_user.id

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config or not config.is_enabled:
        return jsonify({"error": "Email automation is not configured or disabled"}), 400

    try:
        # Add banktransactions module to Python path
        import os
        import sys

        banktransactions_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        if banktransactions_path not in sys.path:
            sys.path.append(banktransactions_path)

        # Import here to avoid circular imports
        import redis
        from rq import Queue

        # Connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = redis.from_url(redis_url)

        # Import job utilities
        from banktransactions.automation.job_utils import (
            generate_job_id,
            get_user_job_status,
            has_user_job_pending,
        )

        # Check if user already has a pending job
        if has_user_job_pending(redis_conn, user_id):
            job_status = get_user_job_status(redis_conn, user_id)
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Email processing job already pending for this user",
                        "job_status": job_status,
                    }
                ),
                409,  # Conflict status code
            )

        # Create queue
        queue = Queue("email_processing", connection=redis_conn)

        # Import the function directly from the automation module
        from banktransactions.automation.email_processor import (
            process_user_emails_standalone,
        )

        # Generate consistent job ID
        job_id = generate_job_id(user_id)

        # Enqueue email processing job using the standalone function
        job = queue.enqueue(
            process_user_emails_standalone, user_id, job_id=job_id, job_timeout="10m"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Email processing job queued successfully",
                    "job_id": job.id,
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Failed to queue email processing job: {str(e)}",
                }
            ),
            500,
        )
