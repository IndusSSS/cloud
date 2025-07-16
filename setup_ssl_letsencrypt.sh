#!/bin/bash

# Industry Standard SSL Setup with Let's Encrypt
# This script sets up HTTPS using Let's Encrypt certificates with best practices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="cloud.smartsecurity.solutions"
EMAIL="admin@smartsecurity.solutions"  # Change this to your email
CERTBOT_OPTS="--non-interactive --agree-tos --email $EMAIL"

echo -e "${BLUE}=== Industry Standard SSL Setup with Let's Encrypt ===${NC}"
echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo -e "${YELLOW}Email:${NC} $EMAIL"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check if domain is accessible
echo -e "${BLUE}Checking domain accessibility...${NC}"
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    echo -e "${RED}Error: Domain $DOMAIN is not accessible${NC}"
    echo "Please ensure DNS is properly configured to point to this server"
    exit 1
fi
echo -e "${GREEN}✓ Domain is accessible${NC}"

# Check if ports 80 and 443 are open
echo -e "${BLUE}Checking port availability...${NC}"
if ! sudo netstat -tlnp | grep -q ":80 "; then
    echo -e "${YELLOW}Warning: Port 80 is not in use${NC}"
    echo "This is required for Let's Encrypt HTTP challenge"
fi

if ! sudo netstat -tlnp | grep -q ":443 "; then
    echo -e "${YELLOW}Warning: Port 443 is not in use${NC}"
    echo "This is required for HTTPS"
fi

# Install Certbot if not present
echo -e "${BLUE}Installing Certbot...${NC}"
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt update
    sudo apt install -y certbot
    echo -e "${GREEN}✓ Certbot installed${NC}"
else
    echo -e "${GREEN}✓ Certbot already installed${NC}"
fi

# Create temporary nginx config for ACME challenge
echo -e "${BLUE}Creating temporary nginx configuration for ACME challenge...${NC}"
sudo tee /tmp/nginx-acme.conf > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF

# Create webroot directory
sudo mkdir -p /var/www/html/.well-known/acme-challenge

# Test nginx configuration
echo -e "${BLUE}Testing nginx configuration...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}Error: Nginx configuration is invalid${NC}"
    exit 1
fi

# Stop existing nginx if running
echo -e "${BLUE}Stopping existing nginx...${NC}"
sudo systemctl stop nginx || true

# Start nginx with temporary config
echo -e "${BLUE}Starting nginx with temporary configuration...${NC}"
sudo nginx -c /tmp/nginx-acme.conf

# Obtain SSL certificate
echo -e "${BLUE}Obtaining SSL certificate from Let's Encrypt...${NC}"
if sudo certbot certonly --webroot \
    --webroot-path=/var/www/html \
    --domain $DOMAIN \
    $CERTBOT_OPTS \
    --rsa-key-size 4096 \
    --preferred-challenges http; then
    echo -e "${GREEN}✓ SSL certificate obtained successfully${NC}"
else
    echo -e "${RED}Error: Failed to obtain SSL certificate${NC}"
    echo "Please check the error messages above"
    exit 1
fi

# Stop temporary nginx
echo -e "${BLUE}Stopping temporary nginx...${NC}"
sudo nginx -s quit || true

# Verify certificate
echo -e "${BLUE}Verifying certificate...${NC}"
if sudo certbot certificates | grep -q "$DOMAIN"; then
    echo -e "${GREEN}✓ Certificate verified${NC}"
else
    echo -e "${RED}Error: Certificate verification failed${NC}"
    exit 1
fi

# Set up automatic renewal
echo -e "${BLUE}Setting up automatic certificate renewal...${NC}"
sudo tee /etc/cron.d/certbot-renew > /dev/null <<EOF
# Certbot renewal
0 12 * * * root /usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"
EOF

echo -e "${GREEN}✓ Automatic renewal configured${NC}"

# Set proper permissions
echo -e "${BLUE}Setting proper permissions...${NC}"
sudo chmod -R 755 /etc/letsencrypt/live/
sudo chmod -R 755 /etc/letsencrypt/archive/

# Create SSL configuration with industry best practices
echo -e "${BLUE}Creating optimized SSL configuration...${NC}"
sudo tee /etc/nginx/snippets/ssl-params.conf > /dev/null <<EOF
# SSL Configuration with industry best practices
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security Headers
add_header Strict-Transport-Security "max-age=63072000" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
EOF

echo -e "${GREEN}✓ SSL configuration created${NC}"

# Test final configuration
echo -e "${BLUE}Testing final nginx configuration...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ Final nginx configuration is valid${NC}"
else
    echo -e "${RED}Error: Final nginx configuration is invalid${NC}"
    exit 1
fi

# Display certificate information
echo -e "${BLUE}Certificate Information:${NC}"
sudo certbot certificates

echo
echo -e "${GREEN}=== SSL Setup Complete ===${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update your docker-compose.yml to use the Let's Encrypt certificates"
echo "2. Start your Docker services: docker-compose up -d"
echo "3. Test HTTPS: https://$DOMAIN"
echo
echo -e "${YELLOW}Certificate renewal:${NC}"
echo "- Certificates will auto-renew via cron job"
echo "- Manual renewal: sudo certbot renew"
echo
echo -e "${YELLOW}Security notes:${NC}"
echo "- Certificates are valid for 90 days"
echo "- Automatic renewal is configured"
echo "- Industry-standard SSL configuration applied" 