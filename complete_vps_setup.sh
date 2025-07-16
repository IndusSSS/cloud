#!/bin/bash

# Complete VPS Setup Script
# This script handles the entire VPS deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Complete VPS Setup Script ===${NC}"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose is installed${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create the .env file with your configuration"
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

# Make all scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x *.sh
echo -e "${GREEN}✓ Scripts made executable${NC}"

# Fix environment variables
echo -e "${BLUE}Fixing environment variables...${NC}"
if [ -f "fix_env_variables.sh" ]; then
    ./fix_env_variables.sh
    echo -e "${GREEN}✓ Environment variables fixed${NC}"
else
    echo -e "${YELLOW}⚠ Environment fix script not found, continuing...${NC}"
fi

# Check SSL certificate status
echo -e "${BLUE}Checking SSL certificate status...${NC}"
if [ -f "/etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem" ]; then
    echo -e "${GREEN}✓ SSL certificate found${NC}"
    SSL_EXISTS=true
else
    echo -e "${YELLOW}⚠ SSL certificate not found${NC}"
    SSL_EXISTS=false
fi

# Run SSL setup if needed
if [ "$SSL_EXISTS" = false ]; then
    echo -e "${BLUE}Setting up SSL certificates...${NC}"
    if [ -f "setup_vps_ssl.sh" ]; then
        ./setup_vps_ssl.sh
        echo -e "${GREEN}✓ SSL setup completed${NC}"
    else
        echo -e "${RED}Error: SSL setup script not found${NC}"
        exit 1
    fi
fi

# Run HTTPS fix
echo -e "${BLUE}Configuring HTTPS...${NC}"
if [ -f "fix_https_setup.sh" ]; then
    ./fix_https_setup.sh
    echo -e "${GREEN}✓ HTTPS configuration completed${NC}"
else
    echo -e "${RED}Error: HTTPS fix script not found${NC}"
    exit 1
fi

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 20

# Check service status
echo -e "${BLUE}Checking service status...${NC}"
docker-compose ps

# Test the setup
echo -e "${BLUE}Testing the complete setup...${NC}"
if [ -f "test_https_setup.sh" ]; then
    ./test_https_setup.sh
else
    echo -e "${YELLOW}⚠ Test script not found, running basic tests...${NC}"
    
    # Basic tests
    if curl -s --connect-timeout 5 http://localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTP is working${NC}"
    else
        echo -e "${RED}✗ HTTP is not working${NC}"
    fi
    
    if curl -s --connect-timeout 5 -k https://localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTPS is working${NC}"
    else
        echo -e "${YELLOW}⚠ HTTPS not accessible locally (normal if testing from VPS)${NC}"
    fi
fi

echo
echo -e "${GREEN}=== Complete VPS Setup Finished ===${NC}"
echo
echo -e "${YELLOW}Your application is now running at:${NC}"
echo "- HTTP: http://cloud.smartsecurity.solutions"
echo "- HTTPS: https://cloud.smartsecurity.solutions"
echo
echo -e "${YELLOW}Service URLs:${NC}"
echo "- API: http://localhost:8082"
echo "- Frontend: http://localhost:8083"
echo
echo -e "${YELLOW}Useful commands:${NC}"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"
echo "- Restart services: docker-compose restart"
echo "- Check status: docker-compose ps"
echo
echo -e "${YELLOW}Monitoring:${NC}"
echo "- Monitor logs: docker-compose logs -f"
echo "- Check health: docker-compose ps"
echo "- Test external: curl -I https://cloud.smartsecurity.solutions" 