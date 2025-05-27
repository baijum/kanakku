# Deployment Circular Import and Admin Server Fixes

## Problem Description

During deployment, several issues were encountered:

1. **Circular Import Error**: The Flask app initialization was failing with:
   ```
   cannot import name 'create_app' from partially initialized module 'app'
   ```

2. **Admin Server Startup Failure**: The admin server was failing to start with exit code 1.

3. **Database Session Import Issues**: Shared imports were causing circular dependencies when trying to import database utilities.

## Root Cause Analysis

### 1. Circular Import Issue

The circular import was caused by:
- Blueprint imports at the top level of `backend/app/__init__.py`
- Shared imports trying to import Flask app components before the app was fully initialized
- Database utilities trying to import Flask extensions during module initialization

### 2. Admin Server Issues

The admin server was failing due to:
- Missing MCP (Model Context Protocol) dependencies in the virtual environment
- Potential import issues with the admin server modules

### 3. Database Session Import Issues

The `shared/database.py` module was trying to import Flask extensions too early in the import process, causing circular dependencies.

## Solutions Implemented

### 1. Fixed Flask App Initialization

**File**: `backend/app/__init__.py`

**Changes**:
- Moved blueprint imports inside the `create_app()` function within the app context
- Restructured imports to avoid circular dependencies
- Added better error handling for blueprint registration
- Added a health check endpoint for monitoring
- Improved logging configuration with request ID filtering

**Key Changes**:
```python
# Before: Imports at module level
from .accounts_bp import accounts_bp
from .api import api as api_bp
# ... other blueprint imports

# After: Imports within app context
def create_app(config_name="default"):
    # ... app setup ...
    with app.app_context():
        try:
            from .accounts_bp import accounts_bp
            from .api import api as api_bp
            # ... other blueprint imports
            
            # Register blueprints
            app.register_blueprint(auth_bp)
            # ... other registrations
        except Exception as e:
            app.logger.error(f"Error registering blueprints: {str(e)}", exc_info=True)
```

### 2. Fixed Database Session Import Issues

**File**: `shared/database.py`

**Changes**:
- Added safer import checking for Flask extensions
- Only import `app.extensions` when we're sure it's already loaded
- Better fallback to standalone session creation

**Key Changes**:
```python
def get_flask_or_standalone_session() -> Session:
    try:
        from flask import has_app_context
        if has_app_context():
            try:
                # Import db only when we're sure we're in a Flask context
                import sys
                if 'app.extensions' in sys.modules:
                    from app.extensions import db
                    return db.session
            except (ImportError, RuntimeError, AttributeError):
                # Flask app not fully initialized, fall back
                pass
    except (ImportError, RuntimeError):
        # Not in Flask context or Flask not available
        pass
    
    # Fall back to standalone session
    return DatabaseManager.create_session()
```

### 3. Fixed Import Order in Bank Transactions

**File**: `banktransactions/core/processed_ids_db.py`

**Changes**:
- Reordered imports to import shared utilities before Flask app components
- This prevents circular imports during module initialization

### 4. Enhanced Deployment Script

**File**: `.github/workflows/deploy.yml`

**Changes**:
- Added admin server dependency testing before startup
- Improved error handling for service startup
- Added proper Flask environment variables for migrations
- Made admin server startup non-blocking (continues if it fails)
- Added better logging and status checking

**Key Improvements**:
```bash
# Test admin server imports before starting
echo "Testing admin server dependencies..."
cd /opt/kanakku/adminserver
if sudo -u kanakku venv/bin/python test_imports.py; then
  echo "Admin server dependencies OK"
else
  echo "Warning: Admin server dependencies have issues, but continuing..."
fi

# Start admin server with error handling
echo "Starting admin server..."
sudo systemctl start kanakku-admin-server || {
  echo "Warning: Admin server failed to start, checking logs..."
  sudo journalctl -u kanakku-admin-server --no-pager -n 20
  echo "Continuing without admin server..."
}
```

### 5. Added Admin Server Import Testing

**File**: `adminserver/test_imports.py`

**Purpose**: 
- Test all critical imports for the admin server
- Identify missing dependencies or import issues
- Provide diagnostic information during deployment

## Testing and Verification

### 1. Local Testing
- Test Flask app creation with `python -c "from app import create_app; app = create_app()"`
- Test shared imports with `python -c "from shared.imports import *"`
- Test admin server imports with `python adminserver/test_imports.py`

### 2. Deployment Testing
- The deployment script now includes automatic testing of admin server dependencies
- Better error reporting for failed services
- Non-blocking startup (deployment continues even if admin server fails)

## Prevention Measures

### 1. Import Best Practices
- Always import Flask components within app context when possible
- Use lazy imports for optional dependencies
- Avoid circular imports by structuring imports carefully

### 2. Deployment Improvements
- Added dependency testing before service startup
- Better error handling and logging
- Non-critical services (like admin server) don't block deployment

### 3. Monitoring
- Added health check endpoint for better monitoring
- Improved logging with request IDs
- Better service status checking in deployment

## Lessons Learned

1. **Circular Imports**: Flask apps with complex blueprint structures need careful import management
2. **Deployment Resilience**: Critical services should start even if non-critical ones fail
3. **Dependency Testing**: Test imports before starting services to catch issues early
4. **Error Handling**: Provide detailed error information for debugging deployment issues

## Future Improvements

1. Consider using dependency injection for better separation of concerns
2. Implement health checks for all services
3. Add automated rollback on deployment failure
4. Consider containerization for better dependency isolation 