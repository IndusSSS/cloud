#!/bin/bash

echo "🧹 Clearing Demo Data and Setting Up Single User Authentication"
echo "==============================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 1. Clear browser storage (instructions for user)
print_status "Clearing browser data..."
echo ""
echo "📋 Please clear your browser data:"
echo "1. Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)"
echo "2. Select 'All time' for time range"
echo "3. Check 'Cookies and site data' and 'Cached images and files'"
echo "4. Click 'Clear data'"
echo "5. Refresh the page"
echo ""

# 2. Clear Redis cache
print_status "Clearing Redis cache..."
docker-compose exec redis redis-cli FLUSHALL
print_success "Redis cache cleared"

# 3. Clear demo users from database
print_status "Clearing demo users from database..."
docker-compose exec db psql -U postgres -d cloud_db -c "
DELETE FROM users WHERE username = 'demo' OR username LIKE '%demo%';
DELETE FROM users WHERE email LIKE '%demo%';
"
print_success "Demo users cleared from database"

# 4. Restart services to clear any cached data
print_status "Restarting services..."
docker-compose restart api worker
print_success "Services restarted"

# 5. Test authentication
print_status "Testing authentication..."
sleep 10

# Test if demo user still exists
DEMO_EXISTS=$(curl -s -k https://admin.smartsecurity.solutions/api/v1/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo"}' | grep -c "Incorrect username or password" || echo "0")

if [ "$DEMO_EXISTS" -eq 1 ]; then
    print_success "Demo user authentication blocked"
else
    print_warning "Demo user might still exist"
fi

echo ""
print_success "Demo data clearing completed!"
echo ""
echo "🔐 Next Steps:"
echo "1. Clear your browser data (see instructions above)"
echo "2. Create your admin user: python3 create_admin_via_api.py"
echo "3. Login with your admin credentials"
echo "4. Only your authenticated user will have access"
echo ""
echo "⚠️  Important: The system will now only work with properly authenticated users." 