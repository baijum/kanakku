# Domain Configuration for Kanakku Deployment

This document explains how to configure your custom domain for Kanakku deployment using GitHub Actions secrets.

## Overview

The Kanakku application supports dynamic domain configuration through GitHub Actions secrets. This allows you to deploy the application to any domain without hardcoding domain names in the configuration files.

## Supported Subdomains

The application automatically configures the following subdomains based on your main domain:

- **Main Application**: `your-domain.com` (frontend)
- **API Server**: `api.your-domain.com` (backend API)
- **Monitoring Dashboard**: `monitor.your-domain.com` (admin monitoring)

## GitHub Actions Secret Configuration

### Step 1: Add Domain Secret

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:

| Secret Name | Example Value | Description |
|-------------|---------------|-------------|
| `DOMAIN` | `kanakku.muthukadan.net` | Your main domain name |

### Step 2: Additional Required Secrets

Ensure you also have these deployment secrets configured:

| Secret Name | Description |
|-------------|-------------|
| `DEPLOY_HOST` | IP address or hostname of your server |
| `DEPLOY_USER` | SSH username for deployment |
| `DEPLOY_SSH_KEY` | Private SSH key for server access |

## DNS Configuration

Configure your DNS provider to point the following records to your server:

```
A     kanakku.muthukadan.net        → YOUR_SERVER_IP
A     api.kanakku.muthukadan.net    → YOUR_SERVER_IP
A     monitor.kanakku.muthukadan.net → YOUR_SERVER_IP
```

Or use CNAME records if you prefer:

```
CNAME api.kanakku.muthukadan.net    → kanakku.muthukadan.net
CNAME monitor.kanakku.muthukadan.net → kanakku.muthukadan.net
```

## How It Works

### Template System

The deployment process uses a template-based approach:

1. **Template File**: `nginx-kanakku.conf` contains `{{DOMAIN}}` placeholders
2. **Substitution**: During deployment, `{{DOMAIN}}` is replaced with your actual domain
3. **Generation**: A final nginx configuration is created with your domain

### Example Transformation

**Template** (`nginx-kanakku.conf`):
```nginx
server {
    listen 80;
    server_name {{DOMAIN}} www.{{DOMAIN}} localhost;
    # ...
}

server {
    listen 8080;
    server_name api.{{DOMAIN}} localhost;
    # ...
}
```

**Generated** (with `DOMAIN=kanakku.muthukadan.net`):
```nginx
server {
    listen 80;
    server_name kanakku.muthukadan.net www.kanakku.muthukadan.net localhost;
    # ...
}

server {
    listen 8080;
    server_name api.kanakku.muthukadan.net localhost;
    # ...
}
```

## Port Configuration

The application uses the following ports:

| Service | Port | Subdomain | Purpose |
|---------|------|-----------|---------|
| Frontend | 80 | `kanakku.muthukadan.net` | Main web application |
| API | 8080 | `api.kanakku.muthukadan.net` | Backend REST API |
| Monitoring | 5000 | `monitor.kanakku.muthukadan.net` | Admin dashboard |

## SSL/HTTPS Configuration

The current configuration uses HTTP. For production deployments, you should:

1. **Obtain SSL certificates** (Let's Encrypt recommended)
2. **Update nginx configuration** to include SSL settings
3. **Redirect HTTP to HTTPS** for security

### Let's Encrypt Setup (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificates for all subdomains
sudo certbot --nginx -d kanakku.muthukadan.net -d api.kanakku.muthukadan.net -d monitor.kanakku.muthukadan.net

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Testing the Configuration

After deployment, verify each subdomain:

```bash
# Test main application
curl -I http://kanakku.muthukadan.net

# Test API
curl -I http://api.kanakku.muthukadan.net/api/v1/health

# Test monitoring (requires authentication)
curl -I http://monitor.kanakku.muthukadan.net
```

## Troubleshooting

### Common Issues

1. **DNS not propagating**: Wait 24-48 hours for DNS changes to propagate globally
2. **Nginx configuration errors**: Check logs with `sudo nginx -t`
3. **Service not starting**: Check systemd logs with `sudo journalctl -u kanakku`

### Verification Commands

```bash
# Check DNS resolution
nslookup kanakku.muthukadan.net
nslookup api.kanakku.muthukadan.net
nslookup monitor.kanakku.muthukadan.net

# Check nginx configuration
sudo nginx -t

# Check service status
sudo systemctl status kanakku
sudo systemctl status nginx
```

## Fallback Configuration

If no `DOMAIN` secret is provided, the system falls back to `localhost` for local development and testing.

## Security Considerations

1. **Use HTTPS in production** - The current HTTP configuration is for initial deployment only
2. **Configure proper CORS** - The API allows requests from your configured domain
3. **Monitor access logs** - Check nginx logs for unauthorized access attempts
4. **Use strong authentication** - The monitoring dashboard requires HTTP basic auth

## Next Steps

After configuring your domain:

1. Set up SSL certificates for HTTPS
2. Configure monitoring and alerting
3. Set up automated backups
4. Configure log rotation and monitoring 