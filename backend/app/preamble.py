import logging

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from .extensions import api_token_required
from .models import Preamble, db

preamble = Blueprint("preamble", __name__)


@preamble.route("/api/v1/preambles", methods=["GET"])
@api_token_required
def get_preambles():
    """Return all preambles for the logged-in user."""
    try:
        user = g.current_user
        preambles = Preamble.query.filter_by(user_id=user.id).all()
        return jsonify({"preambles": [p.to_dict() for p in preambles]})
    except Exception as e:
        logging.error(f"Error getting preambles: {e}")
        return jsonify({"error": "Failed to retrieve preambles"}), 500


@preamble.route("/api/v1/preambles/<int:preamble_id>", methods=["GET"])
@api_token_required
def get_preamble(preamble_id):
    """Return a specific preamble by ID."""
    try:
        user = g.current_user
        preamble = Preamble.query.filter_by(id=preamble_id, user_id=user.id).first()
        if not preamble:
            return jsonify({"error": "Preamble not found"}), 404
        return jsonify(preamble.to_dict())
    except Exception as e:
        logging.error(f"Error getting preamble: {e}")
        return jsonify({"error": "Failed to retrieve preamble"}), 500


@preamble.route("/api/v1/preambles/name/<string:name>", methods=["GET"])
@api_token_required
def get_preamble_by_name(name):
    """Return a specific preamble by name."""
    try:
        user = g.current_user
        preamble = Preamble.query.filter_by(name=name, user_id=user.id).first()
        if not preamble:
            return jsonify({"error": "Preamble not found"}), 404
        return jsonify(preamble.to_dict())
    except Exception as e:
        logging.error(f"Error getting preamble by name: {e}")
        return jsonify({"error": "Failed to retrieve preamble"}), 500


@preamble.route("/api/v1/preambles", methods=["POST"])
@api_token_required
def create_preamble():
    """Create a new preamble."""
    user = g.current_user
    data = request.json

    if not data or not data.get("name") or not data.get("content"):
        return jsonify({"error": "Name and content are required"}), 400

    is_default = data.get("is_default", False)

    try:
        # If setting as default, unset any existing defaults
        if is_default:
            existing_defaults = Preamble.query.filter_by(
                user_id=user.id, is_default=True
            ).all()
            for p in existing_defaults:
                p.is_default = False

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
    except IntegrityError as e:
        db.session.rollback()
        # Log the original error for debugging
        logging.error(f"IntegrityError encountered. Original error: {e.orig}")
        # Check if the error is the unique constraint violation for user_id and name
        error_str = str(e.orig).lower()
        if (
            "unique constraint failed" in error_str
            and "preamble.user_id" in error_str
            and "preamble.name" in error_str
        ):
            return (
                jsonify(
                    {"message": "Preamble with this name already exists for this user"}
                ),
                400,
            )
        else:
            logging.error(f"Integrity error creating preamble: {e}")
            return jsonify({"message": "Database integrity error"}), 500
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating preamble: {e}")
        # Use 'message' key for consistency
        return jsonify({"message": "Failed to create preamble"}), 500


@preamble.route("/api/v1/preambles/<int:preamble_id>", methods=["PUT"])
@api_token_required
def update_preamble(preamble_id):
    """Update an existing preamble."""
    user = g.current_user
    preamble = Preamble.query.filter_by(id=preamble_id, user_id=user.id).first()
    if not preamble:
        return jsonify({"message": "Preamble not found"}), 404

    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400

    try:
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
    except IntegrityError as e:
        db.session.rollback()
        # Log the original error for debugging
        logging.error(f"IntegrityError encountered. Original error: {e.orig}")
        # Check if the error is the unique constraint violation for user_id and name
        error_str = str(e.orig).lower()
        if (
            "unique constraint failed" in error_str
            and "preamble.user_id" in error_str
            and "preamble.name" in error_str
        ):
            return (
                jsonify(
                    {"message": "Preamble with this name already exists for this user"}
                ),
                400,
            )
        else:
            logging.error(f"Integrity error updating preamble: {e}")
            return jsonify({"message": "Database integrity error"}), 500
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating preamble: {e}")
        # Use 'message' key for consistency
        return jsonify({"message": "Failed to update preamble"}), 500


@preamble.route("/api/v1/preambles/<int:preamble_id>", methods=["DELETE"])
@api_token_required
def delete_preamble(preamble_id):
    """Delete a preamble."""
    try:
        user = g.current_user
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
@api_token_required
def get_default_preamble():
    """Return the default preamble for the logged-in user."""
    try:
        user = g.current_user
        preamble = Preamble.query.filter_by(user_id=user.id, is_default=True).first()
        if not preamble:
            return jsonify({"error": "No default preamble found"}), 404
        return jsonify(preamble.to_dict())
    except Exception as e:
        logging.error(f"Error getting default preamble: {e}")
        return jsonify({"error": "Failed to retrieve default preamble"}), 500
