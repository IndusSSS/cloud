#!/bin/bash

# Fix frontend_admin nginx configuration issue
# This script addresses the "host not found in upstream 'backend'" error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔧 Fixing Frontend Admin Nginx Configuration"
echo "==========================================="

# Step 1: Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

# Step 2: Stop the problematic container
print_status "Stopping frontend_admin container..."
docker-compose stop frontend_admin 2>/dev/null || true

# Step 3: Remove the container to force rebuild
print_status "Removing frontend_admin container..."
docker-compose rm -f frontend_admin 2>/dev/null || true

# Step 4: Verify the nginx configuration is correct
print_status "Verifying nginx configuration..."
if grep -q "proxy_pass http://api:8000/api/" frontend_admin/nginx.conf; then
    print_success "nginx configuration is correct (points to api:8000)"
else
    print_error "nginx configuration is incorrect. Expected 'api:8000' but found something else."
    grep "proxy_pass" frontend_admin/nginx.conf || echo "No proxy_pass found"
    exit 1
fi

# Step 5: Check if API service is running
print_status "Checking API service status..."
if docker-compose ps api | grep -q "Up"; then
    print_success "API service is running"
else
    print_warning "API service is not running. Starting it..."
    docker-compose up -d api
    sleep 10
fi

# Step 6: Rebuild frontend_admin
print_status "Rebuilding frontend_admin container..."
docker-compose build --no-cache frontend_admin
print_success "frontend_admin rebuilt successfully"

# Step 7: Start frontend_admin
print_status "Starting frontend_admin service..."
docker-compose up -d frontend_admin

# Step 8: Wait for service to start
print_status "Waiting for service to start..."
sleep 15

# Step 9: Check the status
print_status "Checking service status..."
docker-compose ps frontend_admin

# Step 10: Check the logs
print_status "Checking logs..."
if docker-compose logs --tail=10 frontend_admin | grep -q "host not found in upstream"; then
    print_error "nginx configuration still has issues"
    docker-compose logs --tail=20 frontend_admin
    exit 1
else
    print_success "frontend_admin is running without nginx errors"
fi

# Step 11: Test the health endpoint
print_status "Testing health endpoint..."
if curl -s http://localhost:8083/health > /dev/null 2>&1; then
    print_success "Health endpoint is accessible"
else
    print_warning "Health endpoint test failed (this might be normal if port 8083 is not exposed)"
fi

echo ""
echo "✅ Frontend Admin Fix Complete!"
echo ""
echo "📊 Service Status:"
docker-compose ps frontend_admin
echo ""
echo "📋 Recent Logs:"
docker-compose logs --tail=5 frontend_admin
echo ""
echo "🌐 Access URLs:"
echo "  Admin Frontend: http://localhost:8083 (if exposed)"
echo "  API: http://localhost:8082/api/v1/health"
echo "" 