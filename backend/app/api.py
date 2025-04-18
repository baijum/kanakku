from flask import Blueprint, jsonify
from werkzeug.exceptions import MethodNotAllowed
from flask_wtf.csrf import generate_csrf

api = Blueprint("api", __name__)


# Health check endpoint
@api.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@api.route("/api/v1/csrf-token", methods=["GET"])
def get_csrf_token():
    """Get a CSRF token for the current session"""
    token = generate_csrf()
    return jsonify({"csrf_token": token})


@api.errorhandler(MethodNotAllowed)
def handle_405_error(e):
    return jsonify({"error": "Method not allowed"}), 405


# Remove all other duplicate/mocked endpoints below this line
