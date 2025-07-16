#!/bin/bash

# SmartSecurity Cloud VPS HTTPS Setup Script
# This script sets up the complete HTTPS configuration on VPS

set -e  # Exit on any error

echo "🔐 SmartSecurity Cloud VPS HTTPS Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Check if we're in the project directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory (where docker-compose.yml is located)"
    exit 1
fi

print_status "Starting VPS HTTPS setup..."

# 1. Create SSL directories
print_status "Creating SSL directories..."
mkdir -p ssl/certs ssl/private

# 2. Create nginx directory and configuration
print_status "Creating Nginx configuration..."
mkdir -p nginx

# Create main nginx.conf
cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'self';" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=()" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
}
EOF

# 3. Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_warning "Certbot not found. Installing..."
    sudo apt update
    sudo apt install -y certbot
fi

# 4. Check if domains are pointing to this server
print_warning "Please ensure your domains are pointing to this server's IP address:"
echo "  - cloud.smartsecurity.solutions"
echo "  - admin.smartsecurity.solutions"
echo ""
read -p "Are your domains configured? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please configure your DNS records first."
    exit 1
fi

# 5. Generate SSL certificates
print_status "Generating SSL certificates..."
sudo certbot certonly --standalone -d cloud.smartsecurity.solutions --non-interactive --agree-tos --email admin@smartsecurity.solutions
sudo certbot certonly --standalone -d admin.smartsecurity.solutions --non-interactive --agree-tos --email admin@smartsecurity.solutions

# 6. Copy certificates to SSL directories
print_status "Copying certificates..."
sudo cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.crt
sudo cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.key
sudo cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.crt
sudo cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.key

# 7. Set proper permissions
print_status "Setting file permissions..."
sudo chown -R $USER:$USER ssl/
chmod 600 ssl/private/*.key
chmod 644 ssl/certs/*.crt

# 8. Backup current docker-compose.yml
print_status "Backing up current configuration..."
cp docker-compose.yml docker-compose.yml.backup

# 9. Update docker-compose.yml with correct SSL configuration
print_status "Updating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Database
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: smartsecurity
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD:-admin123}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks: [backend]
    restart: unless-stopped

  # API Backend
  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD:-admin123}@db:5432/smartsecurity
      JWT_SECRET: ${JWT_SECRET:-your-secret-key}
      NODE_ENV: production
    depends_on:
      - db
    networks: [backend]
    restart: unless-stopped

  # Customer Portal Frontend
  frontend_cloud:
    build: ./frontend_customer
    environment:
      VITE_API_URL: https://cloud.smartsecurity.solutions/api
      NODE_ENV: production
    networks: [backend]
    restart: unless-stopped

  # Admin Console Frontend
  frontend_admin:
    build: ./frontend_admin
    environment:
      VITE_API_URL: https://admin.smartsecurity.solutions/api
      NODE_ENV: production
    networks: [backend]
    restart: unless-stopped

  # Nginx Reverse Proxy with SSL
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"   # HTTP redirect only
      - "443:443" # HTTPS only
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d/cloud.conf:/etc/nginx/conf.d/default.conf:ro
      # SSL certificates from Let's Encrypt
      - /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem:/etc/ssl/certs/cloud.smartsecurity.solutions.crt:ro
      - /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem:/etc/ssl/private/cloud.smartsecurity.solutions.key:ro
      - /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem:/etc/ssl/certs/admin.smartsecurity.solutions.crt:ro
      - /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem:/etc/ssl/private/admin.smartsecurity.solutions.key:ro
    depends_on:
      - frontend_cloud
      - frontend_admin
      - api
    restart: unless-stopped
    networks: [backend]

networks:
  backend:
    driver: bridge

volumes:
  db_data:
EOF

# 10. Stop any running containers
print_status "Stopping existing containers..."
docker-compose down || true

# 11. Start the application
print_status "Starting application with HTTPS..."
docker-compose up -d

# 12. Wait for containers to be ready
print_status "Waiting for containers to be ready..."
sleep 30

# 13. Test the setup
print_status "Testing HTTPS setup..."
if [ -f "vps_https_test.py" ]; then
    python3 vps_https_test.py
else
    print_warning "VPS test script not found. Running basic validation..."
    python3 validate_https_config.py
fi

# 14. Set up certificate renewal
print_status "Setting up certificate renewal..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx"; } | sudo crontab -

print_status "Setup complete!"
echo ""
echo "🎉 Your SmartSecurity Cloud is now running with HTTPS!"
echo ""
echo "📋 Next steps:"
echo "  - Test your domains: https://cloud.smartsecurity.solutions"
echo "  - Test admin console: https://admin.smartsecurity.solutions"
echo "  - Certificates will auto-renew daily at 12:00 PM"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Restart: docker-compose restart"
echo "  - Stop: docker-compose down"
echo "  - Update: git pull && docker-compose up -d --build" 