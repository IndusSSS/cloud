#!/bin/bash

# SSL Certificate Setup Script for Smart Security Cloud
# This script sets up SSL certificates for both domains

set -e

echo "🔒 Setting up SSL certificates for Smart Security Cloud..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Step 1: Stop nginx container to free up port 80
print_status "Stopping nginx container..."
docker-compose stop nginx

# Step 2: Create SSL directories
print_status "Creating SSL directories..."
mkdir -p ssl/certs
mkdir -p ssl/private

# Step 3: Get SSL certificates using certbot
print_status "Obtaining SSL certificates from Let's Encrypt..."
if certbot certonly --standalone -d admin.smartsecurity.solutions -d cloud.smartsecurity.solutions --non-interactive --agree-tos --email admin@smartsecurity.solutions; then
    print_status "SSL certificates obtained successfully!"
else
    print_error "Failed to obtain SSL certificates"
    print_status "Starting nginx container..."
    docker-compose start nginx
    exit 1
fi

# Step 4: Copy certificates to project directory
print_status "Copying certificates to project directory..."
cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem
cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem
cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem

# Step 5: Set proper permissions
print_status "Setting proper permissions..."
chmod 644 ssl/certs/*
chmod 600 ssl/private/*
chown -R $SUDO_USER:$SUDO_USER ssl/

# Step 6: Start nginx container
print_status "Starting nginx container..."
docker-compose start nginx

# Step 7: Wait for nginx to be ready
print_status "Waiting for nginx to be ready..."
sleep 10

# Step 8: Test the setup
print_status "Testing HTTPS setup..."

# Test cloud domain
if curl -s -o /dev/null -w "%{http_code}" https://cloud.smartsecurity.solutions | grep -q "200\|301\|302"; then
    print_status "✅ Cloud domain HTTPS is working!"
else
    print_warning "⚠️  Cloud domain HTTPS test failed"
fi

# Test admin domain
if curl -s -o /dev/null -w "%{http_code}" https://admin.smartsecurity.solutions | grep -q "200\|301\|302"; then
    print_status "✅ Admin domain HTTPS is working!"
else
    print_warning "⚠️  Admin domain HTTPS test failed"
fi

# Step 9: Set up automatic renewal
print_status "Setting up automatic certificate renewal..."
cat > /etc/cron.d/ssl-renewal << EOF
# SSL Certificate Renewal for Smart Security Cloud
0 12 * * * root cd /home/admin/Projects/cloud && ./renew_ssl_certificates.sh >> /var/log/ssl-renewal.log 2>&1
EOF

# Create renewal script
cat > renew_ssl_certificates.sh << 'EOF'
#!/bin/bash
# SSL Certificate Renewal Script

set -e

echo "$(date): Starting SSL certificate renewal..."

# Stop nginx
docker-compose stop nginx

# Renew certificates
if certbot renew --standalone --non-interactive; then
    echo "$(date): Certificates renewed successfully"
    
    # Copy renewed certificates
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem
    
    # Set permissions
    chmod 644 ssl/certs/*
    chmod 600 ssl/private/*
    chown -R $SUDO_USER:$SUDO_USER ssl/
    
    # Start nginx
    docker-compose start nginx
    
    echo "$(date): SSL renewal completed successfully"
else
    echo "$(date): SSL renewal failed"
    docker-compose start nginx
    exit 1
fi
EOF

chmod +x renew_ssl_certificates.sh

print_status "🎉 SSL setup completed successfully!"
print_status "Your domains are now accessible via HTTPS:"
print_status "  - https://cloud.smartsecurity.solutions"
print_status "  - https://admin.smartsecurity.solutions"
print_status ""
print_status "Certificates will be automatically renewed every 60 days."
print_status "You can check renewal logs at: /var/log/ssl-renewal.log" 