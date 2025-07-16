#!/bin/bash

# VPS Deployment Script
# This script deploys the application to a VPS with proper SSL setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== VPS Deployment Script ===${NC}"
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
    echo "Please install Docker first: https://docs.docker.com/engine/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    echo "Please install docker-compose first"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose is installed${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker first: sudo systemctl start docker"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Stop any existing containers
echo -e "${BLUE}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Existing containers stopped${NC}"

# Build images
echo -e "${BLUE}Building Docker images...${NC}"
docker-compose build
echo -e "${GREEN}✓ Images built successfully${NC}"

# Check if SSL setup is needed
if [ ! -f "/etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem" ]; then
    echo -e "${YELLOW}SSL certificates not found. Running SSL setup...${NC}"
    ./setup_vps_ssl.sh
else
    echo -e "${GREEN}✓ SSL certificates found${NC}"
    
    # Start services
    echo -e "${BLUE}Starting services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Services started successfully${NC}"
fi

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 15

# Check service status
echo -e "${BLUE}Checking service status...${NC}"
docker-compose ps

# Test the application
echo -e "${BLUE}Testing application...${NC}"

# Test API
if curl -s --connect-timeout 5 http://localhost:8082/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${YELLOW}⚠ API not responding (may still be starting)${NC}"
fi

# Test frontend
if curl -s --connect-timeout 5 http://localhost:8083 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is responding${NC}"
else
    echo -e "${YELLOW}⚠ Frontend not responding (may still be starting)${NC}"
fi

# Test HTTPS (if accessible)
if curl -s --connect-timeout 5 -k https://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTPS is working${NC}"
else
    echo -e "${YELLOW}⚠ HTTPS not accessible locally (normal if testing from VPS)${NC}"
fi

echo
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${YELLOW}Service URLs:${NC}"
echo "- API: http://localhost:8082"
echo "- Frontend: http://localhost:8083"
echo "- HTTPS: https://cloud.smartsecurity.solutions"
echo
echo -e "${YELLOW}Useful commands:${NC}"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"
echo "- Restart services: docker-compose restart"
echo "- Test SSL: ./test_https_setup.sh"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Ensure your domain DNS points to this VPS IP"
echo "2. Test from external: https://cloud.smartsecurity.solutions"
echo "3. Monitor logs: docker-compose logs -f" 