# Authenticated Client Infinite Recursion Fix

## Problem Description

The GitHub Actions CI pipeline was failing with an infinite recursion error in the `authenticated_client` pytest fixture. The error manifested as:

```
backend.tests.conftest.authenticated_client.backend.tests.conftest.authenticated_client.backend.tests.conftest.authenticated_client...
```

This pattern repeated indefinitely, causing the test suite to hang and eventually fail with a timeout.

## Root Cause Analysis

The issue was in the `authenticated_client` fixture definition in `backend/tests/conftest.py`. The problem was with how the inner `AuthenticatedClient` class was referencing the `client` parameter from the fixture's outer scope.

### Original Problematic Code

```python
@pytest.fixture(scope="function")
def authenticated_client(client, app, user, db_session):
    # ... token creation logic ...
    
    class AuthenticatedClient:
        def get(self, path, **kwargs):
            kwargs.setdefault("headers", {}).update(auth_headers)
            return client.get(path, **kwargs)  # Direct reference to outer scope
        
        def post(self, path, **kwargs):
            # ... similar pattern ...
            return client.post(path, **kwargs)  # Direct reference to outer scope
    
    return AuthenticatedClient()
```

The issue was that the `AuthenticatedClient` class methods were directly referencing the `client` variable from the fixture's outer scope, which could cause pytest's fixture resolution system to get confused and create a circular dependency.

## Solution

The fix involved explicitly passing the `client` as a parameter to the `AuthenticatedClient` class constructor and storing it as an instance variable:

### Fixed Code

```python
@pytest.fixture(scope="function")
def authenticated_client(client, app, user, db_session):
    # ... token creation logic ...
    
    class AuthenticatedClient:
        def __init__(self, test_client):
            self.test_client = test_client
        
        def get(self, path, **kwargs):
            kwargs.setdefault("headers", {}).update(auth_headers)
            return self.test_client.get(path, **kwargs)  # Use instance variable
        
        def post(self, path, **kwargs):
            # ... similar pattern ...
            return self.test_client.post(path, **kwargs)  # Use instance variable
    
    return AuthenticatedClient(client)  # Pass client explicitly
```

## Key Changes

1. **Added `__init__` method**: The `AuthenticatedClient` class now has a proper constructor that accepts the test client as a parameter.

2. **Instance variable storage**: The client is stored as `self.test_client` instead of being referenced from the outer scope.

3. **Explicit parameter passing**: The client is explicitly passed to the constructor when creating the `AuthenticatedClient` instance.

4. **Removed debug prints**: Also cleaned up debug print statements that were cluttering test output.

## Verification

After applying the fix:

- All tests in `test_api.py` pass (6/6)
- Tests in `test_settings.py` that use `authenticated_client` pass
- No infinite recursion errors in local test runs
- GitHub Actions CI pipeline should now complete successfully

## Prevention

To prevent similar issues in the future:

1. **Avoid direct outer scope references**: When creating classes inside pytest fixtures, avoid directly referencing fixture parameters from the outer scope.

2. **Use explicit parameter passing**: Always pass dependencies explicitly to class constructors rather than relying on closure variables.

3. **Test fixture isolation**: Ensure that fixtures are properly isolated and don't create unintended dependencies.

## Files Modified

- `backend/tests/conftest.py`: Fixed the `authenticated_client` fixture implementation

## Related Issues

This fix resolves the GitHub Actions performance test failures that were occurring due to the infinite recursion in the test fixture system. 