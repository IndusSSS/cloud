#!/bin/bash

# Fix Docker Package Conflict Script
# This script resolves Docker installation conflicts

set -e

echo "🔧 Fixing Docker Package Conflicts"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Step 1: Check current Docker installation
print_step "1. Checking current Docker installation..."
docker --version 2>/dev/null && print_status "Docker is already installed" || print_warning "Docker not found"

# Step 2: Remove conflicting packages
print_step "2. Removing conflicting Docker packages..."
apt remove -y docker.io containerd 2>/dev/null || true
apt autoremove -y

# Step 3: Clean up Docker repositories
print_step "3. Cleaning up Docker repositories..."
rm -f /etc/apt/sources.list.d/docker.list
rm -f /etc/apt/sources.list.d/docker.list.save

# Step 4: Update package lists
print_step "4. Updating package lists..."
apt update

# Step 5: Install Docker properly
print_step "5. Installing Docker properly..."

# Install Docker using the official method
apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package lists again
apt update

# Install Docker Engine
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Step 6: Start and enable Docker
print_step "6. Starting and enabling Docker..."
systemctl start docker
systemctl enable docker

# Step 7: Add user to docker group
print_step "7. Adding user to docker group..."
usermod -aG docker $SUDO_USER

# Step 8: Verify installation
print_step "8. Verifying Docker installation..."
if docker --version; then
    print_status "✅ Docker installed successfully"
else
    print_error "❌ Docker installation failed"
    exit 1
fi

# Step 9: Test Docker
print_step "9. Testing Docker..."
if docker run hello-world; then
    print_status "✅ Docker is working correctly"
else
    print_warning "⚠️  Docker test failed, but installation may still be functional"
fi

# Step 10: Check docker-compose
print_step "10. Checking docker-compose..."
if docker compose version; then
    print_status "✅ Docker Compose is available"
else
    print_warning "⚠️  Docker Compose not found, installing separately..."
    apt install -y docker-compose
fi

print_status "🎉 Docker conflict resolved!"
print_status "You may need to log out and back in for group changes to take effect."
print_status "Or run: newgrp docker" 