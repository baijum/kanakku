import json
import os
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from .extensions import api_token_required, db
from .models import EmailConfiguration
from .utils.encryption import encrypt_value
from .utils.logging_utils import log_api_call, log_business_logic, log_debug, log_error

# Import unified services
try:
    from shared.imports import EmailProcessingService
except ImportError:
    EmailProcessingService = None

email_automation = Blueprint("email_automation", __name__)


@email_automation.route("/api/v1/email-automation/config", methods=["GET"])
@api_token_required
def get_email_config():
    """Get the current user's email automation configuration"""
    user_id = g.current_user.id

    log_api_call(
        "/api/v1/email-automation/config",
        "GET",
        user_id=user_id,
        extra_data={"operation": "get_email_config"},
    )

    # Use service layer if available, otherwise fallback to direct DB access
    if EmailProcessingService:
        log_debug(
            "Using EmailProcessingService for configuration retrieval",
            extra_data={"user_id": user_id},
            module_name="EmailAutomation",
        )

        service = EmailProcessingService(user_id=user_id)
        result = service.get_email_configuration()

        if result.success:
            log_debug(
                "Email configuration retrieved successfully via service",
                extra_data={"user_id": user_id, "has_config": result.data is not None},
                module_name="EmailAutomation",
            )
            return jsonify({"config": result.data}), 200
        else:
            log_error(Exception(result.error), module_name="EmailAutomation")
            return jsonify({"error": result.error}), 500
    else:
        log_debug(
            "Using fallback direct DB access for configuration retrieval",
            extra_data={"user_id": user_id},
            module_name="EmailAutomation",
        )

        # Fallback to original implementation
        config = EmailConfiguration.query.filter_by(user_id=user_id).first()

        if not config:
            log_debug(
                "No email configuration found for user",
                extra_data={"user_id": user_id},
                module_name="EmailAutomation",
            )
            return jsonify({"config": None}), 200

        log_debug(
            "Email configuration found and returning sanitized data",
            extra_data={"user_id": user_id, "config_id": config.id},
            module_name="EmailAutomation",
        )

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

    log_api_call(
        "/api/v1/email-automation/config",
        "POST",
        user_id=user_id,
        extra_data={"operation": "create_email_config", "has_data": data is not None},
    )

    # Use service layer if available, otherwise fallback to direct DB access
    if EmailProcessingService:
        log_debug(
            "Using EmailProcessingService for configuration creation/update",
            extra_data={"user_id": user_id},
            module_name="EmailAutomation",
        )

        service = EmailProcessingService(user_id=user_id)
        result = service.update_email_configuration(data)

        if result.success:
            operation = result.metadata.get("operation", "updated")
            status_code = 201 if operation == "created" else 200

            log_business_logic(
                f"Email configuration {operation} successfully",
                extra_data={"user_id": user_id, "operation": operation},
                module_name="EmailAutomation",
            )

            return (
                jsonify(
                    {
                        "message": "Email configuration saved successfully",
                        "config": result.data,
                    }
                ),
                status_code,
            )
        else:
            log_error(Exception(result.error), module_name="EmailAutomation")
            return jsonify({"error": result.error}), 400
    else:
        log_debug(
            "Using fallback direct DB access for configuration creation/update",
            extra_data={"user_id": user_id},
            module_name="EmailAutomation",
        )

        # Fallback to original implementation
        # Validate required fields
        required_fields = ["email_address", "app_password"]
        for field in required_fields:
            if not data.get(field):
                log_debug(
                    f"Validation failed: missing required field {field}",
                    extra_data={"user_id": user_id, "field": field},
                    module_name="EmailAutomation",
                )
                return jsonify({"error": f"{field} is required"}), 400

        # Check if configuration already exists
        existing_config = EmailConfiguration.query.filter_by(user_id=user_id).first()
        is_update = existing_config is not None

        log_debug(
            f"Email configuration {'update' if is_update else 'creation'} operation",
            extra_data={
                "user_id": user_id,
                "is_update": is_update,
                "email_address": data.get("email_address"),
                "imap_server": data.get("imap_server", "imap.gmail.com"),
            },
            module_name="EmailAutomation",
        )

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

            log_business_logic(
                f"Email configuration {'updated' if is_update else 'created'} successfully",
                extra_data={"user_id": user_id, "config_id": config.id},
                module_name="EmailAutomation",
            )

            # Return config without sensitive data
            config_dict = config.to_dict()
            config_dict.pop("app_password", None)

            return jsonify(
                {
                    "message": "Email configuration saved successfully",
                    "config": config_dict,
                }
            ), (201 if not existing_config else 200)

        except Exception as e:
            db.session.rollback()
            log_error(e, module_name="EmailAutomation")
            return jsonify({"error": f"Failed to save configuration: {str(e)}"}), 500


@email_automation.route("/api/v1/email-automation/config", methods=["PUT"])
@api_token_required
def update_email_config():
    """Update the current user's email automation configuration"""
    user_id = g.current_user.id
    data = request.get_json()

    log_api_call(
        "/api/v1/email-automation/config",
        "PUT",
        user_id=user_id,
        extra_data={
            "operation": "update_email_config",
            "fields_to_update": list(data.keys()) if data else [],
        },
    )

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config:
        log_debug(
            "Email configuration not found for update",
            extra_data={"user_id": user_id},
            module_name="EmailAutomation",
        )
        return jsonify({"error": "Email configuration not found"}), 404

    log_debug(
        "Updating email configuration fields",
        extra_data={
            "user_id": user_id,
            "config_id": config.id,
            "fields_to_update": list(data.keys()) if data else [],
        },
        module_name="EmailAutomation",
    )

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

        log_business_logic(
            "Email configuration updated successfully",
            extra_data={"user_id": user_id, "config_id": config.id},
            module_name="EmailAutomation",
        )

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
        log_error(e, module_name="EmailAutomation")
        return jsonify({"error": f"Failed to update configuration: {str(e)}"}), 500


@email_automation.route("/api/v1/email-automation/config", methods=["DELETE"])
@api_token_required
def delete_email_config():
    """Delete the current user's email automation configuration"""
    user_id = g.current_user.id

    log_api_call(
        "/api/v1/email-automation/config",
        "DELETE",
        user_id=user_id,
        extra_data={"operation": "delete_email_config"},
    )

    config = EmailConfiguration.query.filter_by(user_id=user_id).first()

    if not config:
        log_debug(
            "Email configuration not found for deletion",
            extra_data={"user_id": user_id},
            module_name="EmailAutomation",
        )
        return jsonify({"error": "Email configuration not found"}), 404

    log_debug(
        "Deleting email configuration",
        extra_data={"user_id": user_id, "config_id": config.id},
        module_name="EmailAutomation",
    )

    try:
        db.session.delete(config)
        db.session.commit()

        log_business_logic(
            "Email configuration deleted successfully",
            extra_data={"user_id": user_id, "config_id": config.id},
            module_name="EmailAutomation",
        )

        return jsonify({"message": "Email configuration deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        log_error(e, module_name="EmailAutomation")
        return jsonify({"error": f"Failed to delete configuration: {str(e)}"}), 500


@email_automation.route("/api/v1/email-automation/test-connection", methods=["POST"])
@api_token_required
def test_email_connection():
    """Test the email connection with provided credentials"""
    user_id = g.current_user.id
    data = request.get_json()

    # Use service layer if available, otherwise fallback to direct implementation
    if EmailProcessingService:
        service = EmailProcessingService(user_id=user_id)
        result = service.test_email_connection(data)

        if result.success:
            return (
                jsonify(
                    {"success": True, "message": "Email connection test successful"}
                ),
                200,
            )
        else:
            return jsonify({"success": False, "error": result.error}), 400
    else:
        # Fallback to original implementation
        required_fields = ["email_address", "app_password"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        try:
            # Set up project paths and import using shared package to avoid path manipulation
            import sys
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from shared.imports import CustomIMAPClient

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
                jsonify(
                    {"success": True, "message": "Email connection test successful"}
                ),
                200,
            )

        except Exception as e:
            return (
                jsonify(
                    {"success": False, "error": f"Connection test failed: {str(e)}"}
                ),
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

    # Use service layer if available for direct processing, otherwise use job queue
    if EmailProcessingService:
        service = EmailProcessingService(user_id=user_id)
        result = service.process_user_emails()

        if result.success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Email processing completed successfully",
                        "data": result.data,
                        "metadata": result.metadata,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.error,
                        "error_code": result.error_code,
                    }
                ),
                400,
            )
    else:
        # Fallback to original job queue implementation
        config = EmailConfiguration.query.filter_by(user_id=user_id).first()

        if not config or not config.is_enabled:
            return (
                jsonify({"error": "Email automation is not configured or disabled"}),
                400,
            )

        try:
            # Set up project paths and import using shared package to avoid path manipulation
            import sys
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            import redis
            from rq import Queue

            from shared.imports import (
                generate_job_id,
                get_user_job_status,
                has_user_job_pending,
                process_user_emails_standalone,
            )

            # Connect to Redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            redis_conn = redis.from_url(redis_url)

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

            # Generate consistent job ID
            job_id = generate_job_id(user_id)

            # Enqueue email processing job using the standalone function
            job = queue.enqueue(
                process_user_emails_standalone,
                user_id,
                job_id=job_id,
                job_timeout="10m",
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
