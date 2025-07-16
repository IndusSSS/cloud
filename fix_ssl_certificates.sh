#!/bin/bash

# SSL Certificate Fix Script for Smart Security Cloud
# This script fixes the certificate copying issue

set -e

echo "🔧 Fixing SSL certificates for Smart Security Cloud..."

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

# Step 1: Check what certificates exist
print_status "Checking existing certificates..."
sudo ls -la /etc/letsencrypt/live/

print_status "Checking renewal configuration..."
sudo ls -la /etc/letsencrypt/renewal/

# Step 2: Create SSL directories
print_status "Creating SSL directories..."
mkdir -p ssl/certs
mkdir -p ssl/private

# Step 3: Check if we have a combined certificate or separate ones
if [ -d "/etc/letsencrypt/live/cloud.smartsecurity.solutions" ]; then
    print_status "Found separate certificate for cloud domain"
    CLOUD_CERT="/etc/letsencrypt/live/cloud.smartsecurity.solutions"
else
    print_warning "No separate cloud certificate found"
    CLOUD_CERT=""
fi

if [ -d "/etc/letsencrypt/live/admin.smartsecurity.solutions" ]; then
    print_status "Found separate certificate for admin domain"
    ADMIN_CERT="/etc/letsencrypt/live/admin.smartsecurity.solutions"
else
    print_warning "No separate admin certificate found"
    ADMIN_CERT=""
fi

# Step 4: Check for combined certificate
COMBINED_CERT=""
for cert_dir in /etc/letsencrypt/live/*; do
    if [ -d "$cert_dir" ] && [ -f "$cert_dir/fullchain.pem" ]; then
        # Check if this certificate covers both domains
        if openssl x509 -in "$cert_dir/fullchain.pem" -text -noout | grep -q "cloud.smartsecurity.solutions" && \
           openssl x509 -in "$cert_dir/fullchain.pem" -text -noout | grep -q "admin.smartsecurity.solutions"; then
            print_status "Found combined certificate: $cert_dir"
            COMBINED_CERT="$cert_dir"
            break
        fi
    fi
done

# Step 5: Copy certificates based on what we found
if [ -n "$COMBINED_CERT" ]; then
    print_status "Using combined certificate for both domains..."
    cp "$COMBINED_CERT/fullchain.pem" ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
    cp "$COMBINED_CERT/privkey.pem" ssl/private/cloud.smartsecurity.solutions.privkey.pem
    cp "$COMBINED_CERT/fullchain.pem" ssl/certs/admin.smartsecurity.solutions.fullchain.pem
    cp "$COMBINED_CERT/privkey.pem" ssl/private/admin.smartsecurity.solutions.privkey.pem
elif [ -n "$CLOUD_CERT" ] && [ -n "$ADMIN_CERT" ]; then
    print_status "Using separate certificates..."
    cp "$CLOUD_CERT/fullchain.pem" ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
    cp "$CLOUD_CERT/privkey.pem" ssl/private/cloud.smartsecurity.solutions.privkey.pem
    cp "$ADMIN_CERT/fullchain.pem" ssl/certs/admin.smartsecurity.solutions.fullchain.pem
    cp "$ADMIN_CERT/privkey.pem" ssl/private/admin.smartsecurity.solutions.privkey.pem
else
    print_error "No suitable certificates found. Let's create new ones..."
    
    # Stop nginx if running
    docker-compose stop nginx 2>/dev/null || true
    
    # Get new certificates
    certbot certonly --standalone \
        -d admin.smartsecurity.solutions \
        -d cloud.smartsecurity.solutions \
        --non-interactive \
        --agree-tos \
        --email admin@smartsecurity.solutions
    
    # Copy the new certificates
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem
fi

# Step 6: Set proper permissions
print_status "Setting proper permissions..."
chmod 644 ssl/certs/*
chmod 600 ssl/private/*
chown -R $SUDO_USER:$SUDO_USER ssl/

# Step 7: Start nginx container
print_status "Starting nginx container..."
docker-compose start nginx

# Step 8: Wait for nginx to be ready
print_status "Waiting for nginx to be ready..."
sleep 10

# Step 9: Test the setup
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

print_status "🎉 SSL certificate fix completed!"
print_status "Your domains should now be accessible via HTTPS:"
print_status "  - https://cloud.smartsecurity.solutions"
print_status "  - https://admin.smartsecurity.solutions" 