from flask import Blueprint, jsonify
from werkzeug.exceptions import MethodNotAllowed

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@errors.app_errorhandler(500)
def internal_error(error):
    # You might want to rollback the session here in a real app
    # from .extensions import db
    # db.session.rollback()
    return jsonify({"error": "Internal Server Error"}), 500


@errors.app_errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


# Add a test route to trigger an error
@errors.route("/api/test/error")
def trigger_error():
    raise Exception("This is a test exception")
