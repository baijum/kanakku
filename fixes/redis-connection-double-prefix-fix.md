# Redis Connection Error: Double Prefix Issue

## Problem Description

The GitHub Actions CI/CD pipeline was failing during the backend test execution with the following error:

```
ConnectionError: Error -3 connecting to redis:6379. Temporary failure in name resolution.
```

The error occurred when the application tried to connect to Redis during test execution, specifically when the Flask-Limiter extension attempted to establish a Redis connection for rate limiting.

## Root Cause Analysis

### Investigation Steps

1. **Initial Error Analysis**: The error showed the application was trying to connect to `redis:6379` instead of `localhost:6379`, despite the `REDIS_URL` environment variable being correctly set to `redis://localhost:6379/0`.

2. **Environment Variable Verification**: Confirmed that the GitHub Actions workflow was correctly setting:
   ```yaml
   env:
     REDIS_URL: redis://localhost:6379/0
   ```

3. **Code Investigation**: Traced the Redis connection logic through the codebase and found the issue in `backend/app/extensions.py` in the `get_limiter_storage_uri()` function.

### Root Cause Identified

The `get_limiter_storage_uri()` function was incorrectly adding a `redis://` prefix to the `REDIS_URL` environment variable:

```python
# ❌ PROBLEMATIC CODE
def get_limiter_storage_uri():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url and not os.environ.get("TESTING"):
        return f"redis://{redis_url}"  # This adds redis:// to redis://localhost:6379/0
    return "memory://"
```

This resulted in a malformed URL: `redis://redis://localhost:6379/0`, which the Redis client interpreted as trying to connect to a hostname called `redis` on port 6379.

## Solution Implemented

### Code Fix

Modified the `get_limiter_storage_uri()` function in `backend/app/extensions.py` to return the Redis URL directly without adding an additional prefix:

```python
# ✅ FIXED CODE
def get_limiter_storage_uri():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url and not os.environ.get("TESTING"):
        return redis_url  # Use the URL as-is
    return "memory://"
```

### Verification

1. **Local Testing**: Ran tests locally with the same environment variables used in GitHub Actions:
   ```bash
   DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_kanakku \
   REDIS_URL=redis://localhost:6379/0 \
   FLASK_ENV=testing \
   python -m pytest backend/tests/test_accounts.py::test_get_accounts -v
   ```

2. **Multiple Test Scenarios**: Verified the fix works across different test cases that use Redis connections.

## Impact Assessment

### Before Fix
- All backend tests in CI/CD pipeline were failing due to Redis connection errors
- Local development was unaffected because the `TESTING` environment variable check caused the function to return `"memory://"` instead

### After Fix
- All backend tests now pass successfully
- Redis connections work correctly in both CI/CD and production environments
- No impact on existing functionality

## Prevention Measures

### Code Review Points
1. **Environment Variable Handling**: Always verify that environment variables containing URLs are used as-is without additional prefixes
2. **Testing Environment Parity**: Ensure local testing environments match CI/CD environments as closely as possible
3. **Redis Connection Patterns**: Standardize Redis connection patterns across the codebase

### Related Code Patterns
The fix aligns with other Redis connection patterns in the codebase, such as:
- `banktransactions/automation/run_worker.py`: Uses `redis.from_url(args.redis_url)` directly
- `banktransactions/automation/run_scheduler.py`: Uses `redis.from_url(args.redis_url)` directly
- Various debugging scripts: All use Redis URLs without additional prefixes

## Lessons Learned

1. **Environment Variable Assumptions**: Don't assume environment variables need additional formatting - they should be used as provided
2. **Testing Environment Variables**: The `TESTING` environment variable check masked this issue in local development
3. **URL Validation**: Consider adding URL validation to catch malformed URLs early in the development process

## Files Modified

- `backend/app/extensions.py`: Fixed the `get_limiter_storage_uri()` function

## Testing Performed

- ✅ Local backend tests with CI environment variables
- ✅ Multiple account-related test cases
- ✅ Redis connection verification
- ✅ Rate limiting functionality verification 