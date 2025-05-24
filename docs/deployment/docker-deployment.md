# Kanakku Email Automation - Docker Deployment Guide

This guide covers deploying the Kanakku email automation system using Docker and Docker Compose for easier deployment and management.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Linux server (Ubuntu 20.04+ recommended)
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/kanakku.git
cd kanakku
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env.production

# Edit environment variables
nano .env.production
```

### 3. Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

## Docker Compose Configuration

### Production Docker Compose File

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: kanakku-postgres
    environment:
      POSTGRES_DB: kanakku_prod
      POSTGRES_USER: kanakku_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kanakku_user -d kanakku_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: kanakku-redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Flask Backend
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: kanakku-backend
    environment:
      - DATABASE_URL=postgresql://kanakku_user:${DB_PASSWORD}@postgres:5432/kanakku_prod
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    ports:
      - "127.0.0.1:5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Email Automation Scheduler
  scheduler:
    build:
      context: .
      dockerfile: banktransactions/Dockerfile.scheduler
    container_name: kanakku-scheduler
    environment:
      - DATABASE_URL=postgresql://kanakku_user:${DB_PASSWORD}@postgres:5432/kanakku_prod
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      backend:
        condition: service_healthy
    restart: unless-stopped
    command: ["python", "run_scheduler.py", "--interval", "300"]

  # Email Automation Worker
  worker:
    build:
      context: .
      dockerfile: banktransactions/Dockerfile.worker
    container_name: kanakku-worker
    environment:
      - DATABASE_URL=postgresql://kanakku_user:${DB_PASSWORD}@postgres:5432/kanakku_prod
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      backend:
        condition: service_healthy
    restart: unless-stopped
    command: ["python", "run_worker.py", "--queue-name", "email_processing", "--worker-name", "docker_worker"]

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: kanakku-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
      - ./frontend/build:/usr/share/nginx/html:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: kanakku-network
```

## Dockerfile Configurations

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .
COPY banktransactions/ /app/banktransactions/

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 kanakku && chown -R kanakku:kanakku /app
USER kanakku

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

### Scheduler Dockerfile

Create `banktransactions/Dockerfile.scheduler`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY banktransactions/requirements.txt .
COPY backend/requirements.txt backend_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r backend_requirements.txt

# Copy application code
COPY banktransactions/ .
COPY backend/ /app/backend/

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 kanakku && chown -R kanakku:kanakku /app
USER kanakku

# Start scheduler
CMD ["python", "email_automation/run_scheduler.py", "--interval", "300"]
```

### Worker Dockerfile

Create `banktransactions/Dockerfile.worker`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY banktransactions/requirements.txt .
COPY backend/requirements.txt backend_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r backend_requirements.txt

# Copy application code
COPY banktransactions/ .
COPY backend/ /app/backend/

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 kanakku && chown -R kanakku:kanakku /app
USER kanakku

# Start worker
CMD ["python", "email_automation/run_worker.py", "--queue-name", "email_processing", "--worker-name", "docker_worker"]
```

## Nginx Configuration

### Main Nginx Config

Create `nginx/nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
```

### Site Configuration

Create `nginx/sites-enabled/kanakku.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://backend:5000/health;
        access_log off;
    }
}
```

## Environment Configuration

### Environment File Template

Create `.env.example`:

```bash
# Database Configuration
DB_PASSWORD=your_secure_database_password_here

# Security Keys
SECRET_KEY=your_super_secret_key_here_64_chars_minimum
JWT_SECRET_KEY=your_jwt_secret_key_here_64_chars_minimum
ENCRYPTION_KEY=your_base64_encryption_key_here_44_chars

# Google API
GOOGLE_API_KEY=your_google_api_key_here

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_notification_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false

# Logging
LOG_LEVEL=INFO
```

## Deployment Commands

### Initial Deployment

```bash
# 1. Clone repository
git clone https://github.com/your-org/kanakku.git
cd kanakku

# 2. Configure environment
cp .env.example .env.production
nano .env.production  # Edit with your values

# 3. Create SSL certificate directory
mkdir -p ssl
# Copy your SSL certificates to ssl/fullchain.pem and ssl/privkey.pem

# 4. Build and start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Run database migrations
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade

# 6. Check service status
docker-compose -f docker-compose.prod.yml ps
```

### Management Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f worker
docker-compose -f docker-compose.prod.yml logs -f scheduler

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update deployment
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U kanakku_user kanakku_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U kanakku_user kanakku_prod < backup_file.sql
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check service health
docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:5000/health

# Check queue status
docker-compose -f docker-compose.prod.yml exec worker python -c "
import redis
from rq import Queue
r = redis.from_url('redis://redis:6379/0')
q = Queue('email_processing', connection=r)
print(f'Queue length: {len(q)}')
"
```

### Log Management

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/kanakku-docker

# Add content:
/path/to/kanakku/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /path/to/kanakku/docker-compose.prod.yml restart
    endscript
}
```

### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U kanakku_user kanakku_prod | gzip > $BACKUP_DIR/kanakku_db_$DATE.sql.gz

# Application data backup
tar -czf $BACKUP_DIR/kanakku_app_$DATE.tar.gz logs/ ssl/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "kanakku_*" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Schedule daily backups
echo "0 2 * * * /path/to/kanakku/backup.sh" | crontab -
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker-compose -f docker-compose.prod.yml logs service_name
   ```

2. **Database connection issues**
   ```bash
   docker-compose -f docker-compose.prod.yml exec postgres psql -U kanakku_user -d kanakku_prod -c "SELECT version();"
   ```

3. **Redis connection issues**
   ```bash
   docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
   ```

4. **Worker not processing jobs**
   ```bash
   docker-compose -f docker-compose.prod.yml logs worker
   docker-compose -f docker-compose.prod.yml restart worker
   ```

### Performance Tuning

```bash
# Increase worker replicas
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# Monitor resource usage
docker stats

# Optimize PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U kanakku_user -d kanakku_prod -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
"
```

## Advantages of Docker Deployment

- **Consistency**: Same environment across development, staging, and production
- **Isolation**: Services run in isolated containers
- **Scalability**: Easy to scale individual services
- **Portability**: Runs on any Docker-compatible system
- **Rollback**: Easy to rollback to previous versions
- **Resource Management**: Better resource utilization and limits

## Security Considerations

- Use non-root users in containers
- Keep base images updated
- Use secrets management for sensitive data
- Implement proper network segmentation
- Regular security scanning of images
- Monitor container logs for security events

This Docker deployment provides a production-ready, scalable solution for the Kanakku email automation system. 