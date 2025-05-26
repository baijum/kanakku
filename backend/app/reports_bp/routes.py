from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError

from ..extensions import api_token_required
from .schemas import BalanceReportSchema, RegisterReportSchema
from .services import ReportsService

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/v1/reports/balance", methods=["GET"])
@api_token_required
def get_balance():
    """Get balance report, optionally filtered by account and limited by depth"""
    try:
        # Validate query parameters
        schema = BalanceReportSchema()
        validated_data = schema.load(request.args)

        # Use service layer
        result = ReportsService.get_balance_report(
            account=validated_data.get("account"),
            depth=validated_data.get("depth"),
            book_id=validated_data.get("book_id"),
        )

        return jsonify(result)

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Balance report error: {e}")
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/api/v1/reports/register", methods=["GET"])
@api_token_required
def get_register():
    """Get transaction register, optionally filtered by account and limited by count"""
    try:
        # Validate query parameters
        schema = RegisterReportSchema()
        validated_data = schema.load(request.args)

        # Use service layer
        result = ReportsService.get_register_report(
            account=validated_data.get("account"), limit=validated_data.get("limit")
        )

        return jsonify(result)

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Register report error: {e}")
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/api/v1/reports/balance_report", methods=["GET"])
@api_token_required
def get_balance_report():
    """Get a full balance report for all accounts"""
    try:
        # Use service layer
        result = ReportsService.get_full_balance_report()

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Balance report error: {e}")
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/api/v1/reports/income_statement", methods=["GET"])
@api_token_required
def get_income_statement():
    """Generate an income statement (Income vs Expenses)"""
    try:
        # Use service layer
        result = ReportsService.get_income_statement()

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Income statement error: {e}")
        return jsonify({"error": str(e)}), 500
