from datetime import date

import pytest
from flask import current_app

from app.models import Account, Book, Transaction, db


class TestTransactionSearch:
    """Test suite for PostgreSQL Full-Text Search functionality"""

    def test_search_by_description(self, authenticated_client, user, app):
        """Test searching transactions by description"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            # Create test data
            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create transactions with different descriptions
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 1),
                    description="Coffee at Starbucks",
                    payee="Starbucks",
                    amount=-5.50,
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 2),
                    description="Grocery shopping",
                    payee="Walmart",
                    amount=-50.00,
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 3),
                    description="Salary deposit",
                    payee="Company",
                    amount=2000.00,
                    currency="INR",
                ),
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test search by description - should find transaction with "Coffee" in description
        response = authenticated_client.get("/api/v1/transactions?search=coffee")
        assert response.status_code == 200
        data = response.get_json()
        # With PostgreSQL FTS, should find the coffee transaction
        assert len(data["transactions"]) >= 1
        found_transaction = data["transactions"][0]
        assert "Starbucks" in found_transaction["payee"] or "Coffee" in str(
            found_transaction
        )

        # Test search by payee
        response = authenticated_client.get("/api/v1/transactions?search=starbucks")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        assert data["transactions"][0]["payee"] == "Starbucks"

    def test_search_by_amount(self, authenticated_client, user, app):
        """Test searching transactions by amount"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create transactions with specific amounts
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 1),
                    description="Test transaction",
                    payee="Test",
                    amount=100.00,  # Integer amount
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 2),
                    description="Test transaction",
                    payee="Test",
                    amount=50.75,  # Decimal amount
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 3),
                    description="Test transaction",
                    payee="Test",
                    amount=200.00,
                    currency="INR",
                ),
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test search by integer amount
        response = authenticated_client.get("/api/v1/transactions?search=100")
        assert response.status_code == 200
        data = response.get_json()
        # With PostgreSQL FTS, should find by amount in search vector
        assert len(data["transactions"]) >= 1
        found_amounts = [
            float(tx["postings"][0]["amount"]) for tx in data["transactions"]
        ]
        assert 100.0 in found_amounts

        # Test search by decimal amount
        response = authenticated_client.get("/api/v1/transactions?search=50.75")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        found_amounts = [
            float(tx["postings"][0]["amount"]) for tx in data["transactions"]
        ]
        assert 50.75 in found_amounts

    def test_search_by_status(self, authenticated_client, user, app):
        """Test searching transactions by status using verbose labels"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create transactions with different statuses
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 1),
                    description="Test transaction",
                    payee="Test",
                    amount=100.00,
                    currency="INR",
                    status="*",  # Cleared
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 2),
                    description="Test transaction",
                    payee="Test",
                    amount=50.00,
                    currency="INR",
                    status="!",  # Pending
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 3),
                    description="Test transaction",
                    payee="Test",
                    amount=75.00,
                    currency="INR",
                    status=None,  # Unmarked
                ),
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test search by "cleared" status - PostgreSQL FTS maps "*" to "Cleared"
        response = authenticated_client.get("/api/v1/transactions?search=cleared")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        found_transaction = data["transactions"][0]
        assert found_transaction.get("status") == "*"

        # Test search by "pending" status - PostgreSQL FTS maps "!" to "Pending"
        response = authenticated_client.get("/api/v1/transactions?search=pending")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        found_transaction = data["transactions"][0]
        assert found_transaction.get("status") == "!"

        # Test search by "unmarked" status - PostgreSQL FTS maps NULL to "Unmarked"
        response = authenticated_client.get("/api/v1/transactions?search=unmarked")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        found_transaction = data["transactions"][0]
        assert found_transaction.get("status") in ["", None]

    def test_search_by_currency(self, authenticated_client, user, app):
        """Test searching transactions by currency"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create transactions with different currencies
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 1),
                    description="INR transaction",
                    payee="Test",
                    amount=100.00,
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 2),
                    description="USD transaction",
                    payee="Test",
                    amount=50.00,
                    currency="USD",
                ),
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test search by currency
        response = authenticated_client.get("/api/v1/transactions?search=USD")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        found_currencies = [
            tx["postings"][0]["currency"] for tx in data["transactions"]
        ]
        assert "USD" in found_currencies

    def test_search_by_account_name(self, authenticated_client, user, app):
        """Test searching transactions by account name"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            # Create accounts with different names
            checking_account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking Account",
                currency="INR",
                balance=1000.0,
            )
            savings_account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Savings Account",
                currency="INR",
                balance=2000.0,
            )
            db.session.add_all([checking_account, savings_account])
            db.session.commit()

            # Create transactions in different accounts
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=checking_account.id,
                    date=date(2024, 1, 1),
                    description="Test transaction",
                    payee="Test",
                    amount=100.00,
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=savings_account.id,
                    date=date(2024, 1, 2),
                    description="Test transaction",
                    payee="Test",
                    amount=200.00,
                    currency="INR",
                ),
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test search by account name
        response = authenticated_client.get("/api/v1/transactions?search=checking")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) >= 1
        found_accounts = [tx["postings"][0]["account"] for tx in data["transactions"]]
        assert any("Checking" in account for account in found_accounts)

    def test_complex_search_queries(self, authenticated_client, user, app):
        """Test complex multi-field search queries"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            checking_account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking Account",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(checking_account)
            db.session.commit()

            # Create a specific transaction for complex search
            transaction = Transaction(
                user_id=user.id,
                book_id=book.id,
                account_id=checking_account.id,
                date=date(2024, 1, 1),
                description="Coffee at Starbucks",
                payee="Starbucks",
                amount=50.00,
                currency="INR",
                status="*",  # Cleared
            )
            db.session.add(transaction)
            db.session.commit()

        # Test complex search: "starbucks 50 cleared checking"
        response = authenticated_client.get(
            "/api/v1/transactions?search=starbucks 50 cleared checking"
        )
        assert response.status_code == 200
        data = response.get_json()
        # PostgreSQL FTS should find this transaction matching multiple criteria
        assert len(data["transactions"]) >= 1
        found_transaction = data["transactions"][0]
        assert found_transaction["payee"] == "Starbucks"

    def test_prefix_matching(self, authenticated_client, user, app):
        """Test prefix matching for real-time search"""
        with app.app_context():
            # Skip if not PostgreSQL
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if "postgresql" not in database_url.lower():
                pytest.skip(
                    "PostgreSQL Full-Text Search tests require PostgreSQL database"
                )

            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create transaction with "Starbucks"
            transaction = Transaction(
                user_id=user.id,
                book_id=book.id,
                account_id=account.id,
                date=date(2024, 1, 1),
                description="Coffee purchase",
                payee="Starbucks",
                amount=5.50,
                currency="INR",
            )
            db.session.add(transaction)
            db.session.commit()

        # Test prefix matching - "star" should match "Starbucks"
        response = authenticated_client.get("/api/v1/transactions?search=star")
        assert response.status_code == 200
        data = response.get_json()
        # PostgreSQL FTS with prefix matching should find this
        assert len(data["transactions"]) >= 1
        found_transaction = data["transactions"][0]
        assert "Starbucks" in found_transaction["payee"]

    def test_search_with_pagination(self, authenticated_client, user, app):
        """Test search functionality with pagination - works with both PostgreSQL and SQLite"""
        with app.app_context():
            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create multiple transactions with "test" in description
            transactions = []
            for i in range(15):
                transaction = Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, i + 1),
                    description=f"Test transaction {i}",
                    payee="Test",
                    amount=10.00 + i,
                    currency="INR",
                )
                transactions.append(transaction)
            db.session.add_all(transactions)
            db.session.commit()

        # Test search with limit
        response = authenticated_client.get("/api/v1/transactions?search=test&limit=5")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) <= 5

        # Test search with offset
        response = authenticated_client.get(
            "/api/v1/transactions?search=test&limit=5&offset=5"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) <= 5

    def test_search_with_date_filters(self, authenticated_client, user, app):
        """Test search functionality combined with date filters - works with both PostgreSQL and SQLite"""
        with app.app_context():
            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create transactions on different dates
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, 1),
                    description="Coffee purchase",
                    payee="Starbucks",
                    amount=5.50,
                    currency="INR",
                ),
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 2, 1),
                    description="Coffee purchase",
                    payee="Starbucks",
                    amount=6.00,
                    currency="INR",
                ),
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test search with date range
        response = authenticated_client.get(
            "/api/v1/transactions?search=coffee&startDate=2024-01-01&endDate=2024-01-31"
        )
        assert response.status_code == 200
        data = response.get_json()
        # Should only find January transactions
        if data["transactions"]:
            for tx in data["transactions"]:
                assert tx["date"].startswith("2024-01")

    def test_empty_search_returns_all(self, authenticated_client, user, app):
        """Test that empty search returns all transactions - works with both PostgreSQL and SQLite"""
        with app.app_context():
            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create a few transactions
            transactions = [
                Transaction(
                    user_id=user.id,
                    book_id=book.id,
                    account_id=account.id,
                    date=date(2024, 1, i + 1),
                    description=f"Transaction {i}",
                    payee="Test",
                    amount=10.00 + i,
                    currency="INR",
                )
                for i in range(3)
            ]
            db.session.add_all(transactions)
            db.session.commit()

        # Test empty search
        response = authenticated_client.get("/api/v1/transactions?search=")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) == 3

        # Test no search parameter
        response = authenticated_client.get("/api/v1/transactions")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) == 3

    def test_search_no_results(self, authenticated_client, user, app):
        """Test search that returns no results - works with both PostgreSQL and SQLite"""
        with app.app_context():
            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create a transaction
            transaction = Transaction(
                user_id=user.id,
                book_id=book.id,
                account_id=account.id,
                date=date(2024, 1, 1),
                description="Coffee purchase",
                payee="Starbucks",
                amount=5.50,
                currency="INR",
            )
            db.session.add(transaction)
            db.session.commit()

        # Test search for non-existent term
        response = authenticated_client.get("/api/v1/transactions?search=nonexistent")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) == 0
        assert data["total"] == 0

    def test_search_with_special_characters(self, authenticated_client, user, app):
        """Test search with special characters like colons doesn't cause server errors"""
        with app.app_context():
            book = Book.query.filter_by(user_id=user.id).first()
            if not book:
                book = Book(user_id=user.id, name="Test Book")
                db.session.add(book)
                db.session.commit()

            account = Account(
                user_id=user.id,
                book_id=book.id,
                name="Checking",
                currency="INR",
                balance=1000.0,
            )
            db.session.add(account)
            db.session.commit()

            # Create a transaction
            transaction = Transaction(
                user_id=user.id,
                book_id=book.id,
                account_id=account.id,
                date=date(2024, 1, 1),
                description="Coffee purchase",
                payee="Starbucks",
                amount=5.50,
                currency="INR",
            )
            db.session.add(transaction)
            db.session.commit()

        # Test search terms with special characters that could break PostgreSQL tsquery
        special_search_terms = [
            "Assets:",
            "Assets:Bank:",
            "Expenses:Food:",
            "test:with:colons",
            "search@with#symbols",
            "term&with|operators",
            "Assets::double",
        ]

        for search_term in special_search_terms:
            response = authenticated_client.get(
                f"/api/v1/transactions?search={search_term}"
            )
            # Should return 200 (success) even if no results found, not 500 (server error)
            assert (
                response.status_code == 200
            ), f"Search term '{search_term}' caused server error"
            data = response.get_json()
            assert (
                "transactions" in data
            ), f"Response missing 'transactions' key for search term '{search_term}'"
            assert (
                "total" in data
            ), f"Response missing 'total' key for search term '{search_term}'"
            # Results can be empty (0) or contain matches, both are valid
            assert isinstance(
                data["transactions"], list
            ), f"'transactions' should be a list for search term '{search_term}'"
            assert isinstance(
                data["total"], int
            ), f"'total' should be an integer for search term '{search_term}'"
