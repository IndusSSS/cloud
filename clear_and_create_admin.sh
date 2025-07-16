#!/bin/bash

# Clear existing admin users and create new admin
echo "🧹 Clearing existing admin users..."

# Clear existing admin users from database
docker-compose exec db psql -U cloud -d cloud_db -c "DELETE FROM \"user\" WHERE is_admin = true;"

echo "✅ Existing admin users cleared!"

# Create new admin user
echo "🔐 Creating new admin user..."
docker-compose exec api python create_admin_user.py

echo "✅ Admin user creation completed!" 