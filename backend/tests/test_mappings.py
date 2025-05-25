import json
from unittest.mock import patch

import pytest

from app.extensions import db
from app.models import BankAccountMapping, Book, ExpenseAccountMapping, User


def ensure_user_has_active_book(user, db_session):
    """Helper function to ensure user has an active book"""
    if not user.active_book_id:
        book = Book(user_id=user.id, name="Test Book")
        db_session.add(book)
        db_session.commit()
        user.active_book_id = book.id
        db_session.commit()


class TestBankAccountMappings:
    """Test bank account mapping endpoints"""

    def test_get_bank_account_mappings_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful retrieval of bank account mappings"""
        ensure_user_has_active_book(user, db_session)

        # Create a mapping
        mapping = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX1234",
            ledger_account="Assets:Bank:Axis",
            description="Test mapping",
        )
        db_session.add(mapping)
        db_session.commit()

        response = authenticated_client.get("/api/v1/bank-account-mappings")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "bank_account_mappings" in data
        assert len(data["bank_account_mappings"]) == 1
        assert data["bank_account_mappings"][0]["account_identifier"] == "XX1234"
        assert data["bank_account_mappings"][0]["ledger_account"] == "Assets:Bank:Axis"

    def test_get_bank_account_mappings_with_book_id(
        self, authenticated_client, user, db_session
    ):
        """Test retrieval with specific book_id parameter"""
        ensure_user_has_active_book(user, db_session)

        # Create another book
        book2 = Book(user_id=user.id, name="Business Book")
        db_session.add(book2)
        db_session.commit()

        # Create mappings in different books
        mapping1 = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX1234",
            ledger_account="Assets:Bank:Personal",
        )
        mapping2 = BankAccountMapping(
            user_id=user.id,
            book_id=book2.id,
            account_identifier="XX5678",
            ledger_account="Assets:Bank:Business",
        )
        db_session.add_all([mapping1, mapping2])
        db_session.commit()

        # Test with specific book_id
        response = authenticated_client.get(
            f"/api/v1/bank-account-mappings?book_id={book2.id}"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["bank_account_mappings"]) == 1
        assert data["bank_account_mappings"][0]["account_identifier"] == "XX5678"

    def test_get_bank_account_mappings_no_active_book(
        self, authenticated_client, user, db_session
    ):
        """Test error when user has no active book"""
        user.active_book_id = None
        db_session.commit()

        response = authenticated_client.get("/api/v1/bank-account-mappings")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "No active book selected"

    def test_get_bank_account_mappings_unauthorized(self, client):
        """Test error when no authentication provided"""
        response = client.get("/api/v1/bank-account-mappings")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["error"] == "Authentication required"

    def test_create_bank_account_mapping_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful creation of bank account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping_data = {
            "account_identifier": "XX9999",
            "ledger_account": "Assets:Bank:HDFC",
            "description": "HDFC Bank Account",
        }

        response = authenticated_client.post(
            "/api/v1/bank-account-mappings", json=mapping_data
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["account_identifier"] == "XX9999"
        assert data["ledger_account"] == "Assets:Bank:HDFC"
        assert data["description"] == "HDFC Bank Account"
        assert data["user_id"] == user.id
        assert data["book_id"] == user.active_book_id

    def test_create_bank_account_mapping_with_book_id(
        self, authenticated_client, user, db_session
    ):
        """Test creation with specific book_id"""
        ensure_user_has_active_book(user, db_session)

        book2 = Book(user_id=user.id, name="Business Book")
        db_session.add(book2)
        db_session.commit()

        mapping_data = {
            "book_id": book2.id,
            "account_identifier": "XX8888",
            "ledger_account": "Assets:Bank:Business",
        }

        response = authenticated_client.post(
            "/api/v1/bank-account-mappings", json=mapping_data
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["book_id"] == book2.id

    def test_create_bank_account_mapping_no_data(self, authenticated_client):
        """Test error when no data is provided"""
        response = authenticated_client.post(
            "/api/v1/bank-account-mappings",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Invalid JSON data"

    def test_create_bank_account_mapping_no_book(
        self, authenticated_client, user, db_session
    ):
        """Test error when no book ID and no active book"""
        # Explicitly set user to have no active book
        user.active_book_id = None
        db_session.commit()

        mapping_data = {
            "account_identifier": "XX7777",
            "ledger_account": "Assets:Bank:Test",
        }

        response = authenticated_client.post(
            "/api/v1/bank-account-mappings", json=mapping_data
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "No book ID provided and no active book selected"

    def test_create_bank_account_mapping_book_not_found(
        self, authenticated_client, user, db_session
    ):
        """Test error when book doesn't exist or unauthorized"""
        ensure_user_has_active_book(user, db_session)

        mapping_data = {
            "book_id": 99999,  # Non-existent book
            "account_identifier": "XX6666",
            "ledger_account": "Assets:Bank:Test",
        }

        response = authenticated_client.post(
            "/api/v1/bank-account-mappings", json=mapping_data
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Book not found or unauthorized"

    def test_create_bank_account_mapping_database_error(
        self, authenticated_client, user, db_session
    ):
        """Test database error during creation"""
        from sqlalchemy.exc import SQLAlchemyError

        ensure_user_has_active_book(user, db_session)

        mapping_data = {
            "account_identifier": "XX5555",
            "ledger_account": "Assets:Bank:Test",
        }

        # Mock the commit after the user setup is done
        with patch("app.mappings.db.session.commit") as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")
            response = authenticated_client.post(
                "/api/v1/bank-account-mappings", json=mapping_data
            )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == "Failed to create mapping"

    def test_update_bank_account_mapping_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful update of bank account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX1111",
            ledger_account="Assets:Bank:Old",
            description="Old description",
        )
        db_session.add(mapping)
        db_session.commit()

        update_data = {
            "ledger_account": "Assets:Bank:New",
            "description": "New description",
        }

        response = authenticated_client.put(
            f"/api/v1/bank-account-mappings/{mapping.id}", json=update_data
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["ledger_account"] == "Assets:Bank:New"
        assert data["description"] == "New description"
        assert data["account_identifier"] == "XX1111"  # Unchanged

    def test_update_bank_account_mapping_partial(
        self, authenticated_client, user, db_session
    ):
        """Test partial update of bank account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX2222",
            ledger_account="Assets:Bank:Test",
            description="Original",
        )
        db_session.add(mapping)
        db_session.commit()

        update_data = {"description": "Updated description only"}

        response = authenticated_client.put(
            f"/api/v1/bank-account-mappings/{mapping.id}", json=update_data
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["description"] == "Updated description only"
        assert data["ledger_account"] == "Assets:Bank:Test"  # Unchanged

    def test_update_bank_account_mapping_not_found(self, authenticated_client):
        """Test error when mapping not found or unauthorized"""
        update_data = {"ledger_account": "Assets:Bank:New"}

        response = authenticated_client.put(
            "/api/v1/bank-account-mappings/99999", json=update_data
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Mapping not found or unauthorized"

    def test_update_bank_account_mapping_no_data(
        self, authenticated_client, user, db_session
    ):
        """Test error when no data provided for update"""
        ensure_user_has_active_book(user, db_session)

        mapping = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX3333",
            ledger_account="Assets:Bank:Test",
        )
        db_session.add(mapping)
        db_session.commit()

        response = authenticated_client.put(
            f"/api/v1/bank-account-mappings/{mapping.id}",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Invalid JSON data"

    def test_delete_bank_account_mapping_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful deletion of bank account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX4444",
            ledger_account="Assets:Bank:ToDelete",
        )
        db_session.add(mapping)
        db_session.commit()
        mapping_id = mapping.id

        response = authenticated_client.delete(
            f"/api/v1/bank-account-mappings/{mapping_id}"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Mapping deleted successfully"

        # Verify deletion
        deleted_mapping = db_session.get(BankAccountMapping, mapping_id)
        assert deleted_mapping is None

    def test_delete_bank_account_mapping_not_found(self, authenticated_client):
        """Test error when trying to delete non-existent mapping"""
        response = authenticated_client.delete("/api/v1/bank-account-mappings/99999")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Mapping not found or unauthorized"


class TestExpenseAccountMappings:
    """Test expense account mapping endpoints"""

    def test_get_expense_account_mappings_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful retrieval of expense account mappings"""
        ensure_user_has_active_book(user, db_session)

        mapping = ExpenseAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            merchant_name="Starbucks",
            ledger_account="Expenses:Food:Coffee",
            description="Coffee expenses",
        )
        db_session.add(mapping)
        db_session.commit()

        response = authenticated_client.get("/api/v1/expense-account-mappings")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "expense_account_mappings" in data
        assert len(data["expense_account_mappings"]) == 1
        assert data["expense_account_mappings"][0]["merchant_name"] == "Starbucks"
        assert (
            data["expense_account_mappings"][0]["ledger_account"]
            == "Expenses:Food:Coffee"
        )

    def test_create_expense_account_mapping_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful creation of expense account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping_data = {
            "merchant_name": "Amazon",
            "ledger_account": "Expenses:Shopping:Online",
            "description": "Online shopping",
        }

        response = authenticated_client.post(
            "/api/v1/expense-account-mappings", json=mapping_data
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["merchant_name"] == "Amazon"
        assert data["ledger_account"] == "Expenses:Shopping:Online"
        assert data["description"] == "Online shopping"

    def test_update_expense_account_mapping_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful update of expense account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping = ExpenseAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            merchant_name="McDonald's",
            ledger_account="Expenses:Food:FastFood",
            description="Fast food",
        )
        db_session.add(mapping)
        db_session.commit()

        update_data = {
            "ledger_account": "Expenses:Food:Restaurant",
            "description": "Restaurant expenses",
        }

        response = authenticated_client.put(
            f"/api/v1/expense-account-mappings/{mapping.id}", json=update_data
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["ledger_account"] == "Expenses:Food:Restaurant"
        assert data["description"] == "Restaurant expenses"
        assert data["merchant_name"] == "McDonald's"  # Unchanged

    def test_delete_expense_account_mapping_success(
        self, authenticated_client, user, db_session
    ):
        """Test successful deletion of expense account mapping"""
        ensure_user_has_active_book(user, db_session)

        mapping = ExpenseAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            merchant_name="ToDelete",
            ledger_account="Expenses:Test",
        )
        db_session.add(mapping)
        db_session.commit()
        mapping_id = mapping.id

        response = authenticated_client.delete(
            f"/api/v1/expense-account-mappings/{mapping_id}"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Mapping deleted successfully"

        # Verify deletion
        deleted_mapping = db_session.get(ExpenseAccountMapping, mapping_id)
        assert deleted_mapping is None


class TestMappingsImportExport:
    """Test import/export functionality"""

    def test_import_mappings_success(self, authenticated_client, user, db_session):
        """Test successful import of mappings"""
        ensure_user_has_active_book(user, db_session)

        import_data = {
            "bank-account-map": {
                "XX1234": "Assets:Bank:Axis",
                "XX5678": "Assets:Bank:HDFC",
            },
            "expense-account-map": {
                "Starbucks": ["Expenses:Food:Coffee", "Coffee shop"],
                "Amazon": ["Expenses:Shopping:Online", "Online shopping"],
            },
        }

        response = authenticated_client.post(
            "/api/v1/mappings/import", json=import_data
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Mappings imported successfully"

        # Verify bank account mappings were created
        bank_mappings = BankAccountMapping.query.filter_by(user_id=user.id).all()
        assert len(bank_mappings) == 2

        # Verify expense account mappings were created
        expense_mappings = ExpenseAccountMapping.query.filter_by(user_id=user.id).all()
        assert len(expense_mappings) == 2

    def test_import_mappings_update_existing(
        self, authenticated_client, user, db_session
    ):
        """Test import updates existing mappings"""
        ensure_user_has_active_book(user, db_session)

        # Create existing mapping
        existing_bank = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX1234",
            ledger_account="Assets:Bank:Old",
        )
        existing_expense = ExpenseAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            merchant_name="Starbucks",
            ledger_account="Expenses:Food:Old",
            description="Old description",
        )
        db_session.add_all([existing_bank, existing_expense])
        db_session.commit()

        import_data = {
            "bank-account-map": {"XX1234": "Assets:Bank:Updated"},
            "expense-account-map": {
                "Starbucks": ["Expenses:Food:Updated", "Updated description"]
            },
        }

        response = authenticated_client.post(
            "/api/v1/mappings/import", json=import_data
        )

        assert response.status_code == 200

        # Verify updates
        updated_bank = BankAccountMapping.query.filter_by(
            user_id=user.id, account_identifier="XX1234"
        ).first()
        assert updated_bank.ledger_account == "Assets:Bank:Updated"

        updated_expense = ExpenseAccountMapping.query.filter_by(
            user_id=user.id, merchant_name="Starbucks"
        ).first()
        assert updated_expense.ledger_account == "Expenses:Food:Updated"
        assert updated_expense.description == "Updated description"

    def test_import_mappings_no_data(self, authenticated_client):
        """Test error when no data provided for import"""
        response = authenticated_client.post(
            "/api/v1/mappings/import", headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Invalid JSON data"

    def test_import_mappings_no_book(self, authenticated_client, user, db_session):
        """Test error when no book available for import"""
        user.active_book_id = None
        db_session.commit()

        import_data = {"bank-account-map": {"XX1234": "Assets:Bank:Test"}}

        response = authenticated_client.post(
            "/api/v1/mappings/import", json=import_data
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "No book ID provided and no active book selected"

    def test_export_mappings_success(self, authenticated_client, user, db_session):
        """Test successful export of mappings"""
        ensure_user_has_active_book(user, db_session)

        # Create test mappings
        bank_mapping = BankAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            account_identifier="XX1234",
            ledger_account="Assets:Bank:Axis",
        )
        expense_mapping = ExpenseAccountMapping(
            user_id=user.id,
            book_id=user.active_book_id,
            merchant_name="Starbucks",
            ledger_account="Expenses:Food:Coffee",
            description="Coffee expenses",
        )
        db_session.add_all([bank_mapping, expense_mapping])
        db_session.commit()

        response = authenticated_client.get("/api/v1/mappings/export")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "bank-account-map" in data
        assert "expense-account-map" in data
        assert data["bank-account-map"]["XX1234"] == "Assets:Bank:Axis"
        assert data["expense-account-map"]["Starbucks"] == [
            "Expenses:Food:Coffee",
            "Coffee expenses",
        ]

    def test_export_mappings_empty(self, authenticated_client, user, db_session):
        """Test export with no mappings"""
        ensure_user_has_active_book(user, db_session)

        response = authenticated_client.get("/api/v1/mappings/export")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["bank-account-map"] == {}
        assert data["expense-account-map"] == {}

    def test_export_mappings_no_active_book(
        self, authenticated_client, user, db_session
    ):
        """Test error when no active book for export"""
        user.active_book_id = None
        db_session.commit()

        response = authenticated_client.get("/api/v1/mappings/export")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "No active book selected"

    def test_import_mappings_database_error(
        self, authenticated_client, user, db_session
    ):
        """Test database error during import"""
        from sqlalchemy.exc import SQLAlchemyError

        ensure_user_has_active_book(user, db_session)

        import_data = {"bank-account-map": {"XX1234": "Assets:Bank:Test"}}

        # Mock the commit after the user setup is done
        with patch("app.mappings.db.session.commit") as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")
            response = authenticated_client.post(
                "/api/v1/mappings/import", json=import_data
            )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == "Failed to import mappings"

    @patch("app.mappings.BankAccountMapping.query")
    def test_export_mappings_database_error(
        self, mock_query, authenticated_client, user, db_session
    ):
        """Test database error during export"""
        from sqlalchemy.exc import SQLAlchemyError

        ensure_user_has_active_book(user, db_session)
        mock_query.filter_by.side_effect = SQLAlchemyError("Database error")

        response = authenticated_client.get("/api/v1/mappings/export")

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == "Failed to export mappings"


class TestMappingsEdgeCases:
    """Test edge cases and error scenarios"""

    def test_expense_mapping_import_with_single_value(
        self, authenticated_client, user, db_session
    ):
        """Test import with expense mapping having only ledger account (no description)"""
        ensure_user_has_active_book(user, db_session)

        import_data = {
            "expense-account-map": {
                "TestMerchant": ["Expenses:Test"]  # Only one value in array
            }
        }

        response = authenticated_client.post(
            "/api/v1/mappings/import", json=import_data
        )

        assert response.status_code == 200

        # Verify mapping was created with None description
        mapping = ExpenseAccountMapping.query.filter_by(
            user_id=user.id, merchant_name="TestMerchant"
        ).first()
        assert mapping is not None
        assert mapping.ledger_account == "Expenses:Test"
        assert mapping.description is None

    def test_expense_mapping_import_with_invalid_format(
        self, authenticated_client, user, db_session
    ):
        """Test import with invalid expense mapping format"""
        ensure_user_has_active_book(user, db_session)

        import_data = {
            "expense-account-map": {
                "TestMerchant": "InvalidFormat"  # Should be array, not string
            }
        }

        response = authenticated_client.post(
            "/api/v1/mappings/import", json=import_data
        )

        # Should still succeed but skip invalid entries
        assert response.status_code == 200

        # Verify no mapping was created for invalid format
        mapping = ExpenseAccountMapping.query.filter_by(
            user_id=user.id, merchant_name="TestMerchant"
        ).first()
        assert mapping is None

    def test_cross_user_isolation(self, app, db_session):
        """Test that users can only access their own mappings"""
        with app.app_context():
            # Create two users
            user1 = User(email="user1@test.com")
            user1.set_password("password")
            user2 = User(email="user2@test.com")
            user2.set_password("password")
            db_session.add_all([user1, user2])
            db_session.commit()

            # Create books for both users
            book1 = Book(user_id=user1.id, name="User1 Book")
            book2 = Book(user_id=user2.id, name="User2 Book")
            db_session.add_all([book1, book2])
            db_session.commit()

            # Set active books for both users
            user1.active_book_id = book1.id
            user2.active_book_id = book2.id
            db_session.commit()

            # Create mappings for both users
            mapping1 = BankAccountMapping(
                user_id=user1.id,
                book_id=book1.id,
                account_identifier="XX1111",
                ledger_account="Assets:Bank:User1",
            )
            mapping2 = BankAccountMapping(
                user_id=user2.id,
                book_id=book2.id,
                account_identifier="XX2222",
                ledger_account="Assets:Bank:User2",
            )
            db_session.add_all([mapping1, mapping2])
            db_session.commit()

            # Create authenticated clients for both users
            from flask_jwt_extended import create_access_token

            token1 = create_access_token(identity=str(user1.id))
            token2 = create_access_token(identity=str(user2.id))

            client = app.test_client()

            # User1 should only see their mapping
            response = client.get(
                "/api/v1/bank-account-mappings",
                headers={"Authorization": f"Bearer {token1}"},
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data["bank_account_mappings"]) == 1
            assert data["bank_account_mappings"][0]["account_identifier"] == "XX1111"

            # User2 should only see their mapping
            response = client.get(
                "/api/v1/bank-account-mappings",
                headers={"Authorization": f"Bearer {token2}"},
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data["bank_account_mappings"]) == 1
            assert data["bank_account_mappings"][0]["account_identifier"] == "XX2222"

            # User1 should not be able to update User2's mapping
            response = client.put(
                f"/api/v1/bank-account-mappings/{mapping2.id}",
                headers={
                    "Authorization": f"Bearer {token1}",
                    "Content-Type": "application/json",
                },
                json={"ledger_account": "Assets:Bank:Hacked"},
            )
            assert response.status_code == 404
