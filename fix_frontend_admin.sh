#!/bin/bash

# Fix frontend_admin nginx configuration issue
echo "🔧 Fixing frontend_admin nginx configuration..."

# Stop the problematic container
echo "Stopping frontend_admin container..."
docker-compose stop frontend_admin

# Remove the container to force rebuild
echo "Removing frontend_admin container..."
docker-compose rm -f frontend_admin

# Rebuild the frontend_admin image
echo "Rebuilding frontend_admin image..."
docker-compose build frontend_admin

# Start the service
echo "Starting frontend_admin service..."
docker-compose up -d frontend_admin

# Wait a moment for the service to start
echo "Waiting for service to start..."
sleep 10

# Check the status
echo "Checking service status..."
docker-compose ps frontend_admin

# Check the logs
echo "Checking logs..."
docker-compose logs --tail=20 frontend_admin

echo "✅ Frontend admin fix completed!" 