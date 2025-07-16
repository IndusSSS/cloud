#!/bin/bash

# Continue Deployment Script
# This script continues from where the main deployment script left off

set -e

echo "🚀 Continuing SmartSecurity Cloud Deployment"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 1. Create environment file
print_status "Creating environment file..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:password@db:5432/cloud_db
POSTGRES_DB=cloud_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# MQTT Configuration
MQTT_BROKER=broker
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# API Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=false
ENVIRONMENT=production

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost/api
NEXT_PUBLIC_WS_URL=ws://localhost/ws

# Worker Configuration
WORKER_ENABLED=true
WORKER_CONCURRENCY=4
EOF
    print_success "Environment file created"
else
    print_status "Environment file already exists"
fi

# 2. Start services
print_status "Starting SmartSecurity Cloud services..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 3. Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# 4. Check service status
print_status "Checking service status..."
docker-compose ps

# 5. Test basic connectivity
print_status "Testing basic connectivity..."

# Test API
if curl -f http://localhost:8082/health > /dev/null 2>&1; then
    print_success "API is accessible"
else
    print_warning "API health check failed, but service might still be starting"
fi

# Test frontend
if curl -f http://localhost:8083 > /dev/null 2>&1; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend check failed, but service might still be starting"
fi

# 6. Create admin user
print_status "Setting up admin user..."
if [ -f create_admin_user.py ]; then
    print_status "Running admin user creation script..."
    python3 create_admin_user.py
else
    print_warning "Admin user creation script not found"
fi

print_success "Deployment completed!"
echo ""
print_status "Your SmartSecurity Cloud is now running at:"
echo "- Frontend: http://localhost:8083"
echo "- API: http://localhost:8082"
echo "- Admin Frontend: http://localhost:8084 (if enabled)"
echo ""
print_status "Next steps:"
echo "1. Access the frontend and test the application"
echo "2. Create an admin user if not already done"
echo "3. Configure your domain and SSL certificates"
echo "4. Update the .env file with your actual domain"
echo ""
print_status "To view logs:"
echo "- All services: docker-compose logs -f"
echo "- Specific service: docker-compose logs -f [service_name]"
echo ""
print_status "To stop services:"
echo "docker-compose down" 