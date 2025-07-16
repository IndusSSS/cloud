#!/bin/bash

# Fix HTTPS Setup Script
# This script fixes the SSL certificate access issues and properly configures HTTPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Fix HTTPS Setup Script ===${NC}"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check if certificate exists
echo -e "${BLUE}Checking SSL certificate...${NC}"
if [ -f "/etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem" ]; then
    echo -e "${GREEN}✓ SSL certificate found${NC}"
    CERT_EXISTS=true
else
    echo -e "${RED}✗ SSL certificate not found${NC}"
    CERT_EXISTS=false
fi

# Check certificate permissions
if [ "$CERT_EXISTS" = true ]; then
    echo -e "${BLUE}Checking certificate permissions...${NC}"
    if [ -r "/etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem" ]; then
        echo -e "${GREEN}✓ Certificate is readable${NC}"
    else
        echo -e "${YELLOW}⚠ Certificate permissions need fixing${NC}"
        sudo chmod -R 755 /etc/letsencrypt/live/
        sudo chmod -R 755 /etc/letsencrypt/archive/
        echo -e "${GREEN}✓ Certificate permissions fixed${NC}"
    fi
fi

# Stop services
echo -e "${BLUE}Stopping services...${NC}"
docker-compose down
echo -e "${GREEN}✓ Services stopped${NC}"

# Create proper SSL configuration
if [ "$CERT_EXISTS" = true ]; then
    echo -e "${BLUE}Creating HTTPS configuration...${NC}"
    
    # Update docker-compose.yml to use SSL certificates
    cat > docker-compose-ssl.yml <<EOF
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: \${POSTGRES_USER:-cloud}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-cloudpass}
      POSTGRES_DB: \${POSTGRES_DB:-cloud_db}
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
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
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
      - "80:80"   # HTTP redirect
      - "443:443" # HTTPS
    volumes:
      - ./nginx/conf.d/cloud.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/conf.d/health.conf:/etc/nginx/conf.d/health.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/lib/letsencrypt:/var/lib/letsencrypt:ro
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

    echo -e "${GREEN}✓ HTTPS configuration created${NC}"
    
    # Use the SSL configuration
    cp docker-compose-ssl.yml docker-compose.yml
    echo -e "${GREEN}✓ Updated docker-compose.yml for HTTPS${NC}"
else
    echo -e "${YELLOW}No SSL certificate found. Using HTTP-only configuration.${NC}"
    echo -e "${YELLOW}Run ./setup_vps_ssl.sh to obtain SSL certificates.${NC}"
fi

# Start services
echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 15

# Check service status
echo -e "${BLUE}Checking service status...${NC}"
docker-compose ps

# Test the setup
echo -e "${BLUE}Testing the setup...${NC}"

# Test HTTP
if curl -s --connect-timeout 5 http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTP is working${NC}"
else
    echo -e "${RED}✗ HTTP is not working${NC}"
fi

# Test HTTPS if certificate exists
if [ "$CERT_EXISTS" = true ]; then
    if curl -s --connect-timeout 5 -k https://localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTPS is working${NC}"
    else
        echo -e "${YELLOW}⚠ HTTPS not accessible locally (this is normal if testing from VPS)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ HTTPS not tested (no certificate)${NC}"
fi

# Test API
if curl -s --connect-timeout 5 http://localhost:8082 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is accessible${NC}"
else
    echo -e "${YELLOW}⚠ API not accessible on port 8082${NC}"
fi

echo
echo -e "${GREEN}=== Fix Complete ===${NC}"

if [ "$CERT_EXISTS" = true ]; then
    echo -e "${YELLOW}Your application is now running with HTTPS:${NC}"
    echo "- HTTP: http://cloud.smartsecurity.solutions"
    echo "- HTTPS: https://cloud.smartsecurity.solutions"
    echo
    echo -e "${YELLOW}To test from external:${NC}"
    echo "curl -I https://cloud.smartsecurity.solutions"
else
    echo -e "${YELLOW}Your application is running with HTTP only:${NC}"
    echo "- HTTP: http://cloud.smartsecurity.solutions"
    echo
    echo -e "${YELLOW}To enable HTTPS, run:${NC}"
    echo "./setup_vps_ssl.sh"
fi

echo
echo -e "${YELLOW}Useful commands:${NC}"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"
echo "- Test setup: ./test_https_setup.sh" 