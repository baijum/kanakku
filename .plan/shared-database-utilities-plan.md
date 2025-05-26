# Shared Database Utilities Plan

## Overview

This plan addresses the fourth refactoring recommendation: **Create shared database utilities**. The goal is to consolidate the numerous duplicate database session creation patterns scattered throughout the `kanakku` project into a unified, reusable database utility system.

## Current State Analysis

### Identified Duplication Patterns

Based on codebase analysis, the following database session creation patterns are duplicated across **15+ files**:

1. **Standalone Session Creation Pattern**:
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   
   db_url = os.getenv("DATABASE_URL")
   if not db_url:
       raise ValueError("DATABASE_URL environment variable not set")
   
   engine = create_engine(db_url)
   Session = sessionmaker(bind=engine)
   session = Session()
   ```

2. **Flask Context Session Usage**:
   ```python
   from app.extensions import db
   # Uses db.session within Flask app context
   ```

3. **Test Database Setup**:
   ```python
   app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
   with app.app_context():
       db.create_all()
   ```

### Files with Database Session Duplication

**Banktransactions Module**:
- `banktransactions/automation/email_processor.py`
- `banktransactions/automation/run_worker.py`
- `banktransactions/automation/run_scheduler.py`
- `banktransactions/core/email_parser.py`
- `banktransactions/tools/check_configs.py`
- `banktransactions/tools/update_test_password.py`
- `banktransactions/tools/debug_encryption.py`
- `banktransactions/tests/test_integration/test_direct.py`
- `banktransactions/tests/test_integration/test_system.py`

**Backend Module**:
- `backend/app/services/gmail_message_service.py` (uses Flask context)
- `backend/tests/conftest.py` (test setup)
- Various service files (use Flask-SQLAlchemy)

## Problems to Solve

1. **Code Duplication**: ~45 lines of duplicate database setup code across multiple files
2. **Inconsistent Error Handling**: Different files handle database connection errors differently
3. **Configuration Fragmentation**: Database URL validation scattered across files
4. **Testing Complexity**: Different test files use different database setup approaches
5. **Maintenance Burden**: Changes to database configuration require updates in multiple places
6. **Resource Management**: Inconsistent session cleanup and connection pooling

## Proposed Solution

### 1. Create Unified Database Utilities

**New file: `shared/database.py`**

```python
"""
Shared database utilities for Kanakku project.

Provides unified database session management for both Flask-context
and standalone usage across backend and banktransactions modules.
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
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
            'pool_pre_ping': True,  # Verify connections before use
            'pool_recycle': 3600,   # Recycle connections every hour
            'echo': os.getenv('SQL_ECHO', 'false').lower() == 'true',
        }
        
        # Special handling for SQLite (testing)
        if db_url.startswith('sqlite'):
            default_config.update({
                'poolclass': StaticPool,
                'connect_args': {'check_same_thread': False},
            })
        
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
    def session_scope(cls, db_url: Optional[str] = None) -> Generator[Session, None, None]:
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
            connect_args={'check_same_thread': False},
            echo=False
        )
    
    @staticmethod
    @contextmanager
    def test_session_scope(test_db_url: str = "sqlite:///:memory:") -> Generator[Session, None, None]:
        """Create a test session with automatic cleanup."""
        engine = TestDatabaseManager.create_test_engine(test_db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Import all models to ensure tables are created
            from app.models import *
            from app.extensions import db
            
            # Create all tables
            db.metadata.create_all(engine)
            
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            engine.dispose()
```

### 2. Update Shared Imports

**Update `shared/imports.py`** to include database utilities:

```python
# Database utilities
try:
    from .database import (
        DatabaseManager,
        get_database_session,
        database_session,
        get_flask_or_standalone_session,
        TestDatabaseManager,
    )
except ImportError as e:
    print(f"Warning: Could not import database utilities: {e}")
    DatabaseManager = None
    get_database_session = None
    database_session = None
    get_flask_or_standalone_session = None
    TestDatabaseManager = None

# Add to __all__ list
__all__ = [
    # ... existing exports ...
    # Database utilities
    'DatabaseManager',
    'get_database_session', 
    'database_session',
    'get_flask_or_standalone_session',
    'TestDatabaseManager',
]
```

## Implementation Plan

### Phase 1: Create Core Database Utilities (Week 1)

#### Step 1.1: Create Database Utility Module
- [ ] Create `shared/database.py` with `DatabaseManager` class
- [ ] Implement engine caching and session factory management
- [ ] Add connection pooling and error handling
- [ ] Include logging and monitoring hooks

#### Step 1.2: Add Testing Utilities
- [ ] Implement `TestDatabaseManager` for test scenarios
- [ ] Create test database session context managers
- [ ] Add utilities for test data setup and cleanup

#### Step 1.3: Update Shared Imports
- [ ] Add database utilities to `shared/imports.py`
- [ ] Ensure graceful fallbacks for missing dependencies
- [ ] Update `__all__` exports list

#### Step 1.4: Create Unit Tests
- [ ] Test `DatabaseManager` functionality
- [ ] Test session creation and cleanup
- [ ] Test error handling and edge cases
- [ ] Test Flask context integration

### Phase 2: Migrate Banktransactions Module (Week 2)

#### Step 2.1: Update Core Automation Files
- [ ] **`banktransactions/automation/email_processor.py`**:
  ```python
  # OLD
  engine = create_engine(db_url)
  Session = sessionmaker(bind=engine)
  db_session = Session()
  
  # NEW
  from shared.imports import database_session
  with database_session() as db_session:
      # existing logic
  ```

- [ ] **`banktransactions/automation/run_worker.py`**:
  ```python
  # OLD
  def create_db_session():
      db_url = os.getenv("DATABASE_URL")
      if not db_url:
          raise ValueError("DATABASE_URL environment variable not set")
      engine = create_engine(db_url)
      Session = sessionmaker(bind=engine)
      return Session()
  
  # NEW
  from shared.imports import get_database_session
  def create_db_session():
      return get_database_session()
  ```

- [ ] **`banktransactions/automation/run_scheduler.py`**: Similar pattern

#### Step 2.2: Update Core Processing Files
- [ ] **`banktransactions/core/email_parser.py`**: Replace standalone session creation
- [ ] Update any other core files with database access

#### Step 2.3: Update Tools and Utilities
- [ ] **`banktransactions/tools/check_configs.py`**
- [ ] **`banktransactions/tools/update_test_password.py`**
- [ ] **`banktransactions/tools/debug_encryption.py`**

### Phase 3: Migrate Test Files (Week 3)

#### Step 3.1: Update Integration Tests
- [ ] **`banktransactions/tests/test_integration/test_direct.py`**
- [ ] **`banktransactions/tests/test_integration/test_system.py`**
- [ ] Use `TestDatabaseManager` for test database setup

#### Step 3.2: Update Unit Tests
- [ ] **`banktransactions/tests/test_automation/test_run_worker.py`**
- [ ] **`banktransactions/tests/test_automation/test_run_scheduler.py`**
- [ ] Mock `DatabaseManager` instead of `create_engine`

#### Step 3.3: Update Backend Tests
- [ ] **`backend/tests/conftest.py`**: Use shared test utilities
- [ ] Update other test files to use consistent patterns

### Phase 4: Enhance Backend Integration (Week 4)

#### Step 4.1: Update Backend Services
- [ ] **`backend/app/services/gmail_message_service.py`**: Use hybrid session approach
- [ ] Update other services to use `get_flask_or_standalone_session()`

#### Step 4.2: Add Configuration Management
- [ ] Create database configuration validation
- [ ] Add connection health checks
- [ ] Implement connection retry logic

#### Step 4.3: Performance Optimization
- [ ] Add connection pooling configuration
- [ ] Implement query performance monitoring
- [ ] Add database metrics collection

## Migration Strategy

### 1. Backward Compatibility
- Keep existing functions working during transition
- Add deprecation warnings for old patterns
- Provide migration guides for each file type

### 2. Gradual Migration
- Start with least critical files (tools, utilities)
- Move to core processing files
- Finish with critical automation components

### 3. Testing Strategy
- Test each migrated file individually
- Run integration tests after each phase
- Maintain test coverage throughout migration

### 4. Rollback Plan
- Keep old code commented for 1 week
- Tag each phase completion for easy rollback
- Document any issues encountered

## Expected Benefits

### 1. Code Quality Improvements
- **Reduced Duplication**: Eliminate ~45 lines of duplicate code
- **Consistent Error Handling**: Unified database error management
- **Better Resource Management**: Proper connection pooling and cleanup

### 2. Maintenance Benefits
- **Single Point of Configuration**: Database settings in one place
- **Easier Testing**: Consistent test database setup
- **Simplified Debugging**: Centralized logging and monitoring

### 3. Performance Improvements
- **Connection Pooling**: Reuse database connections efficiently
- **Reduced Memory Usage**: Shared engine instances
- **Better Error Recovery**: Automatic connection retry logic

### 4. Developer Experience
- **Simpler API**: Easy-to-use context managers
- **Better Documentation**: Clear patterns for database access
- **Consistent Patterns**: Same approach across all modules

## Risk Assessment

### Low Risk
- **Backward Compatibility**: Old patterns continue working
- **Gradual Migration**: Can be done incrementally
- **Well-Tested Patterns**: Using established SQLAlchemy practices

### Medium Risk
- **Flask Integration**: Need to ensure Flask context works correctly
- **Test Migration**: Test files need careful updating

### Mitigation Strategies
- Extensive testing at each phase
- Keep old code as fallback
- Document all changes thoroughly

## Success Metrics

### Quantitative Metrics
- [ ] Reduce database setup code duplication by 90%
- [ ] Consolidate 15+ session creation patterns into 1 utility
- [ ] Maintain 100% test coverage
- [ ] Zero performance regression

### Qualitative Metrics
- [ ] Improved code maintainability
- [ ] Consistent error handling across modules
- [ ] Simplified onboarding for new developers
- [ ] Better debugging and monitoring capabilities

## Timeline

- **Week 1**: Core utilities and testing framework
- **Week 2**: Banktransactions module migration
- **Week 3**: Test file migration and validation
- **Week 4**: Backend integration and optimization

**Total Estimated Time**: 4 weeks

## Dependencies

- Completion of import strategy improvements (already done)
- Access to test environment for validation
- Coordination with any ongoing development work

## Documentation Updates

- [ ] Update development setup guide
- [ ] Create database utilities usage guide
- [ ] Update testing documentation
- [ ] Add troubleshooting guide for database issues 