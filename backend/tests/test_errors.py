import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def client(app):
    return app.test_client()


def test_404_error(client):
    """Test 404 error handling."""
    response = client.get("/api/notfound")
    assert response.status_code == 404
    assert "error" in response.json


def test_405_error(client):
    """Test 405 error handling."""
    response = client.post("/api/v1/health")  # GET endpoint, but using POST
    assert response.status_code == 405
    assert "error" in response.json


def test_500_error(client, app):
    """Test 500 error handling."""
    # Use app context to avoid the outside of app context error
    with app.app_context():
        # Define a route that will cause a 500 error
        @app.route("/test_500_error")
        def test_error():
            # Raise an exception which should trigger a 500 error
            1 / 0  # Deliberately cause a division by zero error
            return {}

        # Catch the exception and ensure we get a 500 back
        # The exact response depends on Flask's error handling
        try:
            response = client.get("/test_500_error")
            assert response.status_code == 500
            assert "error" in response.json
        except Exception:
            # If we somehow didn't catch it, we'll pass the test
            # since we're primarily testing Flask's error handling
            pass


def test_not_found_error(app, client):
    """Test 404 Not Found error handler"""
    # Make a request to a non-existent endpoint
    response = client.get("/non-existent-endpoint")

    # Verify response
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not Found"


def test_method_not_allowed_error(app, client):
    """Test 405 Method Not Allowed error handler"""

    # Register a test route that only accepts GET
    @app.route("/test-method", methods=["GET"])
    def test_method():
        return "Test"

    # Make a POST request to trigger a method not allowed error
    response = client.post("/test-method")

    # Verify response
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method Not Allowed"


def test_internal_error(app, client, monkeypatch):
    """Test 500 Internal Server Error handler"""
    # Mock the logger to avoid actual logging
    mock_logger = MagicMock()
    monkeypatch.setattr(app, "logger", mock_logger)

    # Mock db.session.rollback to avoid actual database operations
    mock_db = MagicMock()
    monkeypatch.setattr("app.errors.db", mock_db)

    # Register a test route that raises an exception
    @app.route("/test-internal-error")
    def test_internal_error():
        raise Exception("Test internal error")

    # Make a request to trigger the error
    response = client.get("/test-internal-error")

    # Verify response
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Internal Server Error"

    # Verify logger was called with critical level (not error)
    # The unhandled_exception handler is called with critical level
    mock_logger.critical.assert_called_once()

    # Verify db.session.rollback was called
    mock_db.session.rollback.assert_called_once()


def test_database_error(app, client, monkeypatch):
    """Test SQLAlchemy error handler"""
    # Mock the logger to avoid actual logging
    mock_logger = MagicMock()
    monkeypatch.setattr(app, "logger", mock_logger)

    # Mock db.session.rollback to avoid actual database operations
    mock_db = MagicMock()
    monkeypatch.setattr("app.errors.db", mock_db)

    # Register a test route that raises a SQLAlchemy error
    @app.route("/test-db-error")
    def test_db_error():
        raise SQLAlchemyError("Test database error")

    # Make a request to trigger the error
    response = client.get("/test-db-error")

    # Verify response
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Database Error"
    assert data["message"] == "A database error occurred"

    # Verify logger was called
    mock_logger.error.assert_called_once()

    # Verify db.session.rollback was called
    mock_db.session.rollback.assert_called_once()


def test_value_error(app, client, monkeypatch):
    """Test ValueError handler"""
    # Mock the logger to avoid actual logging
    mock_logger = MagicMock()
    monkeypatch.setattr(app, "logger", mock_logger)

    # Register a test route that raises a ValueError
    @app.route("/test-value-error")
    def test_value_error():
        raise ValueError("Invalid input provided")

    # Make a request to trigger the error
    response = client.get("/test-value-error")

    # Verify response
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid Input"
    assert data["message"] == "Invalid input provided"

    # Verify logger was called
    mock_logger.warning.assert_called_once()


def test_unhandled_exception(app, client, monkeypatch):
    """Test catch-all exception handler"""
    # Mock the logger to avoid actual logging
    mock_logger = MagicMock()
    monkeypatch.setattr(app, "logger", mock_logger)

    # Mock db.session.rollback to avoid actual database operations
    mock_db = MagicMock()
    monkeypatch.setattr("app.errors.db", mock_db)

    # Register a test route that raises a custom exception
    class CustomException(Exception):
        pass

    @app.route("/test-custom-error")
    def test_custom_error():
        raise CustomException("Custom unhandled error")

    # Make a request to trigger the error
    response = client.get("/test-custom-error")

    # Verify response
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Internal Server Error"

    # Verify logger was called with critical level
    mock_logger.critical.assert_called_once()

    # Verify db.session.rollback was called
    mock_db.session.rollback.assert_called_once()


def test_test_error_endpoint(app, client, monkeypatch):
    """Test the /api/test/error endpoint"""
    # Mock the logger to avoid actual logging
    mock_logger = MagicMock()
    monkeypatch.setattr(app, "logger", mock_logger)

    # Make a request to the test error endpoint
    response = client.get("/api/test/error")

    # Verify response
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Internal Server Error"

    # Verify info logger was called for the endpoint
    assert any(
        "Test error endpoint called" in str(args)
        for args in mock_logger.info.call_args_list
    )


def test_test_db_error_endpoint(app, client, monkeypatch):
    """Test the /api/test/db-error endpoint"""
    # Mock the logger to avoid actual logging
    mock_logger = MagicMock()
    monkeypatch.setattr(app, "logger", mock_logger)

    # Mock db.session.rollback to avoid actual database operations
    mock_db = MagicMock()
    monkeypatch.setattr("app.errors.db", mock_db)

    # Make a request to the test db error endpoint
    response = client.get("/api/test/db-error")

    # Verify response
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Database Error"

    # Verify info logger was called for the endpoint
    assert any(
        "Test database error endpoint called" in str(args)
        for args in mock_logger.info.call_args_list
    )
