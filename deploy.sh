#!/bin/bash

echo "🚀 SmartSecurity Cloud Platform - VPS Deployment Script"
echo "=================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo apt install -y docker.io docker-compose-v2
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please logout and login again, then run this script again."
    exit 0
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating environment configuration..."
    python3 create_env.py
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Test API
echo "🧪 Testing API..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ API is running successfully!"
else
    echo "❌ API is not responding. Check logs with: docker-compose logs api"
fi

echo ""
echo "🎉 Deployment completed!"
echo "📱 Access your application at:"
echo "   - API: http://localhost:8000"
echo "   - Frontend: http://localhost:8080"
echo "   - Admin: http://localhost:8081"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Update: git pull && docker-compose up -d --build" 