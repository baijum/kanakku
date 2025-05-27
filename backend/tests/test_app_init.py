import logging
from unittest.mock import MagicMock, patch

from flask import g

from app import create_app, setup_logging


def test_create_app():
    """Test app creation with default config"""
    app = create_app()
    assert app is not None
    assert (
        app.config["TESTING"] is not True
    )  # Default config should not be in testing mode

    # Test that all blueprints are registered
    blueprints = [
        "auth",
        "ledger",
        "reports",
        "transactions",
        "accounts",
        "preamble",
        "errors",
        "api",
        "swagger",
    ]

    for bp in blueprints:
        assert bp in app.blueprints


def test_create_app_testing_config():
    """Test app creation with testing config"""
    app = create_app("testing")
    assert app is not None
    assert app.config["TESTING"] is True


def test_setup_logging(monkeypatch):
    """Test the logging setup function"""
    app = create_app("testing")

    # Create properly configured mocks for the handlers
    mock_rotating_handler = MagicMock()
    mock_rotating_handler.level = logging.INFO  # Set the level attribute
    mock_rotating_handler.name = "rotating_handler"

    mock_error_handler = MagicMock()
    mock_error_handler.level = logging.ERROR  # Set the level attribute
    mock_error_handler.name = "error_handler"

    mock_stream_handler = MagicMock()
    mock_stream_handler.level = logging.INFO  # Set the level attribute
    mock_stream_handler.name = "stream_handler"

    # Configure setLevel to update the level property correctly
    def update_level(level):
        mock_rotating_handler.level = level

    mock_rotating_handler.setLevel.side_effect = update_level

    def update_error_level(level):
        mock_error_handler.level = level

    mock_error_handler.setLevel.side_effect = update_error_level

    def update_stream_level(level):
        mock_stream_handler.level = level

    mock_stream_handler.setLevel.side_effect = update_stream_level

    # Mock the handler creation functions
    mock_rotating_file_handler = MagicMock(
        side_effect=[mock_rotating_handler, mock_error_handler]
    )
    mock_stream_handler_constructor = MagicMock(return_value=mock_stream_handler)

    # Mock os.path.exists and os.makedirs
    mock_exists = MagicMock(return_value=False)
    mock_makedirs = MagicMock()

    # Patch both handler constructors and os functions
    with patch("app.RotatingFileHandler", mock_rotating_file_handler):
        with patch("app.logging.StreamHandler", mock_stream_handler_constructor):
            with patch("os.path.exists", mock_exists):
                with patch("os.makedirs", mock_makedirs):
                    # Also override the logger to avoid actual logging
                    mock_logger = MagicMock()
                    monkeypatch.setattr(app, "logger", mock_logger)

                    # Run the setup_logging function
                    setup_logging(app)

                    # Verify the handlers were created correctly
                    assert (
                        mock_rotating_file_handler.call_count == 2
                    )  # Two rotating file handlers
                    assert (
                        mock_stream_handler_constructor.call_count == 1
                    )  # One stream handler

                    # Verify directory existence check and creation
                    assert mock_exists.call_count == 1
                    assert mock_makedirs.call_count == 1

                    # Verify the handlers were set up correctly
                    assert mock_rotating_handler.setFormatter.call_count == 1
                    assert mock_error_handler.setFormatter.call_count == 1
                    assert mock_stream_handler.setFormatter.call_count == 1

                    # Verify handler levels were set
                    assert mock_rotating_handler.setLevel.call_count == 1
                    assert mock_error_handler.setLevel.call_count == 1
                    assert mock_stream_handler.setLevel.call_count == 1


def test_request_id_middleware():
    """Test that request ID middleware assigns a unique ID to each request"""
    app = create_app("testing")

    with app.test_client() as client:
        # Make a request
        client.get("/")

        # Request ID should be set for each request
        with app.test_request_context("/"):
            # Call the before_request handler manually
            for func in app.before_request_funcs[None]:
                func()

            # Verify g.request_id was set
            assert hasattr(g, "request_id")
            assert isinstance(g.request_id, str)
            assert len(g.request_id) > 0


def test_log_response_middleware():
    """Test that response logging middleware logs responses"""
    app = create_app("testing")

    # Mock the logger
    mock_logger = MagicMock()
    app.logger = mock_logger

    # Find the actual log_response function to test directly
    # It should be one of the functions registered to after_request
    log_response_func = None
    for func in app.after_request_funcs[None]:
        # Check if it's a functools.partial object or regular function
        if (hasattr(func, "func") and func.func.__name__ == "log_response") or (
            hasattr(func, "__name__") and func.__name__ == "log_response"
        ):
            log_response_func = func
            break

    # If we found the function, test it directly
    assert (
        log_response_func is not None
    ), f"Could not find log_response function in after_request_funcs. Available functions: {[getattr(f, '__name__', str(f)) for f in app.after_request_funcs[None]]}"

    # Create a test response and call the function directly
    with app.test_request_context("/test"):
        response = app.make_response("Test response")
        response.status_code = 200

        # Call the middleware function directly
        result = log_response_func(response)

        # Verify the logger was called
        mock_logger.debug.assert_called_once()
        assert "Request completed" in mock_logger.debug.call_args[0][0]
        assert "200" in mock_logger.debug.call_args[0][0]

        # Verify the response was returned unchanged
        assert result == response
