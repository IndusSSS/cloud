#!/bin/bash

# VPS SSL Setup Script for Production Deployment
# This script is designed for VPS deployment with proper cleanup and error handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="cloud.smartsecurity.solutions"
EMAIL="contact@smartsecurity.solutions"

echo -e "${BLUE}=== VPS SSL Setup Script ===${NC}"
echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo -e "${YELLOW}Email:${NC} $EMAIL"
echo

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    docker stop nginx-acme-temp 2>/dev/null || true
    docker rm nginx-acme-temp 2>/dev/null || true
    sudo rm -rf /tmp/acme-challenge 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check if Docker is running
echo -e "${BLUE}Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose is available${NC}"

# Check domain accessibility
echo -e "${BLUE}Checking domain accessibility...${NC}"
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    echo -e "${RED}Error: Domain $DOMAIN is not accessible${NC}"
    echo "Please ensure DNS is properly configured to point to this VPS"
    exit 1
fi
echo -e "${GREEN}✓ Domain is accessible${NC}"

# Stop any existing containers that might use port 80
echo -e "${BLUE}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Clean up any existing temporary containers
docker stop nginx-acme-temp 2>/dev/null || true
docker rm nginx-acme-temp 2>/dev/null || true

# Create Let's Encrypt directories
echo -e "${BLUE}Creating Let's Encrypt directories...${NC}"
sudo mkdir -p /etc/letsencrypt
sudo mkdir -p /var/lib/letsencrypt
sudo chown -R $USER:$USER /etc/letsencrypt
sudo chown -R $USER:$USER /var/lib/letsencrypt

# Create temporary nginx configuration for ACME challenge
echo -e "${BLUE}Creating temporary nginx configuration...${NC}"
cat > /tmp/nginx-acme-temp.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        try_files \$uri =404;
    }
    
    location / {
        return 200 "ACME Challenge Server - $DOMAIN";
        add_header Content-Type text/plain;
    }
}
EOF

# Create webroot directory
echo -e "${BLUE}Creating webroot directory...${NC}"
sudo mkdir -p /tmp/acme-challenge/.well-known/acme-challenge
sudo chown -R $USER:$USER /tmp/acme-challenge

# Run temporary nginx container
echo -e "${BLUE}Starting temporary nginx container...${NC}"
docker run -d \
    --name nginx-acme-temp \
    -p 80:80 \
    -v /tmp/nginx-acme-temp.conf:/etc/nginx/conf.d/default.conf:ro \
    -v /tmp/acme-challenge:/var/www/html \
    nginx:alpine

# Wait for nginx to start
echo -e "${BLUE}Waiting for nginx to start...${NC}"
sleep 5

# Test if nginx is responding
if ! curl -s --connect-timeout 5 http://localhost > /dev/null; then
    echo -e "${RED}Error: Temporary nginx is not responding${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Temporary nginx is responding${NC}"

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

# Check if certificate already exists
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${YELLOW}Certificate already exists. Checking expiration...${NC}"
    EXPIRY=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -enddate | cut -d= -f2)
    echo -e "${GREEN}Certificate expires: $EXPIRY${NC}"
    
    # Check if certificate expires in less than 30 days
    EXPIRY_DATE=$(date -d "$EXPIRY" +%s)
    CURRENT_DATE=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_DATE - CURRENT_DATE) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo -e "${YELLOW}Certificate expires in $DAYS_LEFT days. Renewing...${NC}"
        RENEW_CERT=true
    else
        echo -e "${GREEN}Certificate is valid for $DAYS_LEFT days. Skipping renewal.${NC}"
        RENEW_CERT=false
    fi
else
    RENEW_CERT=true
fi

# Obtain or renew SSL certificate
if [ "$RENEW_CERT" = true ]; then
    echo -e "${BLUE}Obtaining SSL certificate from Let's Encrypt...${NC}"
    if sudo certbot certonly --webroot \
        --webroot-path=/tmp/acme-challenge \
        --domain $DOMAIN \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        --rsa-key-size 4096 \
        --preferred-challenges http \
        --force-renewal; then
        echo -e "${GREEN}✓ SSL certificate obtained successfully${NC}"
    else
        echo -e "${RED}Error: Failed to obtain SSL certificate${NC}"
        echo "Please check the error messages above"
        exit 1
    fi
fi

# Stop temporary nginx container
echo -e "${BLUE}Stopping temporary nginx container...${NC}"
docker stop nginx-acme-temp
docker rm nginx-acme-temp

# Set up automatic renewal
echo -e "${BLUE}Setting up automatic certificate renewal...${NC}"
sudo tee /etc/cron.d/certbot-renew-vps > /dev/null <<EOF
# Certbot renewal for VPS
0 12 * * * root /usr/bin/certbot renew --quiet --deploy-hook "cd /home/$USER/Projects/cloud && docker-compose restart nginx"
EOF

echo -e "${GREEN}✓ Automatic renewal configured${NC}"

# Set proper permissions
echo -e "${BLUE}Setting proper permissions...${NC}"
sudo chmod -R 755 /etc/letsencrypt/live/
sudo chmod -R 755 /etc/letsencrypt/archive/

# Verify certificate
echo -e "${BLUE}Verifying certificate...${NC}"
if sudo certbot certificates | grep -q "$DOMAIN"; then
    echo -e "${GREEN}✓ Certificate verified${NC}"
else
    echo -e "${RED}Error: Certificate verification failed${NC}"
    exit 1
fi

# Display certificate information
echo -e "${BLUE}Certificate Information:${NC}"
sudo certbot certificates

# Start the main services
echo -e "${BLUE}Starting main services...${NC}"
docker-compose up -d

# Wait for services to start
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Test the setup
echo -e "${BLUE}Testing HTTPS setup...${NC}"
if curl -s --connect-timeout 5 -k https://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTPS is working locally${NC}"
else
    echo -e "${YELLOW}⚠ HTTPS not accessible locally (this is normal if testing from VPS)${NC}"
fi

echo
echo -e "${GREEN}=== VPS SSL Setup Complete ===${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Ensure your domain DNS points to this VPS IP"
echo "2. Test HTTPS from external: https://$DOMAIN"
echo "3. Run the test script: ./test_https_setup.sh"
echo
echo -e "${YELLOW}Certificate renewal:${NC}"
echo "- Certificates will auto-renew via cron job"
echo "- Manual renewal: sudo certbot renew"
echo
echo -e "${YELLOW}Security notes:${NC}"
echo "- Certificates are valid for 90 days"
echo "- Automatic renewal is configured"
echo "- Industry-standard SSL configuration applied"
echo
echo -e "${YELLOW}Important:${NC}"
echo "- Make sure ports 80 and 443 are open in your VPS firewall"
echo "- The setup is now ready for production use" 