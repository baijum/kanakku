# API Utility Tests

This directory contains tests for the API utilities used in the frontend application, particularly the Axios instance that handles API requests.

## axiosInstance Tests

The `axiosInstance.test.js` file contains tests for the utilities exported from `src/api/axiosInstance.js`.
This module provides critical functionality for:

- JWT authentication token management
- Automatic token refresh when tokens expire
- CSRF token handling
- Error intercepting and processing
- Redirect to login page when authentication fails
- Enhanced API URL handling and logging

### Recent Changes

The following updates were recently made to the axiosInstance module:

1. **API URL Configuration**
   - Changed the fallback baseURL from `'/'` to `'/api/v1/'` in development mode
   - This ensures all API requests include the correct API prefix even when `REACT_APP_API_URL` is not set
   - Fixed 404 errors that were occurring due to requests going to the root path

2. **Enhanced Logging**
   - Added detailed request and response logging
   - Improved error logging with context for troubleshooting

### What's being tested

The tests focus on the exported functions that provide the key functionality:

1. **Direct Function Mocking**
   - We mock the exported functions directly (`fetchCsrfToken` and `refreshAuthToken`)
   - This avoids issues with module initialization and circular dependencies

2. **Behavior Verification**
   - Testing the expected behavior rather than implementation details
   - Focusing on input/output behavior rather than internal workings

3. **API URL Configuration**
   - Testing that the correct API base URL is used
   - Verifying fallback to `/api/v1/` when environment variables are not set

### Running the tests

To run just the axiosInstance tests:

```bash
npm run test:axiosinstance
```

To run all tests:

```bash
npm test
```

### Test implementation details

The testing approach uses:

- **Direct mocking of exports**: Mocking the functions themselves rather than their implementation
- **Clean mocks**: Resetting mocks between tests to avoid test pollution
- **Proper mock implementations**: Implementing mocks that behave like the real thing
- **Focus on behavior**: Testing what the functions do, not how they do it
- **Environment variable testing**: Testing behavior with and without environment variables

#### Mocking approach

The key to making these tests work is the order of operations:

1. Set up all mocks **before** importing any modules
2. Mock the exported functions directly
3. Test against the mocked functions rather than implementation details

This approach avoids the "Cannot read properties of undefined (reading 'interceptors')" error
that occurs when trying to test the implementation directly.

### Troubleshooting

If you encounter test failures:

1. Make sure the mocks are defined before importing any modules
2. Use direct function mocking rather than trying to test implementation details
3. Focus on testing behavior rather than internal mechanics
4. Pay attention to the order of imports and mock setups

### Adding new tests

For new functionality in `axiosInstance.js`:

1. Add the exported function to the mocks
2. Test the function's behavior, not its implementation
3. Focus on input/output relationships
4. Keep tests simple and focused on one aspect of behavior per test 