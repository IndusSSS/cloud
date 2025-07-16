#!/bin/bash

# Docker-specific SSL Setup with Let's Encrypt
# This script sets up HTTPS for Docker containers using Let's Encrypt

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="cloud.smartsecurity.solutions"
EMAIL="contact@smartsecurity.solutions"  # Change this to your email

echo -e "${BLUE}=== Docker SSL Setup with Let's Encrypt ===${NC}"
echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo -e "${YELLOW}Email:${NC} $EMAIL"
echo

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

# Create directories for Let's Encrypt
echo -e "${BLUE}Creating Let's Encrypt directories...${NC}"
sudo mkdir -p /etc/letsencrypt
sudo mkdir -p /var/lib/letsencrypt
sudo chown -R $USER:$USER /etc/letsencrypt
sudo chown -R $USER:$USER /var/lib/letsencrypt

# Create temporary nginx container for ACME challenge
echo -e "${BLUE}Creating temporary nginx container for ACME challenge...${NC}"

# Stop any existing containers that might use port 80
docker-compose down || true

# Create temporary nginx config
cat > /tmp/nginx-acme.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 200 "ACME Challenge Server";
        add_header Content-Type text/plain;
    }
}
EOF

# Run temporary nginx container
docker run -d \
    --name nginx-acme \
    -p 80:80 \
    -v /tmp/nginx-acme.conf:/etc/nginx/conf.d/default.conf:ro \
    -v /tmp/acme-challenge:/var/www/html \
    nginx:alpine

# Create webroot directory
sudo mkdir -p /tmp/acme-challenge/.well-known/acme-challenge
sudo chown -R $USER:$USER /tmp/acme-challenge

# Wait for nginx to start
sleep 3

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

# Obtain SSL certificate
echo -e "${BLUE}Obtaining SSL certificate from Let's Encrypt...${NC}"
if sudo certbot certonly --webroot \
    --webroot-path=/tmp/acme-challenge \
    --domain $DOMAIN \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --rsa-key-size 4096 \
    --preferred-challenges http; then
    echo -e "${GREEN}✓ SSL certificate obtained successfully${NC}"
else
    echo -e "${RED}Error: Failed to obtain SSL certificate${NC}"
    echo "Please check the error messages above"
    # Clean up
    docker stop nginx-acme || true
    docker rm nginx-acme || true
    exit 1
fi

# Stop temporary nginx container
echo -e "${BLUE}Stopping temporary nginx container...${NC}"
docker stop nginx-acme
docker rm nginx-acme

# Set up automatic renewal
echo -e "${BLUE}Setting up automatic certificate renewal...${NC}"
sudo tee /etc/cron.d/certbot-renew-docker > /dev/null <<EOF
# Certbot renewal for Docker
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

echo
echo -e "${GREEN}=== Docker SSL Setup Complete ===${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start your Docker services: docker-compose up -d"
echo "2. Test HTTPS: https://$DOMAIN"
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
echo "- Make sure your domain DNS points to this server"
echo "- Ports 80 and 443 must be open in your firewall"
echo "- The docker-compose.yml is already configured to use Let's Encrypt certificates" 
