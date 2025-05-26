# GitHub Actions Performance Test Failures

## Problem Description

The GitHub Actions "Backend Performance" workflow was failing with multiple issues:

1. **Missing `imapclient` dependency** causing warnings:
   ```
   Warning: Could not import banktransactions core modules: No module named 'imapclient'
   Warning: Could not import banktransactions automation modules: No module named 'imapclient'
   ```

2. **Import error for `db` from `app.models`** causing the performance test to fail:
   ```
   ImportError: cannot import name 'db' from 'app.models' (/home/runner/work/kanakku/kanakku/backend/app/models/__init__.py)
   ```

3. **Missing logs directory** causing test collection failures:
   ```
   FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/kanakku/kanakku/banktransactions/logs/scheduler.log'
   FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/kanakku/kanakku/banktransactions/logs/worker.log'
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

### Missing Logs Directory
- The automation scripts (`run_scheduler.py` and `run_worker.py`) were configured to write log files to a `logs` directory
- In CI environments, this directory doesn't exist and the logging configuration failed at module import time
- This prevented pytest from collecting tests that imported these modules

## Diagnostic Steps

1. **Analyzed the GitHub Actions log** to identify the specific error messages
2. **Examined the performance workflow** (`.github/workflows/performance.yml`) to understand what it was trying to do
3. **Searched for `imapclient` usage** in the codebase to understand the dependency requirement
4. **Checked the `app.models` module structure** to see why `db` wasn't available for import
5. **Verified the current dependencies** in `pyproject.toml`
6. **Analyzed the logging configuration** in automation scripts to understand the FileNotFoundError

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

### 3. Fixed Logging Configuration for CI Environments

**Files:** `banktransactions/automation/run_scheduler.py` and `banktransactions/automation/run_worker.py`

Modified the logging configuration to:
- Create the logs directory if it doesn't exist
- Gracefully handle cases where file logging fails (e.g., in CI environments)
- Fall back to console-only logging when file logging is not possible

```python
# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
log_file = os.path.join(log_dir, "scheduler.log")  # or "worker.log"

# Create logs directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Set up logging handlers
handlers = [logging.StreamHandler(sys.stdout)]

# Try to add file handler, but don't fail if we can't
try:
    handlers.append(logging.FileHandler(log_file))
except (OSError, PermissionError) as e:
    # If we can't create the log file (e.g., in CI environments), just use console logging only.
    print(f"Warning: Could not create log file {log_file}: {e}. Using console logging only.")

logging.basicConfig(
    level=logging.INFO,  # or getattr(logging, log_level, logging.DEBUG) for worker
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)
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

3. **Tested automation module imports:**
   ```bash
   python -c "from banktransactions.automation.run_scheduler import create_db_session, main; print('✅ run_scheduler import successful')"
   python -c "from banktransactions.automation.run_worker import create_db_session, main; print('✅ run_worker import successful')"
   ```

4. **Tested pytest collection:**
   ```bash
   python -m pytest banktransactions/tests/test_automation/test_run_scheduler.py --collect-only
   python -m pytest banktransactions/tests/test_automation/test_run_worker.py --collect-only
   ```

All tests passed successfully.

## Impact

- **GitHub Actions performance tests** should now run without import errors or collection failures
- **Banktransactions module** can be imported without warnings about missing dependencies
- **Performance monitoring** can properly measure application startup time including database initialization
- **Automation scripts** can run in various environments (development, CI, production) without logging configuration failures

## Prevention

- **Dependency auditing:** Regularly check that all imported packages are included in `pyproject.toml`
- **Import testing:** Add import tests to CI to catch missing dependencies early
- **Module exports:** Ensure commonly used objects like `db` are properly exported from their respective modules
- **Environment-agnostic logging:** Configure logging to handle different environments gracefully
- **Directory creation:** Always create required directories before attempting to write files

## Related Files

- `.github/workflows/performance.yml` - Performance monitoring workflow
- `pyproject.toml` - Project dependencies
- `backend/app/models/__init__.py` - Models module exports
- `backend/app/extensions.py` - Flask extensions including `db`
- `banktransactions/core/imap_client.py` - Uses `imapclient` library
- `banktransactions/automation/run_scheduler.py` - Scheduler script with logging configuration
- `banktransactions/automation/run_worker.py` - Worker script with logging configuration 