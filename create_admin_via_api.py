#!/usr/bin/env python3
"""
Industry-Standard Admin User Creation via API
SmartSecurity Cloud - Secure Admin User Setup

This script creates a system administrator account through the API,
following industry best practices for user management.
"""

import requests
import json
import sys
import re
import getpass
from typing import Tuple
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
API_BASE_URL = "http://localhost:8082"  # Adjust if needed
API_ENDPOINTS = {
    "register": "/api/v1/auth/register",
    "login": "/api/v1/auth/login",
    "me": "/api/v1/auth/me",
    "admin_users": "/api/v1/admin/users"
}

# Headers
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be no more than 50 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address"
    
    return True, ""


def check_api_health() -> bool:
    """Check if the API is running and accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", headers=HEADERS, verify=False, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def create_admin_user_via_api(username: str, email: str, password: str) -> bool:
    """Create admin user via API registration endpoint."""
    url = f"{API_BASE_URL}{API_ENDPOINTS['register']}"
    
    # The API expects query parameters, not JSON body
    params = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, params=params, headers=HEADERS, verify=False, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User created successfully!")
            print(f"   User ID: {result.get('id', 'N/A')}")
            print(f"   Username: {result.get('username', username)}")
            print(f"   Email: {result.get('email', email)}")
            return True
        else:
            error_msg = response.text
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_msg)
            except:
                pass
            print(f"❌ Error creating user: {error_msg}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False


def login_and_verify_admin(username: str, password: str) -> bool:
    """Login and verify admin privileges."""
    url = f"{API_BASE_URL}{API_ENDPOINTS['login']}"
    
    # Use form data for login (OAuth2PasswordRequestForm)
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, data=data, headers=HEADERS, verify=False, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            
            if token:
                # Verify admin privileges
                return verify_admin_privileges(token)
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during login: {e}")
        return False


def verify_admin_privileges(token: str) -> bool:
    """Verify that the user has admin privileges."""
    url = f"{API_BASE_URL}{API_ENDPOINTS['me']}"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            is_admin = user_data.get('is_admin', False)
            
            if is_admin:
                print("✅ Admin privileges verified!")
                return True
            else:
                print("⚠️  User created but does not have admin privileges")
                print("   You may need to manually grant admin access")
                return False
        else:
            print(f"❌ Failed to verify admin privileges: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error during verification: {e}")
        return False


def main():
    """Main function for admin user creation."""
    print("🔐 SmartSecurity Cloud - Industry-Standard Admin Creation")
    print("=" * 60)
    print("This script creates a system administrator account via API.")
    print("Following industry best practices for secure user management.\n")
    
    # Check API health
    print("🔍 Checking API availability...")
    if not check_api_health():
        print("❌ API is not accessible. Please ensure:")
        print("   1. Docker containers are running: docker-compose ps")
        print("   2. API is healthy: docker-compose logs api")
        print("   3. Correct API URL is configured")
        return False
    
    print("✅ API is accessible\n")
    
    # Get user input with validation
    while True:
        username = input("Enter admin username: ").strip()
        is_valid, error = validate_username(username)
        if is_valid:
            break
        print(f"❌ {error}")
    
    while True:
        email = input("Enter admin email: ").strip()
        is_valid, error = validate_email(email)
        if is_valid:
            break
        print(f"❌ {error}")
    
    while True:
        password = getpass.getpass("Enter admin password: ")
        is_valid, error = validate_password(password)
        if is_valid:
            break
        print(f"❌ {error}")
        print("Password requirements:")
        print("  - At least 8 characters long")
        print("  - Contains uppercase and lowercase letters")
        print("  - Contains at least one number")
        print("  - Contains at least one special character")
    
    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("❌ Passwords do not match!")
        return False
    
    # Confirm creation
    print(f"\n📋 Admin Account Details:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")
    
    confirm = input("\nCreate this admin account? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Admin account creation cancelled.")
        return False
    
    # Create admin user
    print("\n🚀 Creating admin user via API...")
    if create_admin_user_via_api(username, email, password):
        print("\n🔐 Verifying admin privileges...")
        if login_and_verify_admin(username, password):
            print("\n🎉 Admin account setup completed successfully!")
            print("\n📋 Access Information:")
            print("   Admin Console: https://admin.smartsecurity.solutions")
            print("   Customer Portal: https://cloud.smartsecurity.solutions")
            print("   API Documentation: https://cloud.smartsecurity.solutions/api/v1/docs")
            print("\n⚠️  Security Notes:")
            print("   - Keep your credentials secure")
            print("   - Change password regularly")
            print("   - Monitor admin console access")
            return True
        else:
            print("\n⚠️  User created but admin privileges need manual verification")
            return False
    else:
        print("\n❌ Failed to create admin user")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 