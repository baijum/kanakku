"""
Unified transaction processing service.

Consolidates transaction logic from backend and provides consistent
interface for transaction operations across modules.
"""

from typing import Dict
from datetime import datetime, timezone
from decimal import Decimal

from .base import BaseService, ServiceResult, require_user_context, log_service_call


class TransactionService(BaseService):
    """Unified service for transaction processing and management."""

    @require_user_context
    @log_service_call("create_transaction")
    def create_transaction(self, transaction_data: Dict) -> ServiceResult:
        """
        Create a new transaction.
        Consolidates logic from backend/app/transactions_bp/services.py
        """
        try:
            # Validate transaction data
            validation_result = self._validate_transaction_data(transaction_data)
            if not validation_result.success:
                return validation_result

            # Create transaction
            with self.transaction_scope():
                transaction = self._create_transaction_record(transaction_data)

                return ServiceResult.success_result(
                    data=(
                        transaction.to_dict()
                        if hasattr(transaction, "to_dict")
                        else transaction
                    ),
                    metadata={"operation": "created", "transaction_id": transaction.id},
                )

        except Exception as e:
            self.logger.error(f"Failed to create transaction: {e}")
            return ServiceResult.error_result(
                f"Failed to create transaction: {str(e)}",
                error_code="TRANSACTION_CREATE_FAILED",
            )

    @require_user_context
    @log_service_call("get_transaction")
    def get_transaction(self, transaction_id: int) -> ServiceResult:
        """Get a transaction by ID."""
        try:
            from shared.imports import Transaction

            transaction = (
                self.session.query(Transaction)
                .filter_by(id=transaction_id, user_id=self.user_id)
                .first()
            )

            if not transaction:
                return ServiceResult.error_result(
                    "Transaction not found", error_code="TRANSACTION_NOT_FOUND"
                )

            return ServiceResult.success_result(
                data=(
                    transaction.to_dict()
                    if hasattr(transaction, "to_dict")
                    else transaction
                )
            )

        except Exception as e:
            self.logger.error(f"Failed to get transaction {transaction_id}: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve transaction",
                error_code="TRANSACTION_RETRIEVAL_FAILED",
            )

    @require_user_context
    @log_service_call("update_transaction")
    def update_transaction(
        self, transaction_id: int, update_data: Dict
    ) -> ServiceResult:
        """Update an existing transaction."""
        try:
            from shared.imports import Transaction

            # Get existing transaction
            transaction = (
                self.session.query(Transaction)
                .filter_by(id=transaction_id, user_id=self.user_id)
                .first()
            )

            if not transaction:
                return ServiceResult.error_result(
                    "Transaction not found", error_code="TRANSACTION_NOT_FOUND"
                )

            # Validate update data
            validation_result = self._validate_transaction_data(
                update_data, is_update=True
            )
            if not validation_result.success:
                return validation_result

            # Update transaction
            with self.transaction_scope():
                self._update_transaction_record(transaction, update_data)

                return ServiceResult.success_result(
                    data=(
                        transaction.to_dict()
                        if hasattr(transaction, "to_dict")
                        else transaction
                    ),
                    metadata={"operation": "updated", "transaction_id": transaction.id},
                )

        except Exception as e:
            self.logger.error(f"Failed to update transaction {transaction_id}: {e}")
            return ServiceResult.error_result(
                f"Failed to update transaction: {str(e)}",
                error_code="TRANSACTION_UPDATE_FAILED",
            )

    @require_user_context
    @log_service_call("delete_transaction")
    def delete_transaction(self, transaction_id: int) -> ServiceResult:
        """Delete a transaction."""
        try:
            from shared.imports import Transaction

            transaction = (
                self.session.query(Transaction)
                .filter_by(id=transaction_id, user_id=self.user_id)
                .first()
            )

            if not transaction:
                return ServiceResult.error_result(
                    "Transaction not found", error_code="TRANSACTION_NOT_FOUND"
                )

            with self.transaction_scope():
                self.session.delete(transaction)

                return ServiceResult.success_result(
                    data={"deleted": True},
                    metadata={"operation": "deleted", "transaction_id": transaction_id},
                )

        except Exception as e:
            self.logger.error(f"Failed to delete transaction {transaction_id}: {e}")
            return ServiceResult.error_result(
                f"Failed to delete transaction: {str(e)}",
                error_code="TRANSACTION_DELETE_FAILED",
            )

    @require_user_context
    @log_service_call("list_transactions")
    def list_transactions(
        self, filters: Dict = None, page: int = 1, per_page: int = 20
    ) -> ServiceResult:
        """List transactions with optional filtering and pagination."""
        try:
            from shared.imports import Transaction

            query = self.session.query(Transaction).filter_by(user_id=self.user_id)

            # Apply filters
            if filters:
                query = self._apply_transaction_filters(query, filters)

            # Apply pagination
            total_count = query.count()
            transactions = query.offset((page - 1) * per_page).limit(per_page).all()

            # Convert to dict format
            transaction_list = []
            for transaction in transactions:
                if hasattr(transaction, "to_dict"):
                    transaction_list.append(transaction.to_dict())
                else:
                    transaction_list.append(transaction)

            return ServiceResult.success_result(
                data=transaction_list,
                metadata={
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_count": total_count,
                        "total_pages": (total_count + per_page - 1) // per_page,
                    },
                    "filters_applied": bool(filters),
                },
            )

        except Exception as e:
            self.logger.error(f"Failed to list transactions: {e}")
            return ServiceResult.error_result(
                "Failed to retrieve transactions", error_code="TRANSACTION_LIST_FAILED"
            )

    @require_user_context
    @log_service_call("process_email_transaction")
    def process_email_transaction(self, email_data: Dict) -> ServiceResult:
        """
        Process a transaction from email data.
        Consolidates logic from banktransactions modules.
        """
        try:
            # Extract transaction details from email
            from shared.imports import extract_transaction_details

            transaction_details = extract_transaction_details(
                email_data.get("body", "")
            )
            if not transaction_details:
                return ServiceResult.error_result(
                    "Failed to extract transaction details from email",
                    error_code="EMAIL_EXTRACTION_FAILED",
                )

            # Construct transaction data
            transaction_data = self._construct_transaction_from_email(
                transaction_details, email_data
            )

            # Create the transaction
            return self.create_transaction(transaction_data)

        except Exception as e:
            self.logger.error(f"Failed to process email transaction: {e}")
            return ServiceResult.error_result(
                f"Failed to process email transaction: {str(e)}",
                error_code="EMAIL_TRANSACTION_FAILED",
            )

    # Private helper methods
    def _validate_transaction_data(
        self, data: Dict, is_update: bool = False
    ) -> ServiceResult:
        """Validate transaction data."""
        required_fields = ["amount", "description"] if not is_update else []
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return ServiceResult.error_result(
                f"Missing required fields: {', '.join(missing_fields)}",
                error_code="VALIDATION_FAILED",
            )

        # Validate amount
        if "amount" in data:
            try:
                amount = Decimal(str(data["amount"]))
                if amount == 0:
                    return ServiceResult.error_result(
                        "Transaction amount cannot be zero", error_code="INVALID_AMOUNT"
                    )
            except (ValueError, TypeError, Exception):
                return ServiceResult.error_result(
                    "Invalid amount format", error_code="INVALID_AMOUNT_FORMAT"
                )

        return ServiceResult.success_result()

    def _create_transaction_record(self, data: Dict):
        """Create a new transaction record."""
        from shared.imports import Transaction

        transaction = Transaction(
            user_id=self.user_id,
            amount=Decimal(str(data["amount"])),
            description=data["description"],
            date=data.get("date", datetime.now(timezone.utc)),
            account_id=data.get("account_id"),
            book_id=data.get("book_id"),
            category=data.get("category"),
            reference=data.get("reference"),
            notes=data.get("notes"),
        )

        self.session.add(transaction)
        self.session.flush()  # Get the ID

        return transaction

    def _update_transaction_record(self, transaction, data: Dict):
        """Update an existing transaction record."""
        updatable_fields = [
            "amount",
            "description",
            "date",
            "account_id",
            "book_id",
            "category",
            "reference",
            "notes",
        ]

        for field in updatable_fields:
            if field in data:
                if field == "amount":
                    setattr(transaction, field, Decimal(str(data[field])))
                else:
                    setattr(transaction, field, data[field])

        transaction.updated_at = datetime.now(timezone.utc)

    def _apply_transaction_filters(self, query, filters: Dict):
        """Apply filters to transaction query."""
        from shared.imports import Transaction

        if "start_date" in filters:
            query = query.filter(Transaction.date >= filters["start_date"])

        if "end_date" in filters:
            query = query.filter(Transaction.date <= filters["end_date"])

        if "account_id" in filters:
            query = query.filter(Transaction.account_id == filters["account_id"])

        if "book_id" in filters:
            query = query.filter(Transaction.book_id == filters["book_id"])

        if "category" in filters:
            query = query.filter(Transaction.category.ilike(f"%{filters['category']}%"))

        if "description" in filters:
            query = query.filter(
                Transaction.description.ilike(f"%{filters['description']}%")
            )

        if "min_amount" in filters:
            query = query.filter(
                Transaction.amount >= Decimal(str(filters["min_amount"]))
            )

        if "max_amount" in filters:
            query = query.filter(
                Transaction.amount <= Decimal(str(filters["max_amount"]))
            )

        return query

    def _construct_transaction_from_email(
        self, transaction_details: Dict, email_data: Dict
    ) -> Dict:
        """Construct transaction data from email extraction results."""
        return {
            "amount": transaction_details.get("amount"),
            "description": transaction_details.get("description", "Email transaction"),
            "date": transaction_details.get("date", datetime.now(timezone.utc)),
            "category": transaction_details.get("category"),
            "reference": transaction_details.get("reference"),
            "notes": f"Processed from email: {email_data.get('subject', 'Unknown subject')}",
            "account_id": transaction_details.get("account_id"),
            "book_id": email_data.get("book_id"),  # From user context
        }
