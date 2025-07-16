#!/bin/bash

# Cloud Platform Startup Script
# Following MESSS Approach: Modular, Efficient, Secure, Scalable, Stable

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Modular: Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Secure: Validate SSL certificates
validate_ssl_certificates() {
    print_status "Validating SSL certificates..."
    
    if [[ ! -f "ssl/certs/cloud.crt" ]] || [[ ! -f "ssl/private/cloud.key" ]]; then
        print_error "SSL certificates not found. Please run the SSL setup first."
        exit 1
    fi
    
    # Check certificate validity
    if ! openssl x509 -checkend 0 -noout -in ssl/certs/cloud.crt; then
        print_error "SSL certificate has expired"
        exit 1
    fi
    
    print_success "SSL certificates validated"
}

# Efficient: Stop existing services
stop_existing_services() {
    print_status "Stopping existing services..."
    docker-compose down --remove-orphans 2>/dev/null || true
    print_success "Existing services stopped"
}

# Scalable: Start services in order
start_services() {
    print_status "Starting services in dependency order..."
    
    # Start core infrastructure first
    print_status "Starting database and cache..."
    docker-compose up -d db redis broker
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Start API and worker
    print_status "Starting API and worker..."
    docker-compose up -d api worker
    
    # Wait for API to be ready
    print_status "Waiting for API to be ready..."
    sleep 15
    
    # Start frontend services
    print_status "Starting frontend services..."
    docker-compose up -d frontend_cloud frontend_admin
    
    # Wait for frontends to be ready
    print_status "Waiting for frontend services to be ready..."
    sleep 10
    
    # Start nginx last
    print_status "Starting nginx reverse proxy..."
    docker-compose up -d nginx
    
    print_success "All services started"
}

# Stable: Health checks and monitoring
perform_health_checks() {
    print_status "Performing health checks..."
    
    # Wait for services to stabilize
    sleep 20
    
    # Check service status
    print_status "Checking service status..."
    docker-compose ps
    
    # Test HTTPS connectivity
    print_status "Testing HTTPS connectivity..."
    if curl -k -s -o /dev/null -w "%{http_code}" https://localhost | grep -q "200\|301\|302"; then
        print_success "HTTPS is working"
    else
        print_warning "HTTPS test failed, checking logs..."
        docker-compose logs nginx --tail=20
    fi
    
    # Test HTTP to HTTPS redirect
    print_status "Testing HTTP to HTTPS redirect..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "301\|302"; then
        print_success "HTTP to HTTPS redirect is working"
    else
        print_warning "HTTP to HTTPS redirect test failed"
    fi
}

# Main execution
main() {
    echo "🚀 Starting Cloud Platform (MESSS Approach)"
    echo "=========================================="
    
    check_prerequisites
    validate_ssl_certificates
    stop_existing_services
    start_services
    perform_health_checks
    
    echo ""
    echo "✅ Cloud Platform is ready!"
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
}

# Run main function
main "$@" 