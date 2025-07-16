#!/bin/bash

# Fix Environment File Script
# This script fixes the .env file with correct Docker service URLs

set -e

echo "🔧 Fixing .env file with correct Docker service URLs"
echo "===================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Step 1: Backup current .env file
print_status "Backing up current .env file..."
cp .env .env.backup

# Step 2: Create correct .env file
print_status "Creating correct .env file..."
cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=cloud
POSTGRES_PASSWORD=cloudpass
POSTGRES_DB=cloud_db
DATABASE_URL=postgresql+asyncpg://cloud:cloudpass@db:5432/cloud_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# MQTT Configuration
MQTT_BROKER=broker
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# API Configuration
API_PREFIX=/api/v1
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=52Xd8XzbHYkXeD2_-3Xy_WXZa8y-W2BHMdDlO3VQVNw
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Token Settings
API_TOKEN_SECRET=smartsecurity-cloud-api-token-secret-key-2024
API_TOKEN_ALGORITHM=HS256
API_TOKEN_EXPIRE_DAYS=365

# Development Mode
DEVELOPMENT_MODE=false
EOF

print_status "✅ .env file updated with correct Docker service URLs"

# Step 3: Set proper permissions
print_status "Setting proper permissions..."
chown $SUDO_USER:$SUDO_USER .env
chmod 644 .env

# Step 4: Restart containers
print_status "Restarting containers with new configuration..."
docker-compose down
docker-compose up -d

# Step 5: Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Step 6: Check container status
print_status "Checking container status..."
docker-compose ps

# Step 7: Test API health
print_status "Testing API health..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/api/v1/health | grep -q "200"; then
    print_status "✅ API is now healthy!"
else
    print_warning "⚠️  API health check failed, checking logs..."
    docker-compose logs api --tail=20
fi

print_status "🎉 Environment file fixed!"
print_status "Your containers should now be working properly." 