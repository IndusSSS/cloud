#!/usr/bin/env python3
"""
Test script to verify user creation functionality.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8001"
ADMIN_TOKEN = None  # You'll need to get this from login

def login_admin():
    """Login as admin to get token."""
    global ADMIN_TOKEN
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login-json", json=login_data)
        if response.status_code == 200:
            data = response.json()
            ADMIN_TOKEN = data["access_token"]
            print("✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_user_creation():
    """Test creating a user without email field."""
    if not ADMIN_TOKEN:
        print("❌ No admin token available")
        return False
    
    user_data = {
        "username": "testuser",
        "password": "testpass123",
        "is_admin": False,
        "tenant_id": None
    }
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print("Creating user with data:", user_data)
        response = requests.post(f"{BASE_URL}/api/v1/admin/users", json=user_data, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            user = response.json()
            print("✅ User created successfully!")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   ID: {user['id']}")
            return True
        else:
            print("❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return False

def test_list_users():
    """Test listing users."""
    if not ADMIN_TOKEN:
        print("❌ No admin token available")
        return False
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        
        print(f"List users response status: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users:")
            for user in users:
                print(f"   - {user['username']} ({user['email']})")
            return True
        else:
            print(f"❌ List users failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ List users error: {e}")
        return False

def main():
    print("🧪 Testing User Creation Functionality")
    print("=" * 50)
    
    # Step 1: Login as admin
    if not login_admin():
        return
    
    # Step 2: Test user creation
    if not test_user_creation():
        return
    
    # Step 3: Test listing users
    test_list_users()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 