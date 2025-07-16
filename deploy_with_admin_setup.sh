#!/bin/bash

# SmartSecurity Cloud - Complete VPS Deployment with Admin Setup
# This script deploys the application and guides through admin user creation

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System updated successfully"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing required packages..."
    
    # Install essential packages
    sudo apt install -y git curl wget docker.io docker-compose nginx certbot python3-certbot-nginx python3-pip
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Dependencies installed successfully"
    print_warning "You may need to log out and back in for Docker group changes to take effect"
}

# Function to clone repository
clone_repository() {
    print_status "Cloning SmartSecurity Cloud repository..."
    
    if [ -d "cloud" ]; then
        print_warning "Cloud directory already exists. Updating..."
        cd cloud
        git pull origin main
    else
        git clone https://github.com/IndusSSS/cloud.git
        cd cloud
    fi
    
    # Make scripts executable
    chmod +x *.sh
    chmod +x deploy_to_vps.sh
    chmod +x setup_vps_ssl.sh
    chmod +x complete_vps_setup.sh
    
    print_success "Repository cloned/updated successfully"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create environment file
    if [ ! -f ".env" ]; then
        python3 create_env.py
        print_success "Environment file created"
    else
        print_warning "Environment file already exists"
    fi
}

# Function to setup SSL certificates
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    # Generate self-signed certificates for development
    if [ -f "setup_vps_ssl.sh" ]; then
        ./setup_vps_ssl.sh
        print_success "SSL certificates generated"
    else
        print_warning "SSL setup script not found, skipping SSL setup"
    fi
}

# Function to start services
start_services() {
    print_status "Starting SmartSecurity Cloud services..."
    
    # Start Docker containers
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check service status
    docker-compose ps
    
    print_success "Services started successfully"
}

# Function to create admin user
create_admin_user() {
    print_status "Setting up admin user..."
    
    echo ""
    echo "=========================================="
    echo "🔐 ADMIN USER CREATION"
    echo "=========================================="
    echo "You need to create a system administrator account."
    echo "This account will have full access to the admin console."
    echo ""
    
    # Check if admin users already exist
    if python3 -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlmodel import select

async def check_admins():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.is_admin == True))
        admins = result.scalars().all()
        return len(admins)

count = asyncio.run(check_admins())
print(count)
" 2>/dev/null | grep -q "0"; then
        
        echo "No admin users found. Creating new admin account..."
        echo ""
        
        # Run admin creation script
        python3 create_admin_user.py
        
        echo ""
        print_success "Admin user creation completed"
    else
        echo "Admin users already exist. Skipping admin creation."
        echo "To create additional admin users, run: python create_admin_user.py"
    fi
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Test health endpoint
    if curl -k -s https://localhost/api/v1/health | grep -q "ok"; then
        print_success "Health check passed"
    else
        print_warning "Health check failed - services may still be starting"
    fi
    
    # Test admin console
    if curl -k -s https://localhost:8080 | grep -q "SmartSecurity"; then
        print_success "Admin console is accessible"
    else
        print_warning "Admin console may not be ready yet"
    fi
    
    echo ""
    print_success "Deployment verification completed"
}

# Function to display final instructions
display_instructions() {
    echo ""
    echo "=========================================="
    echo "🎉 DEPLOYMENT COMPLETED"
    echo "=========================================="
    echo ""
    echo "SmartSecurity Cloud has been deployed successfully!"
    echo ""
    echo "📋 Access URLs:"
    echo "   Admin Console: https://admin.smartsecurity.solutions"
    echo "   Customer Portal: https://cloud.smartsecurity.solutions"
    echo "   API Documentation: https://cloud.smartsecurity.solutions/api/v1/docs"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   Create admin user: python create_admin_user.py"
    echo "   List admin users: python create_admin_user.py --list"
    echo ""
    echo "📁 Important Files:"
    echo "   Environment: .env"
    echo "   SSL Certificates: ssl/"
    echo "   Docker Compose: docker-compose.yml"
    echo ""
    echo "⚠️  Security Notes:"
    echo "   - Keep your admin credentials secure"
    echo "   - Regularly update SSL certificates"
    echo "   - Monitor system logs for security events"
    echo ""
    echo "For support, check the documentation or contact the development team."
    echo ""
}

# Main deployment function
main() {
    echo "🚀 SmartSecurity Cloud - VPS Deployment"
    echo "========================================"
    echo ""
    
    # Check if running as root
    check_root
    
    # Check if running on supported system
    if ! command_exists apt; then
        print_error "This script is designed for Debian/Ubuntu systems"
        exit 1
    fi
    
    # Confirm deployment
    echo "This script will:"
    echo "1. Update system packages"
    echo "2. Install Docker and dependencies"
    echo "3. Clone/update the repository"
    echo "4. Setup environment and SSL certificates"
    echo "5. Start SmartSecurity Cloud services"
    echo "6. Guide you through admin user creation"
    echo ""
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps
    update_system
    install_dependencies
    clone_repository
    setup_environment
    setup_ssl
    start_services
    create_admin_user
    verify_deployment
    display_instructions
}

# Run main function
main "$@" 