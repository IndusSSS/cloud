#!/usr/bin/env python3
"""
Security Features Test Runner - MESSS Framework

This script runs comprehensive tests for all security features implemented in Phase 1.
It tests password security, rate limiting, session management, and authentication.

Usage:
    python3 test_security_runner.py
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def run_test_command(command, test_name):
    """Run a test command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {test_name} - PASSED")
            print(f"Output:\n{result.stdout}")
            return True
        else:
            print(f"❌ {test_name} - FAILED")
            print(f"Error:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {test_name} - ERROR: {str(e)}")
        return False

def test_password_security():
    """Test password security features."""
    print("\n🔐 Testing Password Security Features")
    
    # Test password hashing
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.utils.security import hash_password, verify_password, validate_password_strength, generate_secure_password

# Test password hashing
password = "SecurePassword123!"
hashed = hash_password(password)
print(f"✅ Password hashing: {len(hashed)} characters")

# Test password verification
assert verify_password(password, hashed) == True
assert verify_password("WrongPassword", hashed) == False
print("✅ Password verification: PASSED")

# Test password strength validation
result = validate_password_strength(password)
assert result["valid"] == True
assert result["score"] >= 3
print(f"✅ Password strength validation: {result['strength']}")

# Test secure password generation
generated = generate_secure_password(16)
assert len(generated) == 16
result = validate_password_strength(generated)
assert result["valid"] == True
print("✅ Secure password generation: PASSED")

print("🎉 All password security tests passed!")
"""
    
    with open("temp_password_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_password_test.py", "Password Security")
    
    # Cleanup
    if os.path.exists("temp_password_test.py"):
        os.remove("temp_password_test.py")
    
    return success

def test_token_security():
    """Test JWT token security features."""
    print("\n🎫 Testing Token Security Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.utils.security import create_access_token, create_refresh_token, verify_token
from datetime import timedelta

# Test access token creation and verification
user_data = {"sub": "user123", "username": "testuser"}
token = create_access_token(user_data)

payload = verify_token(token)
assert payload is not None
assert payload["sub"] == "user123"
assert payload["username"] == "testuser"
assert payload["iss"] == "SmartSecurity Cloud"
assert payload["aud"] == "SmartSecurity Users"
assert payload["type"] == "access"
print("✅ Access token creation and verification: PASSED")

# Test refresh token creation and verification
refresh_token = create_refresh_token(user_data)
payload = verify_token(refresh_token)
assert payload is not None
assert payload["type"] == "refresh"
print("✅ Refresh token creation and verification: PASSED")

# Test token expiration
expired_token = create_access_token(user_data, expires_delta=timedelta(seconds=1))
import time
time.sleep(2)
payload = verify_token(expired_token)
assert payload is None
print("✅ Token expiration: PASSED")

# Test invalid token handling
payload = verify_token("invalid.token.here")
assert payload is None
print("✅ Invalid token handling: PASSED")

print("🎉 All token security tests passed!")
"""
    
    with open("temp_token_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_token_test.py", "Token Security")
    
    # Cleanup
    if os.path.exists("temp_token_test.py"):
        os.remove("temp_token_test.py")
    
    return success

