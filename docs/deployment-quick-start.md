# Kanakku Deployment Quick Start Guide

This is a condensed guide to get your Kanakku application deployed quickly using the automated CI/CD pipeline.

## Prerequisites Checklist

- [ ] Debian 11+ or Ubuntu 20.04+ server with root access
- [ ] Domain name pointed to your server (optional but recommended)
- [ ] GitHub repository with admin access

## Step 1: Server Setup (5 minutes)

Run this single command on your server to set up everything:

```bash
# Download and run the automated setup script
wget https://raw.githubusercontent.com/baijum/kanakku/main/scripts/server-setup.sh
sudo bash server-setup.sh
```

**What this does:**
- Installs PostgreSQL, Redis, Nginx, Python 3.12
- Creates the `kanakku` user and directories
- Sets up firewall and security
- Generates SSH keys and environment variables
- Prepares systemd services for email automation

## Step 2: GitHub Secrets Setup (2 minutes)

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret Name | Value | How to get it |
|-------------|-------|---------------|
| `DEPLOY_HOST` | Your server IP | `hostname -I \| awk '{print $1}'` |
| `DEPLOY_USER` | `root` | Or any user with sudo privileges |
| `DEPLOY_SSH_KEY` | SSH private key | Copy from `/opt/kanakku/.ssh/id_rsa` |

### Get the SSH private key:
```bash
# On your server, copy this output to GitHub secrets
sudo cat /opt/kanakku/.ssh/id_rsa
```

### Add the public key to authorized_keys:
```bash
# On your server
cat /opt/kanakku/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

## Step 3: Configure Your Domain (2 minutes)

### Update environment file:
```bash
sudo nano /opt/kanakku/.env
```

Change this line:
```env
FRONTEND_URL=https://yourdomain.com
```

### Update nginx configuration:
The CI/CD pipeline will deploy the nginx config, but you'll need to update the domain names in `nginx-kanakku.conf` before deployment.

## Step 4: Deploy! (1 minute)

Push to the `main` branch or manually trigger the deployment:

1. Go to your GitHub repository
2. Click "Actions" tab
3. Select "Deploy to Production"
4. Click "Run workflow"

## Step 5: SSL Setup (2 minutes)

After successful deployment:

```bash
# Install SSL certificates
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## Verification

Check that everything is working:

```bash
# Check services
sudo systemctl status kanakku kanakku-worker kanakku-scheduler nginx

# Run health check
sudo /opt/kanakku/health-check.sh

# Check application
curl http://localhost:8000/api/v1/health
```

## Common Issues & Quick Fixes

### Deployment fails with SSH connection error
```bash
# Test SSH connection
ssh -i ~/.ssh/id_rsa root@your-server-ip "echo 'Connection works'"
```

### Services not starting
```bash
# Check logs
sudo journalctl -u kanakku -f
sudo tail -f /opt/kanakku/logs/kanakku.log
```

### Database connection issues
```bash
# Test database
sudo -u kanakku psql -d kanakku -c "SELECT 1;"
```

### Frontend not loading
```bash
# Check nginx
sudo nginx -t
sudo systemctl status nginx
```

## Management Commands

```bash
# Check status
sudo /opt/kanakku/deploy-helper.sh status

# Create backup
sudo /opt/kanakku/deploy-helper.sh backup

# Restart services
sudo /opt/kanakku/deploy-helper.sh restart

# View logs
sudo /opt/kanakku/deploy-helper.sh logs
```

## Next Steps

- Set up monitoring and alerting
- Configure email automation for bank transaction processing
- Configure email settings for notifications
- Review security settings
- Set up regular backups

For detailed documentation, see [docs/deployment.md](deployment.md).

## Support

If you encounter issues:

1. Check the [troubleshooting section](deployment.md#troubleshooting) in the full deployment guide
2. Review GitHub Actions logs for deployment errors
3. Check application logs: `sudo tail -f /opt/kanakku/logs/kanakku.log`
4. Create an issue in the GitHub repository 