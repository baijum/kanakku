# Rate Limiting Implementation

## Problem
The application was vulnerable to brute force attacks on authentication endpoints. Attackers could make unlimited login attempts, password reset requests, and new user registrations, potentially compromising user accounts.

## Solution
We implemented a multi-layered rate limiting approach:

1. **Global Rate Limiting**: Used Flask-Limiter to apply basic rate limits across all API endpoints:
   - 200 requests per day per IP address
   - 50 requests per hour per IP address

2. **Sensitive Endpoint Protection**: Applied stricter limits to authentication endpoints:
   - Login: 5 attempts per minute per IP
   - Password Reset Request: 5 attempts per minute per IP
   - Registration: 5 attempts per minute per IP
   - Password Reset: 5 attempts per minute per IP

3. **Progressive Rate Limiting**: Implemented custom tracking of failed authentication attempts:
   - After 3 failed login attempts for the same email/IP combination, stricter rate limits are applied (3 per minute)
   - After 3 password reset requests for the same email in an hour, further requests are blocked
   - Failed password reset token validations are tracked and limited to prevent token brute forcing

4. **Memory Management**: Added cleanup routines to prevent memory leaks:
   - Failed attempts and password reset records are cleared after a set time period
   - Large tracking dictionaries are periodically pruned

5. **Production Configuration**: 
   - Redis storage backend for distributed deployments
   - Configurable limits via environment variables
   - Comprehensive logging of rate limit events and suspicious activity

## Implementation Details
- Added Flask-Limiter to handle basic rate limiting
- Created custom authentication decorators for sensitive endpoints
- Implemented in-memory tracking of failed attempts with time-based expiry
- Added Redis support for distributed environments
- Enhanced logging for security monitoring

## Results
This implementation provides protection against:
- Username enumeration attacks
- Password guessing attacks
- Account takeover via password reset
- Distributed login attempts
- DOS attacks against authentication endpoints

The rate limiting is transparent to legitimate users but significantly increases the difficulty and time required for brute force attacks. 