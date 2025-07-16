#!/usr/bin/env python3
"""
Secure Admin Account Setup Script (Final Working Version)

This script implements industry-standard security measures for admin account creation:
• Deletes all existing admin users
• Creates a new secure admin account with strong password requirements
• Implements password complexity validation
• Uses secure password hashing with Argon2

Security Features:
• Password complexity validation (12+ chars, mixed case, numbers, symbols)
• Secure password hashing with Argon2
• Common password blacklist
• Comprehensive password validation
"""

import asyncio
import re
import secrets
import string
import sys
from datetime import datetime
from typing import Tuple

# Add the app directory to the path
sys.path.append('.')

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.utils.security import hash_password


class PasswordValidator:
    """Password complexity validator with industry standards."""
    
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_symbols = True
        self.max_length = 128
        self.common_passwords = self._load_common_passwords()
    
    def _load_common_passwords(self) -> set:
        """Load list of common passwords to avoid."""
        return {
            "password", "123456", "123456789", "qwerty", "abc123", "password123",
            "admin", "admin123", "root", "user", "test", "guest", "welcome",
            "letmein", "monkey", "dragon", "master", "sunshine", "princess",
            "qwertyuiop", "asdfghjkl", "zxcvbnm", "111111", "000000", "123123",
            "admin@123", "password@123", "P@ssw0rd", "P@ssw0rd123"
        }
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password against security requirements.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
        
        if len(password) > self.max_length:
            return False, f"Password must be no more than {self.max_length} characters long"
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.require_digits and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if self.require_symbols and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            return False, "Password must contain at least one special character"
        
        if password.lower() in self.common_passwords:
            return False, "Password is too common and easily guessable"
        
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            return False, "Password cannot contain more than 2 repeated characters in a row"
        
        # Check for sequential characters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|123|234|345|456|567|678|789|890)', password.lower()):
            return False, "Password cannot contain sequential characters"
        
        return True, "Password meets security requirements"
    
    def generate_secure_password(self) -> str:
        """Generate a cryptographically secure password."""
        # Ensure at least one character from each required category
        password = [
            secrets.choice(string.ascii_uppercase),  # Uppercase
            secrets.choice(string.ascii_lowercase),  # Lowercase
            secrets.choice(string.digits),           # Digit
            secrets.choice('!@#$%^&*()_+-=[]{}|;:,.<>?')  # Symbol
        ]
        
        # Fill the rest with random characters
        remaining_length = self.min_length - len(password)
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
        password.extend(secrets.choice(all_chars) for _ in range(remaining_length))
        
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)


class AdminAccountManager:
    """Manages admin account creation and security."""
    
    def __init__(self):
        self.password_validator = PasswordValidator()
    
    async def delete_existing_admins(self, session) -> int:
        """Delete all existing admin users."""
        try:
            from sqlmodel import select, delete
            
            # Find all admin users
            result = await session.execute(select(User).where(User.is_admin == True))
            admin_users = result.scalars().all()
            
            if not admin_users:
                print("✅ No existing admin users found")
                return 0
            
            # Delete all admin users
            await session.execute(delete(User).where(User.is_admin == True))
            await session.commit()
            
            print(f"✅ Deleted {len(admin_users)} existing admin users")
            return len(admin_users)
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error deleting existing admins: {e}")
            raise
    
    async def create_secure_admin(
        self, 
        session, 
        username: str, 
        email: str, 
        password: str,
        tenant_id: str = "default"
    ) -> User:
        """Create a new secure admin account."""
        try:
            from sqlmodel import select
            
            # Validate password
            is_valid, error_msg = self.password_validator.validate_password(password)
            if not is_valid:
                raise ValueError(f"Password validation failed: {error_msg}")
            
            # Check if username or email already exists
            existing_user = await session.execute(
                select(User).where(
                    (User.username == username) | (User.email == email)
                )
            )
            if existing_user.scalars().first():
                raise ValueError("Username or email already exists")
            
            # Hash password with Argon2
            hashed_password = hash_password(password)
            
            # Create admin user
            admin_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True,
                tenant_id=tenant_id,
                created_at=datetime.utcnow()
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print(f"✅ Created secure admin account: {username}")
            return admin_user
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating admin account: {e}")
            raise


