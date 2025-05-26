# Kanakku Monitoring Dashboard Authentication

The Kanakku Monitoring Dashboard now includes secure htpasswd-based authentication to protect access to sensitive system information.

## Features

- **htpasswd Authentication**: Industry-standard Apache htpasswd file format
- **Session Management**: Secure session handling with configurable timeouts
- **Password Security**: Uses bcrypt hashing for strong password protection
- **User Management**: Command-line tools for managing users
- **Security Headers**: Proper security headers and CSRF protection
- **Login/Logout**: Clean login interface with proper session handling

## Quick Setup

### 1. Install Dependencies

```bash
# From the project root directory
pip install -e ".[dev]"
```

This installs all dependencies from the unified `pyproject.toml` file, including the authentication dependencies needed for the dashboard.

### 2. Run Setup Script

```bash
python setup_auth.py
```

This will:
- Check for required dependencies
- Generate a secure configuration file (`.env`)
- Create an htpasswd file with an admin user
- Set proper file permissions

### 3. Start the Dashboard

```bash
python web_dashboard.py
```

### 4. Access the Dashboard

Open your browser to `http://localhost:5001` and log in with your admin credentials.

## Manual Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Security (REQUIRED in production)
DASHBOARD_SECRET_KEY=your-secure-secret-key-here

# Authentication
DASHBOARD_HTPASSWD_FILE=/path/to/dashboard.htpasswd
DASHBOARD_AUTH_REALM="Kanakku Monitoring Dashboard"
DASHBOARD_SESSION_TIMEOUT=3600

# Logging
DASHBOARD_LOG_LEVEL=INFO

# Environment
FLASK_ENV=development  # Use 'production' in production
```

### Creating htpasswd File

#### Using the Management Script

```bash
# Create a new user (will prompt for password)
python manage_users.py create admin

# List all users
python manage_users.py list

# Delete a user
python manage_users.py delete olduser

# Check file permissions
python manage_users.py check
```

#### Using Apache htpasswd Tool

```bash
# Create new htpasswd file with user
htpasswd -c /path/to/dashboard.htpasswd admin

# Add user to existing file
htpasswd /path/to/dashboard.htpasswd newuser

# Use bcrypt (recommended)
htpasswd -B /path/to/dashboard.htpasswd admin
```

#### Manual Creation

```python
from auth import create_htpasswd_file

# Create htpasswd file with initial user
create_htpasswd_file("/path/to/dashboard.htpasswd", "admin", "secure_password")
```

## User Management

### Command Line Tool

The `manage_users.py` script provides comprehensive user management:

```bash
# Create user (interactive password prompt)
python manage_users.py create username

# Create user with password (not recommended for production)
python manage_users.py create username --password mypassword

# List all users
python manage_users.py list

# Delete user
python manage_users.py delete username

# Check file permissions
python manage_users.py check

# Use custom htpasswd file
python manage_users.py --file /custom/path.htpasswd create admin

# Use different environment
python manage_users.py --env production create admin
```

### Programmatic Management

```python
from auth import add_user_to_htpasswd, create_htpasswd_file

# Create new htpasswd file
create_htpasswd_file("/path/to/file.htpasswd", "admin", "password")

# Add user to existing file
add_user_to_htpasswd("/path/to/file.htpasswd", "newuser", "password")
```

## Security Considerations

### File Permissions

The htpasswd file should have restrictive permissions:

```bash
chmod 600 /path/to/dashboard.htpasswd
chown dashboard-user:dashboard-group /path/to/dashboard.htpasswd
```

### Secret Key

- **Development**: Auto-generated secure key
- **Production**: Use a strong, unique secret key
- **Environment**: Store in environment variables, never in code

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Session Security

- Sessions expire after configured timeout (default: 1 hour)
- Secure session cookies in production (HTTPS required)
- HttpOnly cookies prevent XSS attacks
- SameSite protection against CSRF

### HTTPS in Production

Always use HTTPS in production:

```bash
# Environment variables for production
FLASK_ENV=production
DASHBOARD_SECRET_KEY=your-production-secret-key
```

## Configuration Options

### Session Timeout

```bash
# Set session timeout (in seconds)
DASHBOARD_SESSION_TIMEOUT=7200  # 2 hours
```

### Authentication Realm

```bash
# Customize the authentication realm
DASHBOARD_AUTH_REALM="My Custom Dashboard"
```

### htpasswd File Location

```bash
# Development
DASHBOARD_HTPASSWD_FILE=./config/dashboard.htpasswd

# Production
DASHBOARD_HTPASSWD_FILE=/etc/kanakku/dashboard.htpasswd
```

## Troubleshooting

### Common Issues

1. **"htpasswd file not found"**
   - Check the `DASHBOARD_HTPASSWD_FILE` path
   - Ensure the file exists and is readable
   - Run `python manage_users.py check`

2. **"Permission denied"**
   - Check file permissions: `ls -la /path/to/dashboard.htpasswd`
   - Ensure the web server user can read the file
   - Set permissions: `chmod 600 /path/to/dashboard.htpasswd`

3. **"Invalid username or password"**
   - Verify credentials with `python manage_users.py list`
   - Check if the user exists in the htpasswd file
   - Ensure password was set correctly

4. **Session expires immediately**
   - Check system clock synchronization
   - Verify `DASHBOARD_SESSION_TIMEOUT` setting
   - Check Flask secret key configuration

### Debug Mode

Enable debug logging:

```bash
DASHBOARD_LOG_LEVEL=DEBUG
```

### Testing Authentication

```python
from auth import dashboard_auth

# Test credentials
if dashboard_auth.verify_credentials("admin", "password"):
    print("Authentication successful")
else:
    print("Authentication failed")
```

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/kanakku-dashboard.service`:

```ini
[Unit]
Description=Kanakku Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=kanakku
Group=kanakku
WorkingDirectory=/opt/kanakku/adminserver
Environment=FLASK_ENV=production
Environment=DASHBOARD_SECRET_KEY=your-production-secret-key
Environment=DASHBOARD_HTPASSWD_FILE=/etc/kanakku/dashboard.htpasswd
ExecStart=/opt/kanakku/venv/bin/python web_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name dashboard.yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Checklist

- [ ] Strong secret key configured
- [ ] htpasswd file has secure permissions (600)
- [ ] HTTPS enabled in production
- [ ] Session timeout configured appropriately
- [ ] Regular password updates
- [ ] Log monitoring enabled
- [ ] Firewall rules configured
- [ ] Regular security updates

## API Changes

All API endpoints now require authentication:

- `/` - Dashboard (login required)
- `/api/services/status` - Service status (login required)
- `/api/system/metrics` - System metrics (login required)
- `/api/system/uptime` - System uptime (login required)
- `/api/logs/*` - Log access (login required)

Public endpoints:

- `/login` - Login page
- `/logout` - Logout handler
- `/api/health` - Health check (no auth required)

## Migration from Unauthenticated Version

If you're upgrading from an unauthenticated version:

1. **Backup your current setup**
2. **Install new dependencies**: `pip install -e ".[dev]"` (from project root)
3. **Run setup script**: `python setup_auth.py`
4. **Update any automation** that accesses the dashboard
5. **Test the authentication** before deploying to production

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the log files for error messages
3. Verify your configuration with `python manage_users.py check`
4. Test authentication with the management tools 