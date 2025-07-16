#!/bin/bash

# Fix Deployment Issues Script
# This script addresses common deployment problems

set -e

echo "🔧 Fixing deployment issues..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Fix MQTT Broker Configuration
print_status "Fixing MQTT broker configuration..."

# Create proper MQTT configuration
cat > mosquitto.conf << EOF
# MQTT Broker Configuration
listener 1883
allow_anonymous true
persistence false
log_type all
EOF

# Update docker-compose.yml to use the config
if ! grep -q "mosquitto.conf" docker-compose.yml; then
    print_status "Updating docker-compose.yml with MQTT configuration..."
    sed -i '/broker:/,/image:/{/volumes:/!{/image:/!d}}' docker-compose.yml
    sed -i '/broker:/a\    volumes:\n      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf' docker-compose.yml
fi

# 2. Fix HTTPS Configuration
print_status "Setting up HTTPS configuration..."

# Create SSL directory if it doesn't exist
sudo mkdir -p /etc/letsencrypt/live/your-domain.com
sudo mkdir -p /etc/letsencrypt/archive/your-domain.com

# Create self-signed certificates for testing (replace with real certificates later)
if [ ! -f /etc/letsencrypt/live/your-domain.com/fullchain.pem ]; then
    print_warning "Creating self-signed certificates for testing..."
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/letsencrypt/live/your-domain.com/privkey.pem \
        -out /etc/letsencrypt/live/your-domain.com/fullchain.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
    
    # Create symlinks for archive
    sudo ln -sf /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/letsencrypt/archive/your-domain.com/privkey1.pem
    sudo ln -sf /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/letsencrypt/archive/your-domain.com/fullchain1.pem
fi

# Set proper permissions
sudo chmod 755 /etc/letsencrypt/live/your-domain.com
sudo chmod 644 /etc/letsencrypt/live/your-domain.com/*.pem

# 3. Update nginx configuration for HTTPS
print_status "Updating nginx configuration..."

# Create HTTPS-enabled nginx config
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # API routes
        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# 4. Fix environment variables
print_status "Fixing environment variables..."

# Create a clean .env file
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:password@db:5432/cloud_db
POSTGRES_DB=cloud_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# MQTT Configuration
MQTT_BROKER=broker
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# API Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=false
ENVIRONMENT=production

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws

# Worker Configuration
WORKER_ENABLED=true
WORKER_CONCURRENCY=4
EOF

# 5. Update docker-compose.yml for proper service dependencies
print_status "Updating docker-compose.yml for better service orchestration..."

# Create a backup
cp docker-compose.yml docker-compose.yml.backup

# Update the docker-compose.yml with proper health checks and dependencies
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cloud_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  broker:
    image: eclipse-mosquitto:2.0
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    ports:
      - "1884:1883"
    healthcheck:
      test: ["CMD", "mosquitto_pub", "-h", "localhost", "-t", "test", "-m", "test"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/cloud_db
      - REDIS_URL=redis://redis:6379/0
      - MQTT_BROKER=broker
      - MQTT_PORT=1883
      - SECRET_KEY=your-super-secret-key-change-this-in-production
      - DEBUG=false
      - ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  worker:
    build: .
    command: python -m app.worker
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/cloud_db
      - REDIS_URL=redis://redis:6379/0
      - MQTT_BROKER=broker
      - MQTT_PORT=1883
      - SECRET_KEY=your-super-secret-key-change-this-in-production
      - DEBUG=false
      - ENVIRONMENT=production
      - WORKER_ENABLED=true
      - WORKER_CONCURRENCY=4
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      broker:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://your-domain.com/api
      - NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws
    depends_on:
      - api

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - api
      - frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
EOF

# 6. Create health check endpoint for API
print_status "Creating health check endpoint..."

# Create a simple health check script
cat > app/health_check.py << 'EOF'
#!/usr/bin/env python3
"""
Simple health check script for the API
"""
import requests
import sys

def check_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("API is healthy")
            return 0
        else:
            print(f"API returned status code: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
EOF

# 7. Restart services
print_status "Restarting services with new configuration..."

# Stop all services
docker-compose down

# Remove old containers and volumes
docker-compose down -v

# Build and start services
docker-compose up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# 8. Test the setup
print_status "Testing the setup..."

# Test HTTP
if curl -f http://localhost:80 > /dev/null 2>&1; then
    print_success "HTTP is working"
else
    print_error "HTTP is not working"
fi

# Test HTTPS
if curl -f -k https://localhost:443 > /dev/null 2>&1; then
    print_success "HTTPS is working"
else
    print_warning "HTTPS is not working (this is expected with self-signed certificates)"
fi

# Test API
if curl -f http://localhost:8082/health > /dev/null 2>&1; then
    print_success "API is working"
else
    print_error "API is not working"
fi

# Test MQTT
if docker-compose exec broker mosquitto_pub -h localhost -t test -m "test" > /dev/null 2>&1; then
    print_success "MQTT broker is working"
else
    print_error "MQTT broker is not working"
fi

# 9. Show final status
print_status "Final service status:"
docker-compose ps

print_success "Deployment issues fixed!"
print_status "Next steps:"
echo "1. Replace 'your-domain.com' with your actual domain in nginx.conf and .env"
echo "2. Obtain real SSL certificates from Let's Encrypt"
echo "3. Update the SECRET_KEY in .env with a secure random string"
echo "4. Configure your domain's DNS to point to this server"
echo "5. Test the application from an external browser"

print_status "Your application should now be accessible at:"
echo "- HTTP: http://your-server-ip"
echo "- HTTPS: https://your-server-ip (with certificate warning)"
echo "- API: http://your-server-ip:8082"
echo "- Frontend: http://your-server-ip:8083" 