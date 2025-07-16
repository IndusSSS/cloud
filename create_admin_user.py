#!/usr/bin/env python3
"""
Secure System Admin User Creation Script

This script creates a system admin user with a user-defined password.
It should be run once during initial setup to create the primary admin account.
"""

import asyncio
import getpass
import re
import sys
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Returns:
        (is_valid, error_message)
    """
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


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.
    
    Returns:
        (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be no more than 50 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format.
    
    Returns:
        (is_valid, error_message)
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address"
    
    return True, ""


async def create_system_admin() -> None:
    """Create a system admin user interactively."""
    print("🔐 SmartSecurity Cloud - System Admin Creation")
    print("=" * 50)
    print("This script will create a system administrator account.")
    print("This account will have full access to the admin console.\n")
    
    # Get username
    while True:
        username = input("Enter admin username: ").strip()
        is_valid, error = validate_username(username)
        if is_valid:
            break
        print(f"❌ {error}")
    
    # Get email
    while True:
        email = input("Enter admin email: ").strip()
        is_valid, error = validate_email(email)
        if is_valid:
            break
        print(f"❌ {error}")
    
    # Get password
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
    
    # Confirm password
    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("❌ Passwords do not match!")
        return
    
    # Confirm creation
    print(f"\n📋 Admin Account Details:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")
    
    confirm = input("\nCreate this admin account? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Admin account creation cancelled.")
        return
    
    # Create the admin user
    try:
        async with AsyncSessionLocal() as session:
            # Check if username already exists
            existing_user = await session.execute(
                select(User).where(User.username == username)
            )
            if existing_user.scalar_one_or_none():
                print(f"❌ Username '{username}' already exists!")
                return
            
            # Check if email already exists
            existing_email = await session.execute(
                select(User).where(User.email == email)
            )
            if existing_email.scalar_one_or_none():
                print(f"❌ Email '{email}' already exists!")
                return
            
            # Get or create system tenant for system admins
            result = await session.execute(select(Tenant).where(Tenant.name == "system"))
            system_tenant = result.scalar_one_or_none()
            if not system_tenant:
                system_tenant = Tenant(name="system", plan="enterprise")
                session.add(system_tenant)
                await session.commit()
                await session.refresh(system_tenant)
            
            # Create system admin user (use "system" tenant for system admins)
            admin_user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                is_admin=True,
                tenant_id=system_tenant.id,  # System admin uses "system" tenant
                is_active=True
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("✅ System admin account created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Account Type: System Administrator")
            print(f"   Status: Active")
            print("\n🔐 You can now log in to the admin console at:")
            print("   https://admin.smartsecurity.solutions")
            print("\n⚠️  Please keep your credentials secure!")
            
    except Exception as e:
        print(f"❌ Error creating admin account: {e}")
        return


async def list_existing_admins() -> None:
    """List existing admin users."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.is_admin == True)
            )
            admin_users = result.scalars().all()
            
            if not admin_users:
                print("No admin users found.")
                return
            
            print(f"\n📋 Existing Admin Users ({len(admin_users)}):")
            print("-" * 60)
            for user in admin_users:
                admin_type = "System Admin" if user.tenant_id is None else "Tenant Admin"
                status = "Active" if user.is_active else "Inactive"
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Type: {admin_type}")
                print(f"  Status: {status}")
                print(f"  Created: {user.created_at}")
                print("-" * 60)
                
    except Exception as e:
        print(f"❌ Error listing admin users: {e}")


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            await list_existing_admins()
            return
        elif sys.argv[1] == "--help":
            print("SmartSecurity Cloud - Admin User Management")
            print("=" * 40)
            print("Usage:")
            print("  python create_admin_user.py          # Create new admin user")
            print("  python create_admin_user.py --list   # List existing admins")
            print("  python create_admin_user.py --help   # Show this help")
            return
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use --help for usage information.")
            return
    
    await create_system_admin()


if __name__ == "__main__":
    asyncio.run(main()) 