# Google Gemini API Setup Guide

This guide explains how to configure the Google Gemini API token in Kanakku for automated email processing features.

## Overview

The Google Gemini API token is required for Kanakku's email processing features, which can automatically extract transaction information from bank emails and create accounting entries.

## Prerequisites

1. **Admin Access**: You must have administrator privileges in Kanakku to configure global settings
2. **Google Account**: You need a Google account to access Google AI Studio
3. **API Access**: Ensure you have access to the Gemini API (may require enabling billing)

## Step 1: Obtain Your Gemini API Key

1. **Visit Google AI Studio**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account

2. **Create an API Key**
   - Click "Create API Key"
   - Choose your Google Cloud project (or create a new one)
   - Copy the generated API key (it will start with `AIzaSy`)

3. **Important Security Notes**
   - Store your API key securely
   - Never share it publicly or commit it to version control
   - The key will only be shown once, so save it immediately

## Step 2: Configure in Kanakku

### Method 1: Web Interface (Recommended)

1. **Access Admin Panel**
   - Log in to Kanakku as an administrator
   - Navigate to the Admin Panel from the user menu
   - Click on the "Global Settings" tab

2. **Quick Setup**
   - Look for the "Quick Setup" section
   - Find the "GEMINI API TOKEN" card
   - Click "Configure" button

3. **Enter API Token**
   - In the dialog that opens:
     - Key: `GEMINI_API_TOKEN` (pre-filled)
     - Value: Paste your API key (starts with `AIzaSy`)
     - Description: "Google Gemini API Token for email processing" (pre-filled)
     - Encryption: Leave enabled (recommended)
   - Click "Add Configuration"

### Method 2: REST API

If you prefer to use the REST API directly:

```bash
curl -X POST http://your-kanakku-instance/api/v1/settings/global \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "key": "GEMINI_API_TOKEN",
    "value": "AIzaSyYourActualAPIKeyHere",
    "description": "Google Gemini API Token for email processing",
    "is_encrypted": true
  }'
```

### Method 3: Python (for developers)

```python
from app.utils.config_manager import set_gemini_api_token

# This will validate the token format and store it securely
success, error = set_gemini_api_token("AIzaSyYourActualAPIKeyHere")

if success:
    print("Gemini API token configured successfully!")
else:
    print(f"Error: {error}")
```

## Step 3: Verify Configuration

### Check via Web Interface
1. Go to Admin Panel → Global Settings
2. Look for the "GEMINI_API_TOKEN" entry in the configurations table
3. The value should show "[ENCRYPTED]" indicating it's properly stored

### Check via API
```bash
curl -X GET http://your-kanakku-instance/api/v1/settings/global/GEMINI_API_TOKEN \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Test the Configuration
```python
from app.utils.config_manager import get_gemini_api_token, is_gemini_api_configured

# Check if configured
if is_gemini_api_configured():
    print("✅ Gemini API is configured")
    
    # Get the token (for testing - be careful with this)
    token = get_gemini_api_token()
    print(f"Token starts with: {token[:10]}...")
else:
    print("❌ Gemini API is not configured")
```

## Troubleshooting

### Common Issues

1. **"API token appears to be too short"**
   - Ensure you copied the complete API key
   - Gemini API keys are typically 39 characters long

2. **"Gemini API tokens should start with 'AIzaSy'"**
   - Double-check you copied the correct key from Google AI Studio
   - Make sure there are no extra spaces or characters

3. **"Admin privileges required"**
   - Only administrators can configure global settings
   - Contact your Kanakku administrator to set up the token

4. **"Failed to decrypt value"**
   - This may indicate an encryption key issue
   - Contact your system administrator

### Validation Rules

The system validates Gemini API tokens with these rules:
- Must start with "AIzaSy"
- Must be at least 30 characters long
- Can only contain alphanumeric characters, hyphens, and underscores

## Security Considerations

1. **Encryption**: The API token is automatically encrypted when stored in the database
2. **Access Control**: Only administrators can view or modify global configurations
3. **Audit Trail**: All configuration changes are logged with timestamps
4. **Environment Variables**: For production deployments, consider setting `ENCRYPTION_KEY` environment variable

## Cost Considerations

- Google Gemini API usage is billed based on the number of requests and tokens processed
- Monitor your usage in the Google Cloud Console
- Consider setting up billing alerts to avoid unexpected charges
- The email processing feature will make API calls for each email processed

## Next Steps

Once configured, the Gemini API token will be used by:
1. **Email Processing**: Automatic extraction of transaction data from bank emails
2. **Smart Categorization**: AI-powered expense categorization
3. **Data Validation**: Intelligent validation of extracted financial data

For more information on using these features, see:
- [Email Processing Setup Guide](EMAIL_PROCESSING.md)
- [AI-Powered Features Documentation](AI_FEATURES.md)

## Support

If you encounter issues:
1. Check the application logs for detailed error messages
2. Verify your Google Cloud project has the Gemini API enabled
3. Ensure your API key has the necessary permissions
4. Contact support with specific error messages if problems persist 