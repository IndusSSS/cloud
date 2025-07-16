#!/bin/bash

# Fix nginx SSL certificate issue
echo "🔧 Fixing nginx SSL certificate issue..."

# Stop all services
echo "Stopping all services..."
docker-compose down

# Remove the problematic nginx container and image
echo "Removing old nginx container and image..."
docker-compose rm -f nginx 2>/dev/null || true
docker rmi cloud-nginx 2>/dev/null || true

# Rebuild nginx with proper SSL handling
echo "Rebuilding nginx with proper SSL handling..."
docker-compose build nginx

# Start all services
echo "Starting all services..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 15

# Check the status
echo "Checking service status..."
docker-compose ps

# Check nginx logs specifically
echo "Checking nginx logs..."
docker-compose logs --tail=10 nginx

echo "✅ Nginx SSL fix completed!" 