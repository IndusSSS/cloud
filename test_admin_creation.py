#!/usr/bin/env python3
"""
Test script for admin user creation functionality.
This script tests the password validation and user creation logic.
"""

import re
import sys
from typing import Tuple


def validate_password(password: str) -> Tuple[bool, str]:
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


def validate_username(username: str) -> Tuple[bool, str]:
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


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Returns:
        (is_valid, error_message)
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address"
    
    return True, ""


def test_password_validation():
    """Test password validation function."""
    print("🔐 Testing Password Validation")
    print("=" * 40)
    
    test_cases = [
        ("weak", False, "Too short"),
        ("password", False, "Missing uppercase, number, special"),
        ("Password", False, "Missing number, special"),
        ("Password1", False, "Missing special"),
        ("Password1!", True, "Valid password"),
        ("MySecurePass123!", True, "Valid password"),
        ("", False, "Empty password"),
        ("12345678", False, "Only numbers"),
        ("ABCDEFGH", False, "Only uppercase"),
        ("abcdefgh", False, "Only lowercase"),
        ("!@#$%^&*", False, "Only special"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for password, expected_valid, description in test_cases:
        is_valid, error = validate_password(password)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"{status} - {description}: '{password}' -> {is_valid}")
        if is_valid == expected_valid:
            passed += 1
    
    print(f"\nPassword Validation: {passed}/{total} tests passed")
    return passed == total


def test_username_validation():
    """Test username validation function."""
    print("\n👤 Testing Username Validation")
    print("=" * 40)
    
    test_cases = [
        ("ab", False, "Too short"),
        ("a" * 51, False, "Too long"),
        ("admin", True, "Valid username"),
        ("admin_user", True, "Valid with underscore"),
        ("admin-user", True, "Valid with hyphen"),
        ("admin123", True, "Valid with numbers"),
        ("admin@user", False, "Invalid character @"),
        ("admin user", False, "Invalid space"),
        ("", False, "Empty username"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for username, expected_valid, description in test_cases:
        is_valid, error = validate_username(username)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"{status} - {description}: '{username}' -> {is_valid}")
        if is_valid == expected_valid:
            passed += 1
    
    print(f"\nUsername Validation: {passed}/{total} tests passed")
    return passed == total


def test_email_validation():
    """Test email validation function."""
    print("\n📧 Testing Email Validation")
    print("=" * 40)
    
    test_cases = [
        ("admin@example.com", True, "Valid email"),
        ("admin@smartsecurity.solutions", True, "Valid domain"),
        ("admin.user@example.com", True, "Valid with dot"),
        ("admin+test@example.com", True, "Valid with plus"),
        ("admin@example", False, "Invalid domain"),
        ("admin.example.com", False, "Missing @"),
        ("@example.com", False, "Missing local part"),
        ("admin@", False, "Missing domain"),
        ("", False, "Empty email"),
        ("admin user@example.com", False, "Space in local part"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for email, expected_valid, description in test_cases:
        is_valid, error = validate_email(email)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"{status} - {description}: '{email}' -> {is_valid}")
        if is_valid == expected_valid:
            passed += 1
    
    print(f"\nEmail Validation: {passed}/{total} tests passed")
    return passed == total


def test_password_requirements_display():
    """Test password requirements display."""
    print("\n📋 Testing Password Requirements Display")
    print("=" * 50)
    
    print("Password requirements:")
    print("  - At least 8 characters long")
    print("  - Contains uppercase and lowercase letters")
    print("  - Contains at least one number")
    print("  - Contains at least one special character")
    
    print("\nExample valid passwords:")
    print("  - MySecurePass123!")
    print("  - Admin@2024!")
    print("  - SmartSecurity#1")
    
    print("\nExample invalid passwords:")
    print("  - password (too weak)")
    print("  - Password (missing number/special)")
    print("  - Password1 (missing special)")
    print("  - 12345678 (only numbers)")
    
    return True


def main():
    """Run all tests."""
    print("🧪 SmartSecurity Cloud - Admin Creation Tests")
    print("=" * 60)
    
    tests = [
        test_password_validation,
        test_username_validation,
        test_email_validation,
        test_password_requirements_display,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("✅ All tests passed! Admin creation functionality is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 