#!/bin/bash

# Fix Frontend Admin Nginx Configuration
# This script rebuilds the frontend_admin container with the corrected nginx configuration

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

# Step 1: Stop all services
print_status "Stopping all services..."
docker-compose down
print_success "Services stopped"

# Step 2: Remove the problematic frontend_admin container and image
print_status "Removing old frontend_admin container and image..."
docker-compose rm -f frontend_admin 2>/dev/null || true
docker rmi cloud-frontend_admin 2>/dev/null || true
print_success "Old container and image removed"

# Step 3: Verify nginx configuration is correct
print_status "Verifying nginx configuration..."
if grep -q "must-revalidate" frontend_admin/nginx.conf; then
    print_error "nginx.conf still contains invalid 'must-revalidate' directive"
    exit 1
fi
print_success "nginx configuration is correct"

# Step 4: Rebuild frontend_admin
print_status "Rebuilding frontend_admin container..."
docker-compose build --no-cache frontend_admin
print_success "frontend_admin rebuilt successfully"

# Step 5: Start services
print_status "Starting all services..."
docker-compose up -d
print_success "Services started"

# Step 6: Wait for services to stabilize
print_status "Waiting for services to stabilize..."
sleep 15

# Step 7: Check service status
print_status "Checking service status..."
docker-compose ps

# Step 8: Test frontend_admin logs
print_status "Checking frontend_admin logs..."
if docker-compose logs frontend_admin --tail=5 | grep -q "must-revalidate"; then
    print_error "frontend_admin still has nginx configuration issues"
    docker-compose logs frontend_admin --tail=10
    exit 1
else
    print_success "frontend_admin nginx configuration is working"
fi

# Step 9: Test HTTPS connectivity
print_status "Testing HTTPS connectivity..."
if curl -k -s -o /dev/null -w "%{http_code}" https://localhost | grep -q "200\|301\|302"; then
    print_success "HTTPS is working correctly"
else
    print_warning "HTTPS test failed, checking nginx logs..."
    docker-compose logs nginx --tail=10
fi

# Step 10: Test HTTP to HTTPS redirect
print_status "Testing HTTP to HTTPS redirect..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "301\|302"; then
    print_success "HTTP to HTTPS redirect is working"
else
    print_warning "HTTP to HTTPS redirect test failed"
fi

echo ""
echo "✅ Frontend Admin Fix Complete!"
echo ""
echo "🌐 Access URLs:"
echo "  Cloud:   https://cloud.smartsecurity.solutions"
echo "  Admin:   https://admin.smartsecurity.solutions"
echo "  API:     https://cloud.smartsecurity.solutions/api/"
echo ""
echo "📊 Monitoring:"
echo "  Status:  docker-compose ps"
echo "  Logs:    docker-compose logs -f"
echo "  Health:  curl -k https://localhost/health"
echo "" 