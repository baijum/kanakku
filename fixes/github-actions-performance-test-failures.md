# GitHub Actions Performance Test Failures

## Problem Description

The GitHub Actions "Backend Performance" workflow was failing with two main issues:

1. **Missing `imapclient` dependency** causing warnings:
   ```
   Warning: Could not import banktransactions core modules: No module named 'imapclient'
   Warning: Could not import banktransactions automation modules: No module named 'imapclient'
   ```

2. **Import error for `db` from `app.models`** causing the performance test to fail:
   ```
   ImportError: cannot import name 'db' from 'app.models' (/home/runner/work/kanakku/kanakku/backend/app/models/__init__.py)
   ```

## Root Cause Analysis

### Missing `imapclient` Dependency
- The `banktransactions` module uses `imapclient` for Gmail IMAP operations
- The dependency was not included in `pyproject.toml`
- This caused import failures when the performance test tried to load banktransactions modules

### Missing `db` Export
- The performance test script tried to import `db` from `app.models`
- The `db` object was defined in `backend/app/extensions.py` but not exported from `app.models`
- The `app.models.__init__.py` file didn't include `db` in its exports

## Diagnostic Steps

1. **Analyzed the GitHub Actions log** to identify the specific error messages
2. **Examined the performance workflow** (`.github/workflows/performance.yml`) to understand what it was trying to do
3. **Searched for `imapclient` usage** in the codebase to understand the dependency requirement
4. **Checked the `app.models` module structure** to see why `db` wasn't available for import
5. **Verified the current dependencies** in `pyproject.toml`

## Solution Implemented

### 1. Added Missing `imapclient` Dependency

**File:** `pyproject.toml`

Added `imapclient==3.0.1` to the dependencies list:

```toml
# Email processing
"imapclient==3.0.1",
```

### 2. Exported `db` from `app.models`

**File:** `backend/app/models/__init__.py`

Added the import and export of `db`:

```python
# Import database instance
from ..extensions import db

# Export all models for easy importing
__all__ = [
    "db",  # Added this
    "BaseModel",
    # ... other exports
]
```

## Verification

1. **Tested `db` import:**
   ```bash
   cd backend && python -c "from app.models import db; print('✅ db import successful')"
   ```

2. **Tested `imapclient` import:**
   ```bash
   python -c "import imapclient; print('✅ imapclient import successful')"
   ```

Both tests passed successfully.

## Impact

- **GitHub Actions performance tests** should now run without import errors
- **Banktransactions module** can be imported without warnings about missing dependencies
- **Performance monitoring** can properly measure application startup time including database initialization

## Prevention

- **Dependency auditing:** Regularly check that all imported packages are included in `pyproject.toml`
- **Import testing:** Add import tests to CI to catch missing dependencies early
- **Module exports:** Ensure commonly used objects like `db` are properly exported from their respective modules

## Related Files

- `.github/workflows/performance.yml` - Performance monitoring workflow
- `pyproject.toml` - Project dependencies
- `backend/app/models/__init__.py` - Models module exports
- `backend/app/extensions.py` - Flask extensions including `db`
- `banktransactions/core/imap_client.py` - Uses `imapclient` library 