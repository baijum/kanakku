# JWT Token Expiration Fix

## Issue

Users were experiencing authentication errors in production with the following error message:

```
[2025-05-10 00:59:17] [ERROR] [34cb8d42-7f8a-4c10-a22d-9e88ba8650a8] extensions: Unexpected error during authenticated route execution: 
Signature has expired
jwt.exceptions.ExpiredSignatureError: Signature has expired
```

This was occurring because JWT tokens were expiring after 1 hour (the default setting), and there was no automatic refresh mechanism in place. When tokens expired, users would be logged out and required to log in again, creating a poor user experience.

## Root Cause

1. JWT tokens were configured to expire after only 1 hour
2. No token refresh mechanism was implemented
3. The frontend had no way to detect expired tokens and refresh them automatically

## Solution

The solution involved multiple changes to both backend and frontend:

1. **Extended Token Lifetime**:
   - Increased the JWT token expiration time from 1 hour to 24 hours in `backend/app/config.py`
   - This reduces the frequency of token expiration issues

2. **Added Token Refresh Endpoint**:
   - Created a new endpoint `POST /api/v1/auth/refresh` that allows clients to get a new token
   - This endpoint uses the existing authentication mechanism to validate requests

3. **Improved Error Response**:
   - Enhanced the expired token error response to include a specific error code (`token_expired`)
   - This allows clients to distinguish token expiration from other authentication errors

4. **Frontend Token Refresh**:
   - Updated the Axios interceptor in `frontend/src/api/axiosInstance.js` to detect token expiration
   - Added automatic token refresh logic when an expired token is detected
   - Implemented a request queue system to retry requests after token refresh

5. **Documentation**:
   - Updated project README with information about the token refresh mechanism
   - Added a test endpoint for simulating token expiration

## Testing

The solution can be tested using the new test endpoint:

```
GET /api/v1/auth/test-token-expiration
```

This endpoint simulates a token expiration response, allowing developers to verify that the frontend properly handles token refreshing without waiting for an actual token to expire.

## Benefits

- Users remain logged in for longer periods (24 hours instead of 1 hour)
- Tokens are automatically refreshed when they expire
- Seamless user experience with no interruption to their workflow
- Increased logging to help diagnose any future token-related issues 