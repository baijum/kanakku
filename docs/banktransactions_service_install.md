# Bank Transactions Service Installation Guide

This guide explains how to set up the Bank Transaction Email Parser as a systemd service on Linux.

## Prerequisites

- Linux system with systemd
- Python 3.9 or higher
- Git

## Installation Steps

1. **Create a dedicated user account**:
   ```bash
   sudo useradd -m -s /bin/bash banktransactions
   ```

2. **Create installation directory**:
   ```bash
   sudo mkdir -p /opt/kanakku/banktransactions
   sudo chown -R banktransactions:banktransactions /opt/kanakku/banktransactions
   ```

3. **Clone the repository**:
   ```bash
   sudo -u banktransactions git clone https://github.com/your-repo/kanakku.git /opt/kanakku
   ```

4. **Set up Python virtual environment**:
   ```bash
   sudo -u banktransactions bash -c "cd /opt/kanakku/banktransactions && python3 -m venv venv"
   sudo -u banktransactions bash -c "cd /opt/kanakku/banktransactions && source venv/bin/activate && pip install -r requirements.txt"
   ```

5. **Create and configure the .env file**:
   ```bash
   sudo -u banktransactions bash -c "cat > /opt/kanakku/banktransactions/.env << EOF
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   BANK_EMAILS=alerts@axisbank.com,alerts@icicibank.com
   EOF"
   ```

6. **Copy the service file**:
   ```bash
   sudo cp banktransactions.service /etc/systemd/system/
   ```

7. **Reload systemd**:
   ```bash
   sudo systemctl daemon-reload
   ```

8. **Enable and start the service**:
   ```bash
   sudo systemctl enable banktransactions.service
   sudo systemctl start banktransactions.service
   ```

9. **Verify the service is running**:
   ```bash
   sudo systemctl status banktransactions.service
   ```

## Service Management

- **Check service status**:
  ```bash
  sudo systemctl status banktransactions.service
  ```

- **Restart the service**:
  ```bash
  sudo systemctl restart banktransactions.service
  ```

- **Stop the service**:
  ```bash
  sudo systemctl stop banktransactions.service
  ```

- **View service logs**:
  ```bash
  sudo journalctl -u banktransactions.service
  ```

## Notes

- The service is configured to restart automatically if it fails
- A 5-minute (300s) delay is set between restart attempts
- Security enhancements are enabled (PrivateTmp, ProtectSystem, etc.)
- The service runs with the dedicated banktransactions user for improved security 