# CSRF Protection Implementation

## Problem

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a user's browser into executing unwanted actions on a web application in which the user is authenticated. Without proper CSRF protection, an attacker could potentially create malicious requests that would be executed using the user's authenticated session.

## Solution

We implemented comprehensive CSRF protection across the application using Flask-WTF on the backend and custom handling in our frontend React application. Here's how we addressed the issue:

### Backend Implementation

1. **Added Flask-WTF Package:**
   - Added Flask-WTF as a dependency to handle CSRF token generation and validation

2. **Configuration:**
   - Added CSRF configuration settings to the Flask application config
   - Enabled CSRF protection globally for all POST, PUT, PATCH, and DELETE requests
   - Set a 1-hour time limit for CSRF tokens

3. **CSRF Token Endpoint:**
   - Created a new endpoint at `/api/v1/csrf-token` to allow the frontend to fetch a CSRF token
   - This endpoint returns a valid CSRF token that the frontend can use for requests

4. **Exempt Authentication Routes:**
   - Created a `csrf_exempt` decorator to exempt certain routes from CSRF protection
   - Applied the decorator to login, registration, password reset, and OAuth endpoints
   - These routes need to be exempt because they handle initial authentication

5. **Error Handling:**
   - Added a custom error handler for CSRF validation failures
   - The handler returns a clear error message to help with debugging

### Frontend Implementation

1. **Updated Axios Instance:**
   - Modified the Axios instance to include credentials with requests (`withCredentials: true`)
   - Added CSRF token handling to the request interceptor
   - Implemented automatic token refresh in case of CSRF validation errors

2. **Token Fetching:**
   - Added a `fetchCsrfToken` function to get a fresh CSRF token from the server
   - Initialized token fetching when the application first loads

3. **Request Headers:**
   - Added the CSRF token to the `X-CSRFToken` header for all mutating requests (POST, PUT, PATCH, DELETE)

## Testing

The implementation was tested for:
- Successful retrieval of CSRF tokens from the backend
- Proper inclusion of CSRF tokens in request headers
- Successful submission of forms with CSRF protection
- Appropriate handling of expired or invalid CSRF tokens
- No regressions in existing functionality

## Security Considerations

- CSRF tokens are tied to the user's session
- Tokens expire after one hour to limit the window of vulnerability
- SSL strict mode is enabled to prevent token leakage
- Authentication routes are exempted to prevent login issues

This implementation provides robust protection against CSRF attacks while maintaining a smooth user experience. 