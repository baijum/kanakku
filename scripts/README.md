# Kanakku Scripts

This directory contains utility scripts for managing the Kanakku application deployment and configuration.

## Scripts Overview

### `create-htpasswd.sh`

Creates and manages the `.htpasswd` file required for nginx basic authentication on the monitoring dashboard.

#### Purpose

The monitoring dashboard at `https://monitor.{{DOMAIN}}` is protected by HTTP Basic Authentication using nginx's `auth_basic` module. This script automates the creation and management of the password file that stores user credentials.

#### Prerequisites

- **Root access**: Script must be run with `sudo` privileges
- **Linux system**: Compatible with Ubuntu/Debian, CentOS/RHEL, and Fedora
- **Internet connection**: Required for automatic dependency installation

#### Usage

```bash
# Create the htpasswd file
sudo ./scripts/create-htpasswd.sh
```

#### What the Script Does

1. **Privilege Check**: Verifies the script is running with root privileges
2. **Dependency Installation**: Automatically installs required tools:
   - Ubuntu/Debian: `apache2-utils` package
   - CentOS/RHEL: `httpd-tools` package  
   - Fedora: `httpd-tools` package
3. **User Input**: Prompts for username and password (password input is hidden)
4. **File Creation**: Creates `/etc/nginx/.htpasswd` with bcrypt-hashed credentials
5. **Permission Setting**: Sets appropriate file ownership and permissions

#### Security Features

- **Bcrypt Hashing**: Passwords are securely hashed using bcrypt algorithm
- **Proper Permissions**: File is set to `644` with `root:root` ownership
- **Hidden Password Input**: Password entry is not echoed to terminal
- **Input Validation**: Ensures username is not empty

#### File Location

The script creates the htpasswd file at:
```
/etc/nginx/.htpasswd
```

This location matches the `auth_basic_user_file` directive in the nginx configuration.

#### Managing Users

After initial setup, you can manage users using the `htpasswd` command directly:

```bash
# Add a new user
sudo htpasswd /etc/nginx/.htpasswd new_username

# Change existing user's password
sudo htpasswd /etc/nginx/.htpasswd existing_username

# Remove a user
sudo htpasswd -D /etc/nginx/.htpasswd username_to_remove

# List all users (usernames only)
sudo cut -d: -f1 /etc/nginx/.htpasswd
```

#### Troubleshooting

**Permission Denied Error**
```bash
# Ensure you're running with sudo
sudo ./scripts/create-htpasswd.sh
```

**htpasswd Command Not Found**
```bash
# Install manually if auto-installation fails
# Ubuntu/Debian:
sudo apt-get install apache2-utils

# CentOS/RHEL:
sudo yum install httpd-tools

# Fedora:
sudo dnf install httpd-tools
```

**File Already Exists Warning**
- The `-c` flag creates a new file, overwriting existing content
- To add users to existing file, use `htpasswd` without `-c` flag

#### Integration with Nginx

This script works with the nginx configuration block:

```nginx
# Authentication
auth_basic "Kanakku Monitoring";
auth_basic_user_file /etc/nginx/.htpasswd;
```

After creating the htpasswd file, restart nginx to apply changes:

```bash
sudo systemctl restart nginx
```

#### Example Output

```
=== Kanakku Monitoring Authentication Setup ===

Enter username for monitoring dashboard: admin
New password: 
Re-type new password: 
Adding password for user admin

✅ .htpasswd file created successfully!
📁 Location: /etc/nginx/.htpasswd
👤 Username: admin

You can now access the monitoring dashboard at https://monitor.{{DOMAIN}}
Use the username and password you just created.

To add more users later, run:
  htpasswd /etc/nginx/.htpasswd <new_username>

To change a user's password, run:
  htpasswd /etc/nginx/.htpasswd <existing_username>
```

## Best Practices

1. **Use Strong Passwords**: Choose complex passwords for monitoring access
2. **Limit Users**: Only create accounts for users who need monitoring access
3. **Regular Updates**: Periodically update passwords and remove unused accounts
4. **Backup**: Consider backing up the htpasswd file as part of your system backup
5. **Audit Access**: Monitor nginx access logs for the monitoring subdomain

## Related Files

- `nginx-kanakku.conf`: Main nginx configuration that references the htpasswd file
- `/etc/nginx/.htpasswd`: Generated password file (not in repository)
- Monitoring dashboard application (running on port 5001)

## Security Considerations

- The htpasswd file contains hashed passwords, but should still be protected
- Basic authentication transmits credentials in base64 encoding - always use HTTPS
- Consider implementing additional security measures like IP whitelisting for production
- Monitor failed authentication attempts in nginx logs 