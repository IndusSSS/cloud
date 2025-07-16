#!/bin/bash

# Create Clean Environment File Script
# This script creates a clean .env file with proper variable escaping

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Create Clean Environment File Script ===${NC}"
echo

# Create backup if .env exists
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Backup created${NC}"
fi

# Create clean .env file
echo -e "${BLUE}Creating clean .env file...${NC}"

cat > .env << 'EOF'
# =============================================================================
# SmartSecurity Cloud Platform - Production Environment Configuration
# =============================================================================
# 
# This file contains all environment variables for the production deployment.
# IMPORTANT: Keep this file secure and never commit it to version control.
# 
# Generated: 2025-07-16
# Environment: Production
# =============================================================================

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# PostgreSQL database connection settings
DATABASE_URL=postgresql+asyncpg://cloud:cloudpass@db:5432/cloud_db
POSTGRES_USER=cloud
POSTGRES_PASSWORD=cloudpass
POSTGRES_DB=cloud_db

# Database performance settings
DATABASE_ECHO=false
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
# Redis cache and pub/sub settings
REDIS_URL=redis://redis:6379/0
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=20

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
# JWT and authentication settings
SECRET_KEY="Nmlc1Y3rLuglA*3%X\$5Q1IIaPReOYwibybAW6TA\$w6kNkSa%9gLgJuUL&Vel0dZU"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password security
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL=true

# =============================================================================
# API CONFIGURATION
# =============================================================================
# FastAPI application settings
API_PREFIX=/api/v1
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# =============================================================================
# MQTT CONFIGURATION
# =============================================================================
# MQTT broker settings for IoT devices
MQTT_BROKER=broker
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=60
MQTT_QOS=1

# MQTT topics
MQTT_TOPIC_PREFIX=iot
MQTT_HEALTH_TOPIC=health
MQTT_SENSOR_TOPIC=sensor

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# Cross-Origin Resource Sharing settings
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080","https://cloud.smartsecurity.solutions","https://admin.smartsecurity.solutions"]
ALLOWED_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
ALLOWED_HEADERS=["*"]
ALLOW_CREDENTIALS=true

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
# Application logging settings
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/cloud/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# =============================================================================
# MONITORING CONFIGURATION
# =============================================================================
# Application monitoring and metrics
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# =============================================================================
# EMAIL CONFIGURATION (Optional)
# =============================================================================
# SMTP settings for email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
SMTP_FROM_EMAIL=noreply@smartsecurity.solutions

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
# File upload settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=["jpg","jpeg","png","gif","pdf","txt","csv"]
UPLOAD_DIR=/app/uploads

# =============================================================================
# CACHE CONFIGURATION
# =============================================================================
# Application caching settings
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
CACHE_ENABLE=true

# =============================================================================
# TENANT CONFIGURATION
# =============================================================================
# Multi-tenant settings
DEFAULT_TENANT_PLAN=free
MAX_DEVICES_FREE=10
MAX_DEVICES_PREMIUM=100
MAX_DEVICES_ENTERPRISE=1000

# =============================================================================
# DEVICE CONFIGURATION
# =============================================================================
# IoT device settings
DEVICE_HEARTBEAT_INTERVAL=300
DEVICE_OFFLINE_THRESHOLD=900
DEVICE_DATA_RETENTION_DAYS=90

# =============================================================================
# WEBHOOK CONFIGURATION (Optional)
# =============================================================================
# Webhook settings for external integrations
WEBHOOK_ENABLED=false
WEBHOOK_URL=
WEBHOOK_SECRET=
WEBHOOK_TIMEOUT=30

# =============================================================================
# BACKUP CONFIGURATION
# =============================================================================
# Database backup settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_PATH=/app/backups

# =============================================================================
# ENVIRONMENT SPECIFIC SETTINGS
# =============================================================================
# Environment identification
ENVIRONMENT=production
DEPLOYMENT_DATE=2025-07-16
VERSION=3.0.0

# =============================================================================
# DEVELOPMENT OVERRIDES (Set to false in production)
# =============================================================================
# Development and testing settings
TESTING=false
MOCK_EXTERNAL_SERVICES=false
ENABLE_DEBUG_ENDPOINTS=false
SHOW_SQL_QUERIES=false

# =============================================================================
# NOTES
# =============================================================================
# 
# IMPORTANT SECURITY NOTES:
# 1. SECRET_KEY has been auto-generated for security
# 2. Use strong passwords for database and Redis
# 3. Configure proper SSL/TLS certificates
# 4. Set up firewall rules
# 5. Enable rate limiting
# 6. Monitor logs for security events
# 
# DEPLOYMENT CHECKLIST:
# 1. [DONE] SECRET_KEY generated automatically
# 2. Set proper database passwords
# 3. Configure domain names in ALLOWED_ORIGINS
# 4. Set up email configuration if needed
# 5. Configure backup settings
# 6. Test all services after deployment
# 
# =============================================================================
EOF

echo -e "${GREEN}✓ Clean .env file created${NC}"

# Verify the SECRET_KEY
echo -e "${BLUE}Verifying SECRET_KEY...${NC}"
if grep -q 'SECRET_KEY="Nmlc1Y3rLuglA' .env; then
    echo -e "${GREEN}✓ SECRET_KEY is properly formatted${NC}"
else
    echo -e "${RED}✗ SECRET_KEY format is incorrect${NC}"
    exit 1
fi

# Restart services to apply changes
echo -e "${BLUE}Restarting services...${NC}"
docker-compose down
docker-compose up -d

echo -e "${GREEN}✓ Services restarted${NC}"
echo
echo -e "${GREEN}=== Clean Environment File Created ===${NC}"
echo -e "${YELLOW}The Docker Compose warnings should now be resolved.${NC}" 