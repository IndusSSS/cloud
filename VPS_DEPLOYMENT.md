# SmartSecurity.Solutions Cloud - VPS Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the SmartSecurity.Solutions Cloud platform to a VPS (Virtual Private Server) for production use.

## 📋 Prerequisites

### VPS Requirements
- **OS**: Ubuntu 22.04 LTS (recommended)
- **RAM**: Minimum 2GB, 4GB recommended
- **Storage**: Minimum 20GB SSD
- **CPU**: 2 cores minimum
- **Network**: Public IP address

### Domain (Optional but Recommended)
- Domain name for SSL certificate
- DNS A record pointing to VPS IP

## 🔧 Step 1: VPS Setup

### 1.1 Initial Server Access
```bash
# Connect to your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y curl wget git htop ufw fail2ban
```

### 1.2 Create Non-Root User
```bash
# Create user
adduser smartsecurity
usermod -aG sudo smartsecurity

# Switch to new user
su - smartsecurity
```

### 1.3 Basic Security Setup
```bash
# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable

# Configure fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 🐍 Step 2: Python Environment

### 2.1 Install Python 3.12
```bash
# Install Python dependencies
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Install build dependencies
sudo apt install -y build-essential libssl-dev libffi-dev
```

### 2.2 Install Poetry
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🗄️ Step 3: Database Setup

### 3.1 Install PostgreSQL
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE cloud_db;"
sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cloud_db TO cloud;"
sudo -u postgres psql -c "ALTER USER cloud CREATEDB;"
```

### 3.2 Configure PostgreSQL
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/*/main/postgresql.conf

# Add/modify these lines:
# listen_addresses = 'localhost'
# max_connections = 100
# shared_buffers = 256MB
# effective_cache_size = 1GB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## 🔴 Step 4: Redis Setup

### 4.1 Install Redis
```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Add/modify these lines:
# bind 127.0.0.1
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## 📡 Step 5: MQTT Broker Setup

### 5.1 Install Mosquitto
```bash
# Install Mosquitto
sudo apt install -y mosquitto mosquitto-clients

# Configure Mosquitto
sudo nano /etc/mosquitto/mosquitto.conf

# Add these lines:
# listener 1883
# allow_anonymous true
# persistence true
# persistence_location /var/lib/mosquitto/

# Start and enable Mosquitto
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

## 📦 Step 6: Application Deployment

### 6.1 Clone Repository
```bash
# Clone the repository
git clone https://github.com/your-username/cloud.git
cd cloud

# Install dependencies
poetry install --only main
```

### 6.2 Environment Configuration
```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Production .env Configuration:**
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://cloud:your_secure_password@localhost/cloud_db
DATABASE_ECHO=false

# Security Configuration
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883

# API Configuration
API_PREFIX=/api/v1
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### 6.3 Database Migration
```bash
# Run database migrations
poetry run python -c "
from app.main import app
from app.db.session import engine
from sqlmodel import SQLModel
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

asyncio.run(create_tables())
"
```

### 6.4 Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/smartsecurity-cloud.service
```

**Service Configuration:**
```ini
[Unit]
Description=SmartSecurity.Solutions Cloud
After=network.target postgresql.service redis-server.service mosquitto.service

[Service]
Type=exec
User=smartsecurity
Group=smartsecurity
WorkingDirectory=/home/smartsecurity/cloud
Environment=PATH=/home/smartsecurity/.local/bin
ExecStart=/home/smartsecurity/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable smartsecurity-cloud
sudo systemctl start smartsecurity-cloud

# Check status
sudo systemctl status smartsecurity-cloud
```

## 🌐 Step 7: Nginx Configuration

### 7.1 Install Nginx
```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/smartsecurity-cloud
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (if deployed)
    location / {
        root /var/www/smartsecurity-frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smartsecurity-cloud /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Step 8: SSL Certificate (Let's Encrypt)

### 8.1 Install Certbot
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Set up auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Step 9: Monitoring Setup

### 9.1 Install Monitoring Tools
```bash
# Install monitoring packages
sudo apt install -y htop iotop nethogs

# Install logrotate
sudo apt install -y logrotate
```

### 9.2 Create Log Rotation
```bash
# Create log rotation configuration
sudo nano /etc/logrotate.d/smartsecurity-cloud
```

**Log Rotation Configuration:**
```
/home/smartsecurity/cloud/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 smartsecurity smartsecurity
    postrotate
        systemctl reload smartsecurity-cloud
    endscript
}
```

## 🧪 Step 10: Testing

### 10.1 Health Check
```bash
# Test health endpoint
curl http://your-domain.com/api/v1/health

# Expected response:
# {"status": "ok", "timestamp": "...", "version": "3.0.0"}
```

### 10.2 API Documentation
```bash
# Access API docs
curl http://your-domain.com/api/v1/docs
```

### 10.3 Database Connection
```bash
# Test database connection
sudo -u postgres psql -d cloud_db -c "SELECT version();"
```

## 🔧 Step 11: Maintenance

### 11.1 Backup Script
```bash
# Create backup script
nano /home/smartsecurity/backup.sh
```

**Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/home/smartsecurity/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U cloud cloud_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /home/smartsecurity/cloud

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable and add to crontab
chmod +x /home/smartsecurity/backup.sh
crontab -e
# Add this line for daily backups at 2 AM:
# 0 2 * * * /home/smartsecurity/backup.sh
```

### 11.2 Update Script
```bash
# Create update script
nano /home/smartsecurity/update.sh
```

**Update Script:**
```bash
#!/bin/bash
cd /home/smartsecurity/cloud

# Pull latest changes
git pull origin main

# Update dependencies
poetry install --only main

# Restart service
sudo systemctl restart smartsecurity-cloud

echo "Update completed: $(date)"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status smartsecurity-cloud

# Check logs
sudo journalctl -u smartsecurity-cloud -f
```

#### 2. Database Connection Issues
```bash
# Test database connection
sudo -u postgres psql -d cloud_db -c "SELECT 1;"

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 3. Port Already in Use
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill process if needed
sudo kill -9 <PID>
```

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_sensors_device_id ON sensors(device_id);
CREATE INDEX idx_sensors_timestamp ON sensors(timestamp);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
```

### 2. Application Optimization
```bash
# Increase worker processes
# Edit service file to use multiple workers
ExecStart=/home/smartsecurity/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. System Optimization
```bash
# Optimize PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf
# shared_buffers = 512MB
# effective_cache_size = 2GB
# work_mem = 16MB
```

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Health endpoint responds: `http://your-domain.com/api/v1/health`
- ✅ API documentation accessible: `http://your-domain.com/api/v1/docs`
- ✅ SSL certificate working: `https://your-domain.com`
- ✅ Database migrations completed successfully
- ✅ All services running: `sudo systemctl status smartsecurity-cloud`
- ✅ Logs show no errors: `sudo journalctl -u smartsecurity-cloud`

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u smartsecurity-cloud -f`
2. Verify all services are running: `sudo systemctl status *`
3. Test database connectivity
4. Check firewall settings: `sudo ufw status`

---

**Deployment Status**: ✅ READY  
**Next Steps**: Monitor and scale as needed 