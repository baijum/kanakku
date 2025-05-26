"""
Shared database utilities for Kanakku project.

Provides unified database session management for both Flask-context
and standalone usage across backend and banktransactions modules.
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Centralized database connection and session management."""

    _engines = {}  # Cache engines by database URL
    _session_factories = {}  # Cache session factories

    @classmethod
    def get_database_url(cls, env_var: str = "DATABASE_URL") -> str:
        """Get database URL from environment with validation."""
        db_url = os.getenv(env_var)
        if not db_url:
            raise ValueError(f"{env_var} environment variable not set")
        return db_url

    @classmethod
    def create_engine_with_config(cls, db_url: str, **kwargs) -> Engine:
        """Create SQLAlchemy engine with optimized configuration."""
        # Default configuration for production
        default_config = {
            "pool_pre_ping": True,  # Verify connections before use
            "pool_recycle": 3600,  # Recycle connections every hour
            "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
        }

        # Special handling for SQLite (testing)
        if db_url.startswith("sqlite"):
            default_config.update(
                {
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False},
                }
            )

        # Merge with provided kwargs
        config = {**default_config, **kwargs}

        engine = create_engine(db_url, **config)

        # Add connection event listeners for logging
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.debug(f"Database connection established: {db_url[:20]}...")

        return engine

    @classmethod
    def get_engine(cls, db_url: Optional[str] = None) -> Engine:
        """Get or create a cached engine for the given database URL."""
        if db_url is None:
            db_url = cls.get_database_url()

        if db_url not in cls._engines:
            cls._engines[db_url] = cls.create_engine_with_config(db_url)
            logger.info(f"Created new database engine for: {db_url[:20]}...")

        return cls._engines[db_url]

    @classmethod
    def get_session_factory(cls, db_url: Optional[str] = None) -> sessionmaker:
        """Get or create a cached session factory."""
        if db_url is None:
            db_url = cls.get_database_url()

        if db_url not in cls._session_factories:
            engine = cls.get_engine(db_url)
            cls._session_factories[db_url] = sessionmaker(bind=engine)
            logger.debug(f"Created session factory for: {db_url[:20]}...")

        return cls._session_factories[db_url]

    @classmethod
    def create_session(cls, db_url: Optional[str] = None) -> Session:
        """Create a new database session."""
        session_factory = cls.get_session_factory(db_url)
        session = session_factory()
        logger.debug("Created new database session")
        return session

    @classmethod
    @contextmanager
    def session_scope(
        cls, db_url: Optional[str] = None
    ) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = cls.create_session(db_url)
        try:
            yield session
            session.commit()
            logger.debug("Database session committed successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"Database session rolled back due to error: {e}")
            raise
        finally:
            session.close()
            logger.debug("Database session closed")

    @classmethod
    def close_all_connections(cls):
        """Close all cached engines and clear caches."""
        for engine in cls._engines.values():
            engine.dispose()
        cls._engines.clear()
        cls._session_factories.clear()
        logger.info("All database connections closed and caches cleared")


# Convenience functions for common usage patterns
def get_database_session(db_url: Optional[str] = None) -> Session:
    """Get a new database session (caller responsible for closing)."""
    return DatabaseManager.create_session(db_url)


@contextmanager
def database_session(db_url: Optional[str] = None) -> Generator[Session, None, None]:
    """Context manager for database sessions with automatic cleanup."""
    with DatabaseManager.session_scope(db_url) as session:
        yield session


def get_flask_or_standalone_session() -> Session:
    """
    Get database session, preferring Flask context if available.
    Falls back to standalone session creation.
    """
    try:
        # Try to use Flask-SQLAlchemy session if in Flask context
        from flask import has_app_context

        if has_app_context():
            from app.extensions import db

            return db.session
    except (ImportError, RuntimeError):
        # Not in Flask context or Flask not available
        pass

    # Fall back to standalone session
    return DatabaseManager.create_session()


# Testing utilities
class TestDatabaseManager:
    """Database utilities specifically for testing."""

    @staticmethod
    def create_test_engine(test_db_url: str = "sqlite:///:memory:") -> Engine:
        """Create an in-memory SQLite engine for testing."""
        return DatabaseManager.create_engine_with_config(
            test_db_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=False,
        )

    @staticmethod
    @contextmanager
    def test_session_scope(
        test_db_url: str = "sqlite:///:memory:",
    ) -> Generator[Session, None, None]:
        """Create a test session with automatic cleanup."""
        engine = TestDatabaseManager.create_test_engine(test_db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Import models and extensions to ensure tables are created
            from app.extensions import db

            # Create all tables
            db.metadata.create_all(engine)

            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            engine.dispose()
