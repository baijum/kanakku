from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .auth import get_current_user
from .extensions import db
from .models import BankAccountMapping, Book, ExpenseAccountMapping

mappings_bp = Blueprint("mappings", __name__)


@mappings_bp.route("/api/v1/bank-account-mappings", methods=["GET"])
@jwt_required()
def get_bank_account_mappings():
    """Get all bank account mappings for the current user's active book"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    book_id = request.args.get("book_id", current_user.active_book_id)
    if not book_id:
        return jsonify({"error": "No active book selected"}), 400

    mappings = BankAccountMapping.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).all()

    return (
        jsonify({"bank_account_mappings": [mapping.to_dict() for mapping in mappings]}),
        200,
    )


@mappings_bp.route("/api/v1/bank-account-mappings", methods=["POST"])
@jwt_required()
def create_bank_account_mapping():
    """Create a new bank account mapping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    book_id = data.get("book_id", current_user.active_book_id)
    if not book_id:
        return (
            jsonify({"error": "No book ID provided and no active book selected"}),
            400,
        )

    # Check if book exists and belongs to user
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({"error": "Book not found or unauthorized"}), 404

    # Create new mapping
    try:
        new_mapping = BankAccountMapping(
            user_id=current_user.id,
            book_id=book_id,
            account_identifier=data.get("account_identifier"),
            ledger_account=data.get("ledger_account"),
            description=data.get("description"),
        )

        db.session.add(new_mapping)
        db.session.commit()
        return jsonify(new_mapping.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating bank account mapping: {str(e)}")
        return jsonify({"error": "Failed to create mapping"}), 500


@mappings_bp.route("/api/v1/bank-account-mappings/<int:mapping_id>", methods=["PUT"])
@jwt_required()
def update_bank_account_mapping(mapping_id):
    """Update an existing bank account mapping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    # Find mapping and check ownership
    mapping = BankAccountMapping.query.filter_by(
        id=mapping_id, user_id=current_user.id
    ).first()
    if not mapping:
        return jsonify({"error": "Mapping not found or unauthorized"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Update fields if provided
        if "account_identifier" in data:
            mapping.account_identifier = data["account_identifier"]
        if "ledger_account" in data:
            mapping.ledger_account = data["ledger_account"]
        if "description" in data:
            mapping.description = data["description"]

        db.session.commit()
        return jsonify(mapping.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating bank account mapping: {str(e)}")
        return jsonify({"error": "Failed to update mapping"}), 500


@mappings_bp.route("/api/v1/bank-account-mappings/<int:mapping_id>", methods=["DELETE"])
@jwt_required()
def delete_bank_account_mapping(mapping_id):
    """Delete a bank account mapping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    mapping = BankAccountMapping.query.filter_by(
        id=mapping_id, user_id=current_user.id
    ).first()
    if not mapping:
        return jsonify({"error": "Mapping not found or unauthorized"}), 404

    try:
        db.session.delete(mapping)
        db.session.commit()
        return jsonify({"message": "Mapping deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting bank account mapping: {str(e)}")
        return jsonify({"error": "Failed to delete mapping"}), 500


@mappings_bp.route("/api/v1/expense-account-mappings", methods=["GET"])
@jwt_required()
def get_expense_account_mappings():
    """Get all expense account mappings for the current user's active book"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    book_id = request.args.get("book_id", current_user.active_book_id)
    if not book_id:
        return jsonify({"error": "No active book selected"}), 400

    mappings = ExpenseAccountMapping.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).all()

    return (
        jsonify(
            {"expense_account_mappings": [mapping.to_dict() for mapping in mappings]}
        ),
        200,
    )


@mappings_bp.route("/api/v1/expense-account-mappings", methods=["POST"])
@jwt_required()
def create_expense_account_mapping():
    """Create a new expense account mapping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    book_id = data.get("book_id", current_user.active_book_id)
    if not book_id:
        return (
            jsonify({"error": "No book ID provided and no active book selected"}),
            400,
        )

    # Check if book exists and belongs to user
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({"error": "Book not found or unauthorized"}), 404

    # Create new mapping
    try:
        new_mapping = ExpenseAccountMapping(
            user_id=current_user.id,
            book_id=book_id,
            merchant_name=data.get("merchant_name"),
            ledger_account=data.get("ledger_account"),
            description=data.get("description"),
        )

        db.session.add(new_mapping)
        db.session.commit()
        return jsonify(new_mapping.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating expense account mapping: {str(e)}")
        return jsonify({"error": "Failed to create mapping"}), 500


@mappings_bp.route("/api/v1/expense-account-mappings/<int:mapping_id>", methods=["PUT"])
@jwt_required()
def update_expense_account_mapping(mapping_id):
    """Update an existing expense account mapping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    # Find mapping and check ownership
    mapping = ExpenseAccountMapping.query.filter_by(
        id=mapping_id, user_id=current_user.id
    ).first()
    if not mapping:
        return jsonify({"error": "Mapping not found or unauthorized"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Update fields if provided
        if "merchant_name" in data:
            mapping.merchant_name = data["merchant_name"]
        if "ledger_account" in data:
            mapping.ledger_account = data["ledger_account"]
        if "description" in data:
            mapping.description = data["description"]

        db.session.commit()
        return jsonify(mapping.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating expense account mapping: {str(e)}")
        return jsonify({"error": "Failed to update mapping"}), 500


@mappings_bp.route(
    "/api/v1/expense-account-mappings/<int:mapping_id>", methods=["DELETE"]
)
@jwt_required()
def delete_expense_account_mapping(mapping_id):
    """Delete an expense account mapping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    mapping = ExpenseAccountMapping.query.filter_by(
        id=mapping_id, user_id=current_user.id
    ).first()
    if not mapping:
        return jsonify({"error": "Mapping not found or unauthorized"}), 404

    try:
        db.session.delete(mapping)
        db.session.commit()
        return jsonify({"message": "Mapping deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting expense account mapping: {str(e)}")
        return jsonify({"error": "Failed to delete mapping"}), 500


# Additional endpoints for bulk operations


@mappings_bp.route("/api/v1/mappings/import", methods=["POST"])
@jwt_required()
def import_mappings():
    """Import mappings from TOML-like structure"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    book_id = data.get("book_id", current_user.active_book_id)
    if not book_id:
        return (
            jsonify({"error": "No book ID provided and no active book selected"}),
            400,
        )

    # Check if book exists and belongs to user
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({"error": "Book not found or unauthorized"}), 404

    bank_account_map = data.get("bank-account-map", {})
    expense_account_map = data.get("expense-account-map", {})

    try:
        # Import bank account mappings
        for account_id, ledger_account in bank_account_map.items():
            # Check if mapping already exists
            existing = BankAccountMapping.query.filter_by(
                user_id=current_user.id, book_id=book_id, account_identifier=account_id
            ).first()

            if existing:
                existing.ledger_account = ledger_account
            else:
                new_mapping = BankAccountMapping(
                    user_id=current_user.id,
                    book_id=book_id,
                    account_identifier=account_id,
                    ledger_account=ledger_account,
                )
                db.session.add(new_mapping)

        # Import expense account mappings
        for merchant, values in expense_account_map.items():
            # In TOML format, values is a list with [ledger_account, description]
            if isinstance(values, list) and len(values) >= 1:
                ledger_account = values[0]
                description = values[1] if len(values) > 1 else None

                # Check if mapping already exists
                existing = ExpenseAccountMapping.query.filter_by(
                    user_id=current_user.id, book_id=book_id, merchant_name=merchant
                ).first()

                if existing:
                    existing.ledger_account = ledger_account
                    existing.description = description
                else:
                    new_mapping = ExpenseAccountMapping(
                        user_id=current_user.id,
                        book_id=book_id,
                        merchant_name=merchant,
                        ledger_account=ledger_account,
                        description=description,
                    )
                    db.session.add(new_mapping)

        db.session.commit()
        return jsonify({"message": "Mappings imported successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error importing mappings: {str(e)}")
        return jsonify({"error": "Failed to import mappings"}), 500


@mappings_bp.route("/api/v1/mappings/export", methods=["GET"])
@jwt_required()
def export_mappings():
    """Export mappings to TOML-like structure"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    book_id = request.args.get("book_id", current_user.active_book_id)
    if not book_id:
        return jsonify({"error": "No active book selected"}), 400

    try:
        # Get all bank account mappings for this book
        bank_mappings = BankAccountMapping.query.filter_by(
            user_id=current_user.id, book_id=book_id
        ).all()

        # Get all expense account mappings for this book
        expense_mappings = ExpenseAccountMapping.query.filter_by(
            user_id=current_user.id, book_id=book_id
        ).all()

        # Construct the response in TOML-like format
        bank_account_map = {}
        for mapping in bank_mappings:
            bank_account_map[mapping.account_identifier] = mapping.ledger_account

        expense_account_map = {}
        for mapping in expense_mappings:
            expense_account_map[mapping.merchant_name] = [
                mapping.ledger_account,
                mapping.description or "",
            ]

        return (
            jsonify(
                {
                    "bank-account-map": bank_account_map,
                    "expense-account-map": expense_account_map,
                }
            ),
            200,
        )
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error exporting mappings: {str(e)}")
        return jsonify({"error": "Failed to export mappings"}), 500
