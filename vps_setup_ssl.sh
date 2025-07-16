#!/bin/bash

# VPS SSL Setup Script for Cloud Platform
# Industry Standard: RSA 2048-bit with SHA-256

set -e

echo "🔐 Setting up SSL certificates for Cloud Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Create SSL directories
print_status "Creating SSL directories..."
mkdir -p ssl/certs ssl/private

# Check if OpenSSL is installed
if ! command -v openssl &> /dev/null; then
    print_error "OpenSSL is not installed. Installing..."
    sudo apt update
    sudo apt install -y openssl
fi

# Generate private key (RSA 2048-bit)
print_status "Generating private key (RSA 2048-bit)..."
openssl genrsa -out ssl/private/cloud.key 2048
chmod 600 ssl/private/cloud.key
print_success "Private key generated: ssl/private/cloud.key"

# Generate certificate signing request (CSR) for cloud domain
print_status "Generating CSR for cloud.smartsecurity.solutions..."
openssl req -new -key ssl/private/cloud.key -out ssl/certs/cloud.csr -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=cloud.smartsecurity.solutions"

# Generate self-signed certificate for cloud domain (valid for 1 year)
print_status "Generating self-signed certificate for cloud domain..."
openssl x509 -req -in ssl/certs/cloud.csr -signkey ssl/private/cloud.key -out ssl/certs/cloud.crt -days 365 -sha256
print_success "Cloud certificate generated: ssl/certs/cloud.crt"

# Generate CSR for admin domain
print_status "Generating CSR for admin.smartsecurity.solutions..."
openssl req -new -key ssl/private/cloud.key -out ssl/certs/admin.csr -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=admin.smartsecurity.solutions"

# Generate self-signed certificate for admin domain
print_status "Generating self-signed certificate for admin domain..."
openssl x509 -req -in ssl/certs/admin.csr -signkey ssl/private/cloud.key -out ssl/certs/admin.crt -days 365 -sha256
print_success "Admin certificate generated: ssl/certs/admin.crt"

# Set proper permissions
print_status "Setting file permissions..."
chmod 644 ssl/certs/*.crt
chmod 600 ssl/private/*.key

# Verify certificates
print_status "Verifying certificates..."
echo "Cloud certificate:"
openssl x509 -in ssl/certs/cloud.crt -text -noout | grep "Subject:"
echo "Admin certificate:"
openssl x509 -in ssl/certs/admin.crt -text -noout | grep "Subject:"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
docker-compose up --build -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# Check service status
print_status "Checking service status..."
docker-compose ps

# Test HTTPS connectivity
print_status "Testing HTTPS connectivity..."
echo "Testing cloud domain..."
curl -k -I https://localhost 2>/dev/null | head -1 || print_warning "Cloud domain not accessible"
echo "Testing admin domain..."
curl -k -I https://localhost 2>/dev/null | head -1 || print_warning "Admin domain not accessible"

print_success "SSL setup completed!"
echo ""
echo "📋 Summary:"
echo "  Private Key: ssl/private/cloud.key"
echo "  Cloud Cert:  ssl/certs/cloud.crt"
echo "  Admin Cert:  ssl/certs/admin.crt"
echo "  CSR Files:   ssl/certs/*.csr"
echo ""
echo "🌐 Access URLs:"
echo "  Cloud:   https://cloud.smartsecurity.solutions"
echo "  Admin:   https://admin.smartsecurity.solutions"
echo ""
print_warning "Note: These are self-signed certificates for development/testing."
print_warning "For production, use Let's Encrypt or a trusted CA."
echo ""
echo "🔍 To check logs: docker-compose logs -f"
echo "🛑 To stop services: docker-compose down" 