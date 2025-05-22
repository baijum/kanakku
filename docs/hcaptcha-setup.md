# hCaptcha Setup Guide

This guide explains how to set up hCaptcha for spam protection in the Kanakku application.

## Overview

hCaptcha is integrated into the user registration form to prevent automated bot registrations. It provides a privacy-focused alternative to other CAPTCHA services.

## Getting hCaptcha Keys

1. **Sign up for hCaptcha**:
   - Go to [hCaptcha Dashboard](https://dashboard.hcaptcha.com/)
   - Create a free account

2. **Create a new site**:
   - Click "New Site" in the dashboard
   - Enter your site details:
     - **Site Name**: Kanakku (or your preferred name)
     - **Hostnames**: Add your domain(s), e.g., `localhost`, `yourdomain.com`
   - Choose the appropriate difficulty level
   - Click "Save"

3. **Get your keys**:
   - **Site Key**: Used in the frontend (public key)
   - **Secret Key**: Used in the backend (private key)

## Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory (or add to existing):

```bash
# hCaptcha Configuration
HCAPTCHA_SECRET_KEY=your-hcaptcha-secret-key-here
```

### Frontend Configuration

Create a `.env` file in the `frontend/` directory (or add to existing):

```bash
# hCaptcha Configuration
REACT_APP_HCAPTCHA_SITE_KEY=your-hcaptcha-site-key-here
```

## Testing

### Development Mode

For development, you can use hCaptcha's test keys:

- **Site Key**: `10000000-ffff-ffff-ffff-000000000001`
- **Secret Key**: `0x0000000000000000000000000000000000000000`

These test keys will always pass verification but should **never** be used in production.

### Test Mode

When running tests, hCaptcha verification is automatically skipped. The backend detects when `TESTING=True` in the Flask configuration and bypasses hCaptcha verification.

## Production Deployment

1. **Update environment variables** with your actual hCaptcha keys
2. **Verify domains** in your hCaptcha dashboard match your production domains
3. **Test registration** to ensure hCaptcha is working correctly

## Troubleshooting

### Common Issues

1. **"Captcha verification is required" error**:
   - Check that the frontend is sending the hCaptcha token
   - Verify the hCaptcha component is rendering correctly

2. **"Captcha verification failed" error**:
   - Check that the backend has the correct `HCAPTCHA_SECRET_KEY`
   - Verify the domain is configured in your hCaptcha dashboard
   - Check network connectivity to hCaptcha's API

3. **hCaptcha not loading**:
   - Check browser console for JavaScript errors
   - Verify the `REACT_APP_HCAPTCHA_SITE_KEY` is set correctly
   - Check if ad blockers are interfering

### Debug Logging

The backend logs hCaptcha verification attempts. Check the logs for:

- `hCaptcha verification successful for IP: {ip}`
- `hCaptcha verification failed for IP: {ip}, errors: {error_codes}`
- `HCAPTCHA_SECRET_KEY not configured`

## Security Considerations

1. **Keep secret keys secure**: Never commit secret keys to version control
2. **Use environment variables**: Store keys in `.env` files that are gitignored
3. **Rotate keys periodically**: Consider rotating your hCaptcha keys regularly
4. **Monitor usage**: Check your hCaptcha dashboard for unusual activity

## Integration Details

### Frontend Integration

The hCaptcha component is integrated into the registration form (`frontend/src/components/Auth/Register.jsx`):

- Renders an hCaptcha widget
- Validates that the user completes the challenge before form submission
- Sends the hCaptcha response token to the backend

### Backend Integration

The backend verifies hCaptcha tokens (`backend/app/auth.py`):

- Receives the hCaptcha token from the frontend
- Makes a server-to-server request to hCaptcha's verification API
- Rejects registration if verification fails
- Logs verification attempts for monitoring

## API Reference

### hCaptcha Verification Endpoint

The backend uses hCaptcha's siteverify API:

```
POST https://api.hcaptcha.com/siteverify
```

**Parameters**:
- `secret`: Your hCaptcha secret key
- `response`: The hCaptcha response token from the frontend
- `remoteip`: The user's IP address (optional)

**Response**:
```json
{
  "success": true|false,
  "challenge_ts": "timestamp",
  "hostname": "your-site.com",
  "error-codes": ["error-code-1", "error-code-2"]
}
``` 