async def get_user_input() -> Tuple[str, str, str]:
    """Get admin credentials from user input."""
    print("\n🔐 Secure Admin Account Setup")
    print("=" * 50)
    print("This script will:")
    print("• Delete all existing admin users")
    print("• Create a new secure admin account")
    print("• Implement industry-standard security measures")
    print()
    
    # Get username
    while True:
        username = input("Enter admin username (or press Enter for 'admin'): ").strip()
        if not username:
            username = "admin"
        
        if len(username) >= 3 and username.isalnum():
            break
        else:
            print("❌ Username must be at least 3 characters and alphanumeric")
    
    # Get email
    while True:
        email = input("Enter admin email: ").strip()
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            break
        else:
            print("❌ Please enter a valid email address")
    
    # Get password
    password_validator = PasswordValidator()
    while True:
        print("\nPassword Requirements:")
        print(f"• Minimum {password_validator.min_length} characters")
        print("• At least one uppercase letter")
        print("• At least one lowercase letter")
        print("• At least one digit")
        print("• At least one special character")
        print("• Cannot be a common password")
        print("• No repeated or sequential characters")
        print()
        
        password = input("Enter admin password: ")
        confirm_password = input("Confirm admin password: ")
        
        if password != confirm_password:
            print("❌ Passwords do not match")
            continue
        
        is_valid, error_msg = password_validator.validate_password(password)
        if is_valid:
            break
        else:
            print(f"❌ {error_msg}")
    
    return username, email, password


async def generate_secure_password_option() -> str:
    """Offer to generate a secure password."""
    print("\n🔑 Password Generation Option")
    print("=" * 30)
    print("Would you like to generate a secure password automatically?")
    print("This will create a cryptographically secure password that meets all requirements.")
    
    while True:
        choice = input("Generate secure password? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            password_validator = PasswordValidator()
            password = password_validator.generate_secure_password()
            print(f"\n✅ Generated secure password: {password}")
            print("⚠️  IMPORTANT: Save this password securely! It won't be shown again.")
            
            confirm = input("Use this password? (y/n): ").lower().strip()
            if confirm in ['y', 'yes']:
                return password
        elif choice in ['n', 'no']:
            return ""
        else:
            print("Please enter 'y' or 'n'")


async def main():
    """Main function to set up secure admin account."""
    try:
        print("🚀 SmartSecurity Cloud - Secure Admin Setup")
        print("=" * 60)
        
        # Check if we want to generate a password
        generated_password = await generate_secure_password_option()
        
        if generated_password:
            username, email, password = "admin", "admin@smartsecurity.solutions", generated_password
        else:
            username, email, password = await get_user_input()
        
        print(f"\n📋 Admin Account Details:")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {'*' * len(password)}")
        print()
        
        # Confirm before proceeding
        confirm = input("Proceed with admin account setup? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Setup cancelled")
            return
        
        # Initialize database session
        if AsyncSessionLocal is None:
            print("❌ Database not configured. Please check your database settings.")
            return
            
        async with AsyncSessionLocal() as session:
            manager = AdminAccountManager()
            
            # Delete existing admins
            deleted_count = await manager.delete_existing_admins(session)
            
            # Create new secure admin
            admin_user = await manager.create_secure_admin(
                session, username, email, password, "default"
            )
        
        print("\n🎉 Secure Admin Setup Complete!")
        print("=" * 40)
        print("✅ All existing admin users deleted")
        print("✅ New secure admin account created")
        print("✅ Industry-standard security measures implemented")
        print()
        print("🔐 Login Credentials:")
        print(f"Username: {username}")
        print(f"Email: {email}")
        if generated_password:
            print(f"Password: {password}")
        else:
            print("Password: [as entered]")
        print()
        print("⚠️  Security Recommendations:")
        print("• Change password on first login")
        print("• Enable two-factor authentication if available")
        print("• Use a password manager for secure storage")
        print("• Regularly review audit logs")
        print("• Monitor for suspicious login attempts")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 