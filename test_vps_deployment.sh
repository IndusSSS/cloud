#!/bin/bash

echo "🧪 SmartSecurity Cloud - VPS Deployment Test"
echo "============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test 1: Service Status
print_status "Checking Docker services..."
if docker-compose ps | grep -q "Up"; then
    print_success "Docker services are running"
else
    print_error "Docker services are not running"
fi

# Test 2: API Health
print_status "Testing API health..."
if curl -f http://localhost:8082/api/v1/health > /dev/null 2>&1; then
    print_success "API health check passed"
else
    print_error "API health check failed"
fi

# Test 3: Frontend Access
print_status "Testing frontend access..."
if curl -f http://localhost:80 > /dev/null 2>&1; then
    print_success "Frontend is accessible"
else
    print_error "Frontend is not accessible"
fi

# Test 4: Database Connection
print_status "Testing database connection..."
if docker-compose exec -T db psql -U postgres -d cloud_db -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database connection working"
else
    print_warning "Database connection failed (may be expected in fallback mode)"
fi

# Test 5: MQTT Broker
print_status "Testing MQTT broker..."
if docker-compose logs broker | grep -q "mosquitto version.*running"; then
    print_success "MQTT broker is running"
else
    print_error "MQTT broker is not running properly"
fi

# Test 6: External IP
print_status "Getting external IP..."
EXTERNAL_IP=$(curl -s ifconfig.me)
if [ ! -z "$EXTERNAL_IP" ]; then
    print_success "External IP: $EXTERNAL_IP"
    print_status "You can test external access at: http://$EXTERNAL_IP"
else
    print_warning "Could not determine external IP"
fi

# Test 7: Port Availability
print_status "Checking port availability..."
PORTS=(80 8082 8083 1884)
for port in "${PORTS[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        print_success "Port $port is listening"
    else
        print_warning "Port $port is not listening"
    fi
done

echo ""
echo "🎉 VPS Deployment Test Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Run: python3 create_admin_via_api.py"
echo "2. Access your application at: http://$EXTERNAL_IP"
echo "3. Check logs: docker-compose logs -f"
echo "4. Monitor resources: docker stats" 