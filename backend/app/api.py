from flask import Blueprint, jsonify
from app.models import db, User, Transaction, Account
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime

api = Blueprint("api", __name__)


# Health check endpoint
@api.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# Remove all other duplicate/mocked endpoints below this line
