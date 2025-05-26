#!/usr/bin/env python3
"""
Unit tests for shared database utilities.
"""

import os
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# Import the database utilities
from .database import (
    DatabaseManager,
    TestDatabaseManager,
    database_session,
    get_database_session,
    get_flask_or_standalone_session,
)


class TestDatabaseManagerClass:
    """Test cases for DatabaseManager class."""

    def setup_method(self):
        """Clear caches before each test."""
        DatabaseManager._engines.clear()
        DatabaseManager._session_factories.clear()

    def teardown_method(self):
        """Clean up after each test."""
        DatabaseManager.close_all_connections()

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"})
    def test_get_database_url_success(self):
        """Test successful database URL retrieval."""
        url = DatabaseManager.get_database_url()
        assert url == "postgresql://test:test@localhost/test"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_database_url_missing(self):
        """Test database URL retrieval when environment variable is missing."""
        with pytest.raises(
            ValueError, match="DATABASE_URL environment variable not set"
        ):
            DatabaseManager.get_database_url()

    @patch.dict(os.environ, {"CUSTOM_DB_URL": "sqlite:///test.db"})
    def test_get_database_url_custom_env_var(self):
        """Test database URL retrieval with custom environment variable."""
        url = DatabaseManager.get_database_url("CUSTOM_DB_URL")
        assert url == "sqlite:///test.db"

    @patch("shared.database.create_engine")
    @patch("shared.database.event")
    def test_create_engine_with_config_postgresql(self, mock_event, mock_create_engine):
        """Test engine creation with PostgreSQL configuration."""
        mock_engine = Mock(spec=Engine)
        mock_engine.pool = Mock()  # Add pool attribute for event listener
        mock_create_engine.return_value = mock_engine

        db_url = "postgresql://test:test@localhost/test"
        engine = DatabaseManager.create_engine_with_config(db_url)

        assert engine == mock_engine
        mock_create_engine.assert_called_once()

        # Check that the call was made with expected configuration
        call_args = mock_create_engine.call_args
        assert call_args[0][0] == db_url
        config = call_args[1]
        assert config["pool_pre_ping"] is True
        assert config["pool_recycle"] == 3600

    @patch("shared.database.create_engine")
    @patch("shared.database.event")
    def test_create_engine_with_config_sqlite(self, mock_event, mock_create_engine):
        """Test engine creation with SQLite configuration."""
        mock_engine = Mock(spec=Engine)
        mock_engine.pool = Mock()  # Add pool attribute for event listener
        mock_create_engine.return_value = mock_engine

        db_url = "sqlite:///test.db"
        engine = DatabaseManager.create_engine_with_config(db_url)

        assert engine == mock_engine
        mock_create_engine.assert_called_once()

        # Check SQLite-specific configuration
        call_args = mock_create_engine.call_args
        config = call_args[1]
        assert "poolclass" in config
        assert "connect_args" in config
        assert config["connect_args"]["check_same_thread"] is False

    @patch("shared.database.DatabaseManager.create_engine_with_config")
    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"})
    def test_get_engine_caching(self, mock_create_engine):
        """Test that engines are cached properly."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        # First call should create engine
        engine1 = DatabaseManager.get_engine()
        assert engine1 == mock_engine
        assert mock_create_engine.call_count == 1

        # Second call should return cached engine
        engine2 = DatabaseManager.get_engine()
        assert engine2 == mock_engine
        assert mock_create_engine.call_count == 1  # Should not be called again

    @patch("shared.database.sessionmaker")
    @patch("shared.database.DatabaseManager.get_engine")
    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"})
    def test_get_session_factory(self, mock_get_engine, mock_sessionmaker):
        """Test session factory creation and caching."""
        mock_engine = Mock(spec=Engine)
        mock_get_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory

        # First call should create session factory
        factory1 = DatabaseManager.get_session_factory()
        assert factory1 == mock_session_factory
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)

        # Second call should return cached factory
        factory2 = DatabaseManager.get_session_factory()
        assert factory2 == mock_session_factory
        assert mock_sessionmaker.call_count == 1  # Should not be called again

    @patch("shared.database.DatabaseManager.get_session_factory")
    def test_create_session(self, mock_get_session_factory):
        """Test session creation."""
        mock_session = Mock(spec=Session)
        mock_factory = Mock()
        mock_factory.return_value = mock_session
        mock_get_session_factory.return_value = mock_factory

        session = DatabaseManager.create_session()
        assert session == mock_session
        mock_factory.assert_called_once()

    @patch("shared.database.DatabaseManager.create_session")
    def test_session_scope_success(self, mock_create_session):
        """Test successful session scope context manager."""
        mock_session = Mock(spec=Session)
        mock_create_session.return_value = mock_session

        with DatabaseManager.session_scope() as session:
            assert session == mock_session
            # Simulate some work

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    @patch("shared.database.DatabaseManager.create_session")
    def test_session_scope_exception(self, mock_create_session):
        """Test session scope context manager with exception."""
        mock_session = Mock(spec=Session)
        mock_create_session.return_value = mock_session

        with pytest.raises(ValueError):
            with DatabaseManager.session_scope() as session:
                assert session == mock_session
                raise ValueError("Test exception")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_close_all_connections(self):
        """Test closing all connections and clearing caches."""
        # Mock some cached engines
        mock_engine1 = Mock(spec=Engine)
        mock_engine2 = Mock(spec=Engine)
        DatabaseManager._engines = {"url1": mock_engine1, "url2": mock_engine2}
        DatabaseManager._session_factories = {"url1": Mock(), "url2": Mock()}

        DatabaseManager.close_all_connections()

        mock_engine1.dispose.assert_called_once()
        mock_engine2.dispose.assert_called_once()
        assert len(DatabaseManager._engines) == 0
        assert len(DatabaseManager._session_factories) == 0


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    @patch("shared.database.DatabaseManager.create_session")
    def test_get_database_session(self, mock_create_session):
        """Test get_database_session convenience function."""
        mock_session = Mock(spec=Session)
        mock_create_session.return_value = mock_session

        session = get_database_session()
        assert session == mock_session
        mock_create_session.assert_called_once_with(None)

    @patch("shared.database.DatabaseManager.session_scope")
    def test_database_session_context_manager(self, mock_session_scope):
        """Test database_session convenience context manager."""
        mock_session = Mock(spec=Session)
        mock_session_scope.return_value.__enter__ = Mock(return_value=mock_session)
        mock_session_scope.return_value.__exit__ = Mock(return_value=None)

        with database_session() as session:
            assert session == mock_session

        mock_session_scope.assert_called_once_with(None)

    @patch("shared.database.DatabaseManager.create_session")
    def test_get_flask_or_standalone_session_flask_context(self, mock_create_session):
        """Test get_flask_or_standalone_session when Flask context is not available."""
        mock_session = Mock(spec=Session)
        mock_create_session.return_value = mock_session

        # Since we can't easily mock Flask context, test the fallback behavior
        session = get_flask_or_standalone_session()
        assert session == mock_session
        mock_create_session.assert_called_once()

    @patch("shared.database.DatabaseManager.create_session")
    def test_get_flask_or_standalone_session_no_flask(self, mock_create_session):
        """Test get_flask_or_standalone_session when not in Flask context."""
        mock_session = Mock(spec=Session)
        mock_create_session.return_value = mock_session

        # This will fail to import Flask, falling back to standalone
        session = get_flask_or_standalone_session()
        assert session == mock_session
        mock_create_session.assert_called_once()


class TestTestDatabaseManagerClass:
    """Test cases for TestDatabaseManager."""

    @patch("shared.database.DatabaseManager.create_engine_with_config")
    def test_create_test_engine(self, mock_create_engine):
        """Test test engine creation."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        engine = TestDatabaseManager.create_test_engine()
        assert engine == mock_engine

        # Check that it was called with test configuration
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        assert call_args[0][0] == "sqlite:///:memory:"
        config = call_args[1]
        assert "poolclass" in config
        assert config["echo"] is False

    @patch("shared.database.TestDatabaseManager.create_test_engine")
    @patch("shared.database.sessionmaker")
    def test_test_session_scope_success(
        self, mock_sessionmaker, mock_create_test_engine
    ):
        """Test successful test session scope."""
        mock_engine = Mock(spec=Engine)
        mock_create_test_engine.return_value = mock_engine

        mock_session = Mock(spec=Session)
        mock_session_class = Mock()
        mock_session_class.return_value = mock_session
        mock_sessionmaker.return_value = mock_session_class

        with TestDatabaseManager.test_session_scope() as session:
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_engine.dispose.assert_called_once()

    @patch("shared.database.TestDatabaseManager.create_test_engine")
    @patch("shared.database.sessionmaker")
    def test_test_session_scope_exception(
        self, mock_sessionmaker, mock_create_test_engine
    ):
        """Test test session scope with exception."""
        mock_engine = Mock(spec=Engine)
        mock_create_test_engine.return_value = mock_engine

        mock_session = Mock(spec=Session)
        mock_session_class = Mock()
        mock_session_class.return_value = mock_session
        mock_sessionmaker.return_value = mock_session_class

        with pytest.raises(ValueError):
            with TestDatabaseManager.test_session_scope() as session:
                assert session == mock_session
                raise ValueError("Test exception")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_engine.dispose.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
