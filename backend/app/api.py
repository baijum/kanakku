from flask import Blueprint, jsonify
from werkzeug.exceptions import MethodNotAllowed

api = Blueprint("api", __name__)


# Health check endpoint
@api.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@api.errorhandler(MethodNotAllowed)
def handle_405_error(e):
    return jsonify({"error": "Method not allowed"}), 405


# Remove all other duplicate/mocked endpoints below this line
