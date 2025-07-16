#!/bin/bash

# SmartSecurity Cloud - Complete HTTPS Setup
# This script sets up HTTPS with SSL certificates and HTTP to HTTPS redirect

set -e

echo "🔒 SmartSecurity Cloud - Complete HTTPS Setup"
echo "============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Get domain names
DOMAIN="cloud.smartsecurity.solutions"
ADMIN_DOMAIN="admin.smartsecurity.solutions"

print_status "Setting up HTTPS for domains:"
print_status "  - Customer Portal: $DOMAIN"
print_status "  - Admin Console: $ADMIN_DOMAIN"

# 1. Create SSL certificates directory
print_status "Creating SSL certificates directory..."
sudo mkdir -p /etc/ssl/smartsecurity
sudo chown $USER:$USER /etc/ssl/smartsecurity

# 2. Generate self-signed certificates (for development/testing)
print_status "Generating SSL certificates..."

# Generate private key
openssl genrsa -out /etc/ssl/smartsecurity/private.key 2048

# Generate certificate for customer portal
openssl req -new -x509 -key /etc/ssl/smartsecurity/private.key \
    -out /etc/ssl/smartsecurity/customer.crt \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=$DOMAIN"

# Generate certificate for admin console
openssl req -new -x509 -key /etc/ssl/smartsecurity/private.key \
    -out /etc/ssl/smartsecurity/admin.crt \
    -days 365 \
    -subj="/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=$ADMIN_DOMAIN"

# Set proper permissions
sudo chmod 600 /etc/ssl/smartsecurity/private.key
sudo chmod 644 /etc/ssl/smartsecurity/*.crt

print_success "SSL certificates generated"

# 3. Create HTTPS nginx configuration
print_status "Creating HTTPS nginx configuration..."

cat > nginx/conf.d/cloud-https.conf << 'EOF'
# HTTPS Configuration for SmartSecurity Cloud
# Customer Portal
server {
    listen 80;
    server_name cloud.smartsecurity.solutions;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cloud.smartsecurity.solutions;

    # SSL Configuration
    ssl_certificate /etc/ssl/smartsecurity/customer.crt;
    ssl_certificate_key /etc/ssl/smartsecurity/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend
    location / {
        proxy_pass http://frontend_cloud:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# Admin Console
server {
    listen 80;
    server_name admin.smartsecurity.solutions;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name admin.smartsecurity.solutions;

    # SSL Configuration
    ssl_certificate /etc/ssl/smartsecurity/admin.crt;
    ssl_certificate_key /etc/ssl/smartsecurity/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Admin Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Default server - redirect all HTTP to HTTPS
server {
    listen 80 default_server;
    server_name _;
    return 301 https://cloud.smartsecurity.solutions$request_uri;
}
EOF

print_success "HTTPS nginx configuration created"

# 4. Update docker-compose.yml for HTTPS
print_status "Updating docker-compose.yml for HTTPS..."

# Create a backup
cp docker-compose.yml docker-compose.yml.backup

# Update nginx service in docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-cloud}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-cloudpass}
      POSTGRES_DB: ${POSTGRES_DB:-cloud_db}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks: [backend]

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks: [backend]

  broker:
    image: eclipse-mosquitto:2
    restart: unless-stopped
    ports: ["1884:1883"]
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
    networks: [backend]

  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    env_file: .env
    ports: ["8082:8000"]
    depends_on: [db, redis, broker]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [backend]

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: ["python", "-m", "app.worker"]
    env_file: .env
    depends_on: [db, redis, broker]
    restart: unless-stopped
    networks: [backend]

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports: ["8083:80"]
    depends_on: [api]
    restart: unless-stopped
    networks: [backend]

  frontend_cloud:
    build:
      context: ./frontend_cloud
      dockerfile: Dockerfile
    depends_on: [api]
    restart: unless-stopped
    networks: [backend]

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"   # HTTP - redirects to HTTPS
      - "443:443" # HTTPS
    volumes:
      - ./nginx/conf.d/cloud-https.conf:/etc/nginx/conf.d/default.conf:ro
      - /etc/ssl/smartsecurity:/etc/ssl/smartsecurity:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - frontend_cloud
      - api
    restart: unless-stopped
    networks: [backend]

volumes:
  db_data:

networks:
  backend:
EOF

print_success "Docker Compose updated for HTTPS"

# 5. Update /etc/hosts for local testing
print_status "Updating /etc/hosts for local testing..."
if ! grep -q "cloud.smartsecurity.solutions" /etc/hosts; then
    echo "127.0.0.1 cloud.smartsecurity.solutions" | sudo tee -a /etc/hosts
fi
if ! grep -q "admin.smartsecurity.solutions" /etc/hosts; then
    echo "127.0.0.1 admin.smartsecurity.solutions" | sudo tee -a /etc/hosts
fi

print_success "Hosts file updated"

# 6. Restart services
print_status "Restarting services with HTTPS configuration..."
docker-compose down
docker-compose up -d

# 7. Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# 8. Test HTTPS
print_status "Testing HTTPS configuration..."

# Test HTTP to HTTPS redirect
if curl -I http://cloud.smartsecurity.solutions 2>/dev/null | grep -q "301"; then
    print_success "HTTP to HTTPS redirect working"
else
    print_warning "HTTP to HTTPS redirect may not be working"
fi

# Test HTTPS access
if curl -k -f https://cloud.smartsecurity.solutions > /dev/null 2>&1; then
    print_success "HTTPS access working"
else
    print_warning "HTTPS access may not be working"
fi

print_success "HTTPS setup completed!"
echo ""
echo "🌐 Access your application:"
echo "   Customer Portal: https://cloud.smartsecurity.solutions"
echo "   Admin Console:   https://admin.smartsecurity.solutions"
echo "   API Docs:        https://cloud.smartsecurity.solutions/api/v1/docs"
echo ""
echo "⚠️  Note: Using self-signed certificates for development."
echo "   For production, replace with Let's Encrypt certificates."
echo ""
echo "📋 Next steps:"
echo "1. Create admin user: python3 create_admin_via_api.py"
echo "2. Access the application via HTTPS"
echo "3. For production, set up Let's Encrypt certificates" 