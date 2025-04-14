from flask import Blueprint, jsonify, request, current_app
import logging
from flask_jwt_extended import jwt_required, current_user
from .extensions import db
from .models import Preamble

preamble = Blueprint("preamble", __name__)


@preamble.route("/api/v1/preambles", methods=["GET"])
@jwt_required()
def get_preambles():
    """Return all preambles for the logged-in user."""
    try:
        user = current_user
        preambles = Preamble.query.filter_by(user_id=user.id).all()
        return jsonify({"preambles": [p.to_dict() for p in preambles]})
    except Exception as e:
        logging.error(f"Error getting preambles: {e}")
        return jsonify({"error": "Failed to retrieve preambles"}), 500


@preamble.route("/api/v1/preambles/<int:preamble_id>", methods=["GET"])
@jwt_required()
def get_preamble(preamble_id):
    """Return a specific preamble by ID."""
    try:
        user = current_user
        preamble = Preamble.query.filter_by(id=preamble_id, user_id=user.id).first()
        if not preamble:
            return jsonify({"error": "Preamble not found"}), 404
        return jsonify(preamble.to_dict())
    except Exception as e:
        logging.error(f"Error getting preamble: {e}")
        return jsonify({"error": "Failed to retrieve preamble"}), 500


@preamble.route("/api/v1/preambles", methods=["POST"])
@jwt_required()
def create_preamble():
    """Create a new preamble."""
    try:
        user = current_user
        data = request.json

        # Validate required fields
        if not data or not data.get("name") or not data.get("content"):
            return jsonify({"error": "Name and content are required"}), 400

        # Check if this is being set as default
        is_default = data.get("is_default", False)

        # If setting as default, unset any existing defaults
        if is_default:
            existing_defaults = Preamble.query.filter_by(
                user_id=user.id, is_default=True
            ).all()
            for p in existing_defaults:
                p.is_default = False

        # Create new preamble
        new_preamble = Preamble(
            user_id=user.id,
            name=data["name"],
            content=data["content"],
            is_default=is_default,
        )

        db.session.add(new_preamble)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Preamble created successfully",
                    "preamble": new_preamble.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating preamble: {e}")
        return jsonify({"error": "Failed to create preamble"}), 500


@preamble.route("/api/v1/preambles/<int:preamble_id>", methods=["PUT"])
@jwt_required()
def update_preamble(preamble_id):
    """Update an existing preamble."""
    try:
        user = current_user
        preamble = Preamble.query.filter_by(id=preamble_id, user_id=user.id).first()
        if not preamble:
            return jsonify({"error": "Preamble not found"}), 404

        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update fields if provided
        if "name" in data:
            preamble.name = data["name"]
        if "content" in data:
            preamble.content = data["content"]

        # Handle default status
        if "is_default" in data and data["is_default"] != preamble.is_default:
            if data["is_default"]:
                # Unset any existing defaults
                existing_defaults = Preamble.query.filter_by(
                    user_id=user.id, is_default=True
                ).all()
                for p in existing_defaults:
                    p.is_default = False
            preamble.is_default = data["is_default"]

        db.session.commit()

        return jsonify(
            {"message": "Preamble updated successfully", "preamble": preamble.to_dict()}
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating preamble: {e}")
        return jsonify({"error": "Failed to update preamble"}), 500


@preamble.route("/api/v1/preambles/<int:preamble_id>", methods=["DELETE"])
@jwt_required()
def delete_preamble(preamble_id):
    """Delete a preamble."""
    try:
        user = current_user
        preamble = Preamble.query.filter_by(id=preamble_id, user_id=user.id).first()
        if not preamble:
            return jsonify({"error": "Preamble not found"}), 404

        was_default = preamble.is_default

        db.session.delete(preamble)
        db.session.commit()

        return jsonify(
            {"message": "Preamble deleted successfully", "was_default": was_default}
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting preamble: {e}")
        return jsonify({"error": "Failed to delete preamble"}), 500


@preamble.route("/api/v1/preambles/default", methods=["GET"])
@jwt_required()
def get_default_preamble():
    """Return the default preamble for the logged-in user."""
    try:
        user = current_user
        preamble = Preamble.query.filter_by(user_id=user.id, is_default=True).first()
        if not preamble:
            return jsonify({"error": "No default preamble found"}), 404
        return jsonify(preamble.to_dict())
    except Exception as e:
        logging.error(f"Error getting default preamble: {e}")
        return jsonify({"error": "Failed to retrieve default preamble"}), 500