def test_device_fingerprinting():
    """Test device fingerprinting features."""
    print("\n📱 Testing Device Fingerprinting Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.utils.security import generate_device_fingerprint

# Test device fingerprint generation
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
ip_address = "192.168.1.100"

fingerprint = generate_device_fingerprint(user_agent, ip_address)
assert len(fingerprint) == 32
assert fingerprint.isalnum()
print("✅ Device fingerprint generation: PASSED")

# Test fingerprint consistency
fingerprint2 = generate_device_fingerprint(user_agent, ip_address)
assert fingerprint == fingerprint2
print("✅ Device fingerprint consistency: PASSED")

# Test fingerprint uniqueness
fingerprint3 = generate_device_fingerprint(user_agent, "192.168.1.101")
assert fingerprint != fingerprint3
print("✅ Device fingerprint uniqueness: PASSED")

print("🎉 All device fingerprinting tests passed!")
"""
    
    with open("temp_device_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_device_test.py", "Device Fingerprinting")
    
    # Cleanup
    if os.path.exists("temp_device_test.py"):
        os.remove("temp_device_test.py")
    
    return success

def test_input_sanitization():
    """Test input sanitization features."""
    print("\n🧹 Testing Input Sanitization Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.utils.security import sanitize_input, validate_email

# Test input sanitization
dangerous_inputs = [
    "<script>alert('xss')</script>",
    "javascript:alert('xss')",
    "onload=alert('xss')",
    "vbscript:alert('xss')",
]

for dangerous_input in dangerous_inputs:
    sanitized = sanitize_input(dangerous_input)
    assert "<script>" not in sanitized
    assert "javascript:" not in sanitized
    assert "onload=" not in sanitized
    assert "vbscript:" not in sanitized
print("✅ Input sanitization: PASSED")

# Test email validation
valid_emails = [
    "user@example.com",
    "user.name@example.com",
    "user+tag@example.com",
]

invalid_emails = [
    "invalid-email",
    "@example.com",
    "user@",
]

for email in valid_emails:
    assert validate_email(email) == True

for email in invalid_emails:
    assert validate_email(email) == False
print("✅ Email validation: PASSED")

print("🎉 All input sanitization tests passed!")
"""
    
    with open("temp_sanitization_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_sanitization_test.py", "Input Sanitization")
    
    # Cleanup
    if os.path.exists("temp_sanitization_test.py"):
        os.remove("temp_sanitization_test.py")
    
    return success

def test_user_model():
    """Test enhanced user model features."""
    print("\n👤 Testing User Model Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.models.user import User
from datetime import datetime, timedelta

# Test user creation
user = User(
    username="testuser",
    email="test@example.com",
    hashed_password="hashed_password",
    tenant_id="tenant123"
)

assert user.username == "testuser"
assert user.failed_login_attempts == 0
assert user.is_active == True
assert user.max_concurrent_sessions == 5
print("✅ User creation: PASSED")

# Test account lockout
assert user.is_locked() == False
user.increment_failed_login_attempts()
assert user.failed_login_attempts == 1
assert user.is_locked() == True
user.reset_failed_login_attempts()
assert user.failed_login_attempts == 0
assert user.is_locked() == False
print("✅ Account lockout: PASSED")

# Test password expiration
user.password_changed_at = datetime.utcnow() - timedelta(days=100)
assert user.is_password_expired() == True
user.password_changed_at = datetime.utcnow()
assert user.is_password_expired() == False
print("✅ Password expiration: PASSED")

# Test password history
assert len(user.get_password_history()) == 0
user.add_password_to_history("old_hash1")
user.add_password_to_history("old_hash2")
history = user.get_password_history()
assert len(history) == 2
assert user.is_password_in_history("old_hash1") == True
print("✅ Password history: PASSED")

# Test device management
assert len(user.get_trusted_devices()) == 0
device_info = {
    "fingerprint": "device123",
    "name": "Test Device",
    "type": "desktop",
    "ip_address": "192.168.1.100"
}
user.add_trusted_device(device_info)
devices = user.get_trusted_devices()
assert len(devices) == 1
assert user.remove_trusted_device("device123") == True
assert len(user.get_trusted_devices()) == 0
print("✅ Device management: PASSED")

# Test login status
status = user.can_login()
assert status["can_login"] == True
assert status["requires_mfa"] == False
print("✅ Login status check: PASSED")

print("🎉 All user model tests passed!")
"""
    
    with open("temp_user_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_user_test.py", "User Model")
    
    # Cleanup
    if os.path.exists("temp_user_test.py"):
        os.remove("temp_user_test.py")
    
    return success

def test_session_management():
    """Test session management features."""
    print("\n🔄 Testing Session Management Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.models.user import UserSession
from datetime import datetime, timedelta

# Test session creation
session = UserSession(
    user_id="user123",
    session_token="token123",
    refresh_token="refresh123",
    device_fingerprint="device123",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0",
    expires_at=datetime.utcnow() + timedelta(hours=1)
)

assert session.user_id == "user123"
assert session.session_token == "token123"
assert session.is_active == True
print("✅ Session creation: PASSED")

# Test session expiration
expired_session = UserSession(
    user_id="user123",
    session_token="expired_token",
    refresh_token="expired_refresh",
    device_fingerprint="device123",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0",
    expires_at=datetime.utcnow() - timedelta(hours=1)
)

assert expired_session.is_expired() == True
session.expires_at = datetime.utcnow() + timedelta(hours=1)
assert session.is_expired() == False
print("✅ Session expiration: PASSED")

# Test session activity update
original_activity = session.last_activity
session.update_activity()
assert session.last_activity > original_activity
print("✅ Session activity update: PASSED")

print("🎉 All session management tests passed!")
"""
    
    with open("temp_session_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_session_test.py", "Session Management")
    
    # Cleanup
    if os.path.exists("temp_session_test.py"):
        os.remove("temp_session_test.py")
    
    return success

def test_security_auditor():
    """Test security audit logging features."""
    print("\n📊 Testing Security Audit Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.models.user import SecurityEvent
import json

# Test security event creation
event = SecurityEvent(
    user_id="user123",
    event_type="login_success",
    severity="low",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0",
    success=True
)

assert event.user_id == "user123"
assert event.event_type == "login_success"
assert event.severity == "low"
assert event.success == True
print("✅ Security event creation: PASSED")

# Test event details management
details = {"username": "testuser", "device": "desktop"}
event.set_details(details)
retrieved_details = event.get_details()
assert retrieved_details["username"] == "testuser"
assert retrieved_details["device"] == "desktop"
print("✅ Event details management: PASSED")

# Test risk factors management
risk_factors = ["unusual_location", "new_device"]
event.set_risk_factors(risk_factors)
retrieved_factors = event.get_risk_factors()
assert "unusual_location" in retrieved_factors
assert "new_device" in retrieved_factors
print("✅ Risk factors management: PASSED")

print("🎉 All security audit tests passed!")
"""
    
    with open("temp_audit_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_audit_test.py", "Security Audit")
    
    # Cleanup
    if os.path.exists("temp_audit_test.py"):
        os.remove("temp_audit_test.py")
    
    return success

def test_rate_limiting():
    """Test rate limiting features."""
    print("\n⏱️ Testing Rate Limiting Features")
    
    test_code = """
import sys
sys.path.insert(0, 'app')

from app.utils.security import RateLimiter
from unittest.mock import Mock

# Test rate limiter initialization
mock_redis = Mock()
rate_limiter = RateLimiter(mock_redis)
assert rate_limiter.redis == mock_redis
print("✅ Rate limiter initialization: PASSED")

# Test rate limit check
mock_redis.pipeline.return_value.execute.return_value = [0, 0, 2, True]  # 2 attempts
result = rate_limiter.check_rate_limit("test:key", 5, 900)
assert result["allowed"] == True
assert result["remaining"] == 3
assert result["attempts"] == 2
print("✅ Rate limit check: PASSED")

# Test rate limit exceeded
mock_redis.pipeline.return_value.execute.return_value = [0, 0, 5, True]  # 5 attempts
result = rate_limiter.check_rate_limit("test:key", 5, 900)
assert result["allowed"] == False
assert result["remaining"] == 0
assert result["attempts"] == 5
print("✅ Rate limit exceeded: PASSED")

# Test increment failed attempt
rate_limiter.increment_failed_attempt("test:key", 900)
mock_redis.zadd.assert_called_once()
mock_redis.expire.assert_called_once_with("test:key", 900)
print("✅ Increment failed attempt: PASSED")

print("🎉 All rate limiting tests passed!")
"""
    
    with open("temp_rate_limit_test.py", "w") as f:
        f.write(test_code)
    
    success = run_test_command("python3 temp_rate_limit_test.py", "Rate Limiting")
    
    # Cleanup
    if os.path.exists("temp_rate_limit_test.py"):
        os.remove("temp_rate_limit_test.py")
    
    return success

def main():
    """Main test runner function."""
    print("🚀 MESSS Framework Security Features Test Runner")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test results tracking
    test_results = []
    
    # Run all security tests
    tests = [
        ("Password Security", test_password_security),
        ("Token Security", test_token_security),
        ("Device Fingerprinting", test_device_fingerprinting),
        ("Input Sanitization", test_input_sanitization),
        ("User Model", test_user_model),
        ("Session Management", test_session_management),
        ("Security Audit", test_security_auditor),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            test_results.append((test_name, success))
        except Exception as e:
            print(f"💥 {test_name} - ERROR: {str(e)}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL SECURITY FEATURES ARE WORKING CORRECTLY!")
        print("✅ MESSS Framework Phase 1 implementation is ready for production!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 