#!/bin/bash

# Fix Environment Variables Script
# This script fixes the SECRET_KEY variable that's causing Docker Compose warnings

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Fix Environment Variables Script ===${NC}"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Create backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✓ Backup created${NC}"

# Fix the SECRET_KEY variable
echo -e "${BLUE}Fixing SECRET_KEY variable...${NC}"
sed -i 's/SECRET_KEY=Nmlc1Y3rLuglA\*3%X\$5Q1IIaPReOYwibybAW6TA\$w6kNkSa%9gLgJuUL&Vel0dZU/SECRET_KEY="Nmlc1Y3rLuglA*3%X\$5Q1IIaPReOYwibybAW6TA\$w6kNkSa%9gLgJuUL&Vel0dZU"/' .env

echo -e "${GREEN}✓ SECRET_KEY variable fixed${NC}"

# Restart services to apply changes
echo -e "${BLUE}Restarting services...${NC}"
docker-compose down
docker-compose up -d

echo -e "${GREEN}✓ Services restarted${NC}"
echo
echo -e "${GREEN}=== Fix Complete ===${NC}"
echo -e "${YELLOW}The Docker Compose warnings should now be resolved.${NC}" 