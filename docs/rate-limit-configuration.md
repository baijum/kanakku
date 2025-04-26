# Rate Limit Configuration

This document explains how to configure and modify rate limits in the Kanakku application.

## Current Rate Limiting Implementation

The application uses a multi-layered rate limiting approach provided by Flask-Limiter:

1. **Global Rate Limiting**: Applied to all API endpoints
   - 200 requests per day per IP address
   - 50 requests per hour per IP address

2. **Authentication Endpoint Protection**: Stricter limits on sensitive endpoints
   - Login: 5 attempts per minute per IP
   - Password Reset Request: 5 attempts per minute per IP
   - Registration: 5 attempts per minute per IP
   - Password Reset: 5 attempts per minute per IP

3. **Progressive Rate Limiting**: Stricter limits after failed attempts
   - After 3 failed login attempts: 3 per minute rate limit applied

## How to Change Rate Limits

There are three ways to modify rate limits in the application:

### 1. Edit Global Default Limits

Modify the `default_limits` parameter in `backend/app/extensions.py`:

```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # Change these values
    storage_uri=get_limiter_storage_uri(),
    strategy="fixed-window",
)
```

### 2. Modify Authentication Endpoint Limits

Edit the rate limit decorators in `backend/app/extensions.py`:

```python
def auth_rate_limit(f):
    @functools.wraps(f)
    @limiter.limit("5 per minute")  # Change this value
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def failed_login_limit(f):
    @functools.wraps(f)
    @limiter.limit("3 per minute")  # Change this value
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function
```

### 3. Configure via Environment Variables

For production deployments, set these environment variables:

```
RATE_LIMIT_DEFAULT_DAY=200       # Requests per day per IP
RATE_LIMIT_DEFAULT_HOUR=50       # Requests per hour per IP
RATE_LIMIT_AUTH_MINUTE=5         # Auth endpoint requests per minute per IP
RATE_LIMIT_FAILED_AUTH_MINUTE=3  # Failed auth attempts per minute per IP
REDIS_URL=your-redis-server      # For distributed rate limiting storage
```

## Storage Backend for Rate Limiting

By default, rate limiting data is stored in memory. For production deployments with multiple instances, Redis should be used:

1. Set the `REDIS_URL` environment variable to your Redis server address
2. The application will automatically use Redis for rate limit storage when available

## Customizing Rate Limit Format

Rate limits use the following format: `[count] per [period]`

Valid periods include:
- `second`
- `minute`
- `hour`
- `day`
- `month`
- `year`

Example formats:
- `5 per minute`
- `100 per day`
- `1000 per hour`

## Rate Limit Response

When rate limits are exceeded, clients receive a `429 Too Many Requests` response with the message:
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

## Monitoring Rate Limits

Rate limit events are logged to the application logs. Look for messages containing:
- "Rate limit exceeded" for triggered limits
- "Rate limit approaching" for warning events

## Restart Required

After changing rate limit configurations, restart the application for changes to take effect. 