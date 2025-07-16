#!/bin/bash

# Proper Environment Variable Fix Script
# This script correctly fixes the SECRET_KEY variable

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Proper Environment Variable Fix Script ===${NC}"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Create backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✓ Backup created${NC}"

# Create a new .env file with the correct SECRET_KEY
echo -e "${BLUE}Creating new .env file with correct SECRET_KEY...${NC}"

# Read the original .env file and replace the SECRET_KEY line
awk '
BEGIN { replaced = 0 }
/^SECRET_KEY=/ { 
    print "SECRET_KEY=\"Nmlc1Y3rLuglA*3%X\$5Q1IIaPReOYwibybAW6TA\$w6kNkSa%9gLgJuUL&Vel0dZU\"";
    replaced = 1;
    next;
}
{ print }
END { 
    if (replaced == 0) {
        print "SECRET_KEY=\"Nmlc1Y3rLuglA*3%X\$5Q1IIaPReOYwibybAW6TA\$w6kNkSa%9gLgJuUL&Vel0dZU\"";
    }
}
' .env.backup.* > .env.new

# Replace the original .env with the fixed one
mv .env.new .env

echo -e "${GREEN}✓ SECRET_KEY variable fixed properly${NC}"

# Verify the fix
echo -e "${BLUE}Verifying the fix...${NC}"
if grep -q 'SECRET_KEY="Nmlc1Y3rLuglA' .env; then
    echo -e "${GREEN}✓ SECRET_KEY is properly formatted${NC}"
else
    echo -e "${RED}✗ SECRET_KEY fix failed${NC}"
    exit 1
fi

# Restart services to apply changes
echo -e "${BLUE}Restarting services...${NC}"
docker-compose down
docker-compose up -d

echo -e "${GREEN}✓ Services restarted${NC}"
echo
echo -e "${GREEN}=== Fix Complete ===${NC}"
echo -e "${YELLOW}The Docker Compose warnings should now be resolved.${NC}" 