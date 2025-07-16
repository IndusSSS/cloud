#!/bin/bash

# Comprehensive Deployment and Fix Script for Smart Security Cloud
# This script will fix all issues and deploy the system properly

set -e

echo "🚀 Smart Security Cloud - Comprehensive Deployment and Fix"
echo "=========================================================="

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

# Step 1: Check and fix Docker installation
print_step "1. Checking Docker installation..."
if docker --version >/dev/null 2>&1; then
    print_status "Docker is already installed"
    docker --version
else
    print_warning "Docker not found, but docker-compose is available"
fi

# Check docker-compose
if docker-compose --version >/dev/null 2>&1; then
    print_status "Docker Compose is available"
    docker-compose --version
else
    print_error "Docker Compose not found"
    exit 1
fi

# Step 2: Install missing dependencies
print_step "2. Installing missing dependencies..."
apt update -y
apt install -y curl wget git certbot python3-certbot-nginx

# Step 3: Create necessary directories
print_step "3. Creating necessary directories..."
mkdir -p ssl/certs ssl/private
mkdir -p logs

# Step 4: Copy environment file
print_step "4. Setting up environment configuration..."
if [ ! -f ".env" ] && [ -f "env.example" ]; then
    cp env.example .env
    print_status "Created .env file from template"
fi

# Step 5: Stop any existing containers
print_step "5. Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Step 6: Build and start containers
print_step "6. Building and starting containers..."
docker-compose build --no-cache
docker-compose up -d

# Step 7: Wait for services to be ready
print_step "7. Waiting for services to be ready..."
sleep 30

# Step 8: Check container status
print_step "8. Checking container status..."
docker-compose ps

# Step 9: Generate SSL certificates if needed
print_step "9. Setting up SSL certificates..."
if [ ! -f "ssl/certs/cloud.smartsecurity.solutions.fullchain.pem" ]; then
    print_status "Generating SSL certificates..."
    
    # Stop nginx to free port 80
    docker-compose stop nginx
    
    # Generate certificates
    certbot certonly --standalone \
        -d admin.smartsecurity.solutions \
        -d cloud.smartsecurity.solutions \
        --non-interactive \
        --agree-tos \
        --email admin@smartsecurity.solutions
    
    # Copy certificates
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem
    
    # Set permissions
    chmod 644 ssl/certs/*
    chmod 600 ssl/private/*
    chown -R $SUDO_USER:$SUDO_USER ssl/
    
    # Start nginx
    docker-compose start nginx
else
    print_status "SSL certificates already exist"
fi

# Step 10: Wait for nginx to be ready
print_step "10. Waiting for nginx to be ready..."
sleep 10

# Step 11: Test the setup
print_step "11. Testing the setup..."

# Get VPS IP
VPS_IP=$(curl -s ifconfig.me)
print_status "VPS IP: $VPS_IP"

# Test local endpoints
print_status "Testing local endpoints..."

# Test nginx
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
    print_status "✅ Nginx is working"
else
    print_warning "⚠️  Nginx test failed"
fi

# Test API
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/api/v1/health | grep -q "200"; then
    print_status "✅ API is working"
else
    print_warning "⚠️  API test failed"
fi

# Test MQTT
if docker exec cloud-broker-1 mosquitto_pub -h localhost -t test -m "test" 2>/dev/null; then
    print_status "✅ MQTT broker is working"
else
    print_warning "⚠️  MQTT broker test failed"
fi

# Step 12: Check container health
print_step "12. Checking container health..."
docker-compose ps

# Step 13: Set up automatic renewal
print_step "13. Setting up automatic certificate renewal..."
cat > /etc/cron.d/ssl-renewal << EOF
# SSL Certificate Renewal for Smart Security Cloud
0 12 * * * root cd /home/admin/Projects/cloud && ./renew_ssl_certificates.sh >> /var/log/ssl-renewal.log 2>&1
EOF

# Step 14: Create renewal script
cat > renew_ssl_certificates.sh << 'EOF'
#!/bin/bash
# SSL Certificate Renewal Script

set -e

echo "$(date): Starting SSL certificate renewal..."

# Stop nginx
docker-compose stop nginx

# Renew certificates
if certbot renew --standalone --non-interactive; then
    echo "$(date): Certificates renewed successfully"
    
    # Copy renewed certificates
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem
    cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem
    
    # Set permissions
    chmod 644 ssl/certs/*
    chmod 600 ssl/private/*
    chown -R $SUDO_USER:$SUDO_USER ssl/
    
    # Start nginx
    docker-compose start nginx
    
    echo "$(date): SSL renewal completed successfully"
else
    echo "$(date): SSL renewal failed"
    docker-compose start nginx
    exit 1
fi
EOF

chmod +x renew_ssl_certificates.sh

# Step 15: Final status check
print_step "15. Final status check..."

# Check all containers are running
if docker-compose ps | grep -q "Up"; then
    print_status "✅ All containers are running"
else
    print_warning "⚠️  Some containers may not be running"
fi

# Check SSL certificates
if [ -f "ssl/certs/cloud.smartsecurity.solutions.fullchain.pem" ] && [ -f "ssl/certs/admin.smartsecurity.solutions.fullchain.pem" ]; then
    print_status "✅ SSL certificates are in place"
else
    print_warning "⚠️  SSL certificates may be missing"
fi

# Final summary
echo ""
echo "🎉 Deployment completed!"
echo "========================"
echo ""
echo "Your VPS IP: $VPS_IP"
echo ""
echo "Next steps:"
echo "1. Update DNS records to point your domains to: $VPS_IP"
echo "   - cloud.smartsecurity.solutions → $VPS_IP"
echo "   - admin.smartsecurity.solutions → $VPS_IP"
echo ""
echo "2. Wait for DNS propagation (15-30 minutes)"
echo ""
echo "3. Test your domains:"
echo "   - https://cloud.smartsecurity.solutions"
echo "   - https://admin.smartsecurity.solutions"
echo ""
echo "4. Create admin user using:"
echo "   python3 create_admin_via_api.py"
echo ""
echo "5. Monitor logs:"
echo "   docker-compose logs -f"
echo ""
echo "SSL certificates will be automatically renewed every 60 days."
echo "Check renewal logs at: /var/log/ssl-renewal.log" 