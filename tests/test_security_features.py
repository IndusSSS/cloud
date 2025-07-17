# tests/test_security_features.py
"""
Comprehensive tests for MESSS framework security features - Phase 1.

• Password security and validation
• Rate limiting and brute force protection
• Session management and device tracking
• Security audit logging
• Authentication service functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

from app.utils.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    generate_secure_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_device_fingerprint,
    check_password_breach,
    sanitize_input,
    validate_email,
    RateLimiter,
    SecurityAuditor
)
from app.services.auth import AuthenticationService
from app.models.user import User, UserSession, SecurityEvent


class TestPasswordSecurity:
    """Test password security features."""
    
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification with Argon2."""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        # Verify hash is different from original
        assert hashed != password
        assert len(hashed) > 50  # Argon2 hashes are long
        
        # Verify password
        assert verify_password(password, hashed) == True
        assert verify_password("WrongPassword", hashed) == False
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Test weak passwords
        weak_passwords = [
            "123456",  # Too short, no complexity
            "password",  # Common password
            "abc123",  # No special characters
            "Password",  # No numbers
            "PASSWORD123",  # No lowercase
            "pass123",  # Too short
        ]
        
        for password in weak_passwords:
            result = validate_password_strength(password)
            assert result["valid"] == False
            assert len(result["issues"]) > 0
        
        # Test strong passwords
        strong_passwords = [
            "SecurePass123!",
            "MyComplexP@ssw0rd",
            "Str0ng#P@ssw0rd!",
            "V3ryS3cur3P@ss!",
        ]
        
        for password in strong_passwords:
            result = validate_password_strength(password)
            assert result["valid"] == True
            assert result["score"] >= 3
            assert result["strength"] in ["strong", "very_strong"]
    
    def test_password_pattern_detection(self):
        """Test password pattern detection."""
        # Test sequential characters
        result = validate_password_strength("abc123!@#")
        assert "sequential" in " ".join(result["issues"]).lower()
        
        # Test repeated characters
        result = validate_password_strength("aaa123!@#")
        assert "repeated" in " ".join(result["issues"]).lower()
        
        # Test keyboard patterns
        result = validate_password_strength("qwerty123!@#")
        assert "keyboard" in " ".join(result["issues"]).lower()
    
    def test_secure_password_generation(self):
        """Test secure password generation."""
        password = generate_secure_password(16)
        
        # Check length
        assert len(password) == 16
        
        # Check complexity
        result = validate_password_strength(password)
        assert result["valid"] == True
        assert result["score"] >= 3
        
        # Check character types
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    def test_password_breach_detection(self):
        """Test password breach detection."""
        # Test common passwords (should be detected)
        common_passwords = ["password", "123456", "admin", "qwerty"]
        for password in common_passwords:
            assert check_password_breach(password) == True
        
        # Test secure passwords (should not be detected)
        secure_passwords = ["SecurePass123!", "MyComplexP@ssw0rd"]
        for password in secure_passwords:
            assert check_password_breach(password) == False


class TestTokenSecurity:
    """Test JWT token security features."""
    
    def test_access_token_creation_and_verification(self):
        """Test access token creation and verification."""
        user_data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(user_data)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["iss"] == "SmartSecurity Cloud"
        assert payload["aud"] == "SmartSecurity Users"
        assert payload["type"] == "access"
    
    def test_refresh_token_creation_and_verification(self):
        """Test refresh token creation and verification."""
        user_data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(user_data)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
    
    def test_token_expiration(self):
        """Test token expiration."""
        user_data = {"sub": "user123"}
        token = create_access_token(user_data, expires_delta=timedelta(seconds=1))
        
        # Token should be valid immediately
        payload = verify_token(token)
        assert payload is not None
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Token should be expired
        payload = verify_token(token)
        assert payload is None
    
    def test_invalid_token_handling(self):
        """Test invalid token handling."""
        # Test with invalid token
        payload = verify_token("invalid.token.here")
        assert payload is None
        
        # Test with empty token
        payload = verify_token("")
        assert payload is None


class TestDeviceFingerprinting:
    """Test device fingerprinting features."""
    
    def test_device_fingerprint_generation(self):
        """Test device fingerprint generation."""
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ip_address = "192.168.1.100"
        
        fingerprint = generate_device_fingerprint(user_agent, ip_address)
        
        # Check fingerprint properties
        assert len(fingerprint) == 32
        assert fingerprint.isalnum()
        
        # Same inputs should produce same fingerprint
        fingerprint2 = generate_device_fingerprint(user_agent, ip_address)
        assert fingerprint == fingerprint2
        
        # Different inputs should produce different fingerprints
        fingerprint3 = generate_device_fingerprint(user_agent, "192.168.1.101")
        assert fingerprint != fingerprint3


class TestInputSanitization:
    """Test input sanitization features."""
    
    def test_input_sanitization(self):
        """Test input sanitization for XSS prevention."""
        # Test dangerous inputs
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onload=alert('xss')",
            "vbscript:alert('xss')",
            "&lt;script&gt;alert('xss')&lt;/script&gt;",
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = sanitize_input(dangerous_input)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onload=" not in sanitized
            assert "vbscript:" not in sanitized
        
        # Test safe inputs
        safe_inputs = [
            "Hello World",
            "user@example.com",
            "MySecurePassword123!",
            "Normal text with spaces",
        ]
        
        for safe_input in safe_inputs:
            sanitized = sanitize_input(safe_input)
            assert sanitized == safe_input.strip()
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid emails
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
        ]
        
        for email in valid_emails:
            assert validate_email(email) == True
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "user@example..com",
        ]
        
        for email in invalid_emails:
            assert validate_email(email) == False


class TestRateLimiting:
    """Test rate limiting features."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        mock_redis = Mock()
        rate_limiter = RateLimiter(mock_redis)
        assert rate_limiter.redis == mock_redis
    
    def test_rate_limit_check(self):
        """Test rate limit checking."""
        mock_redis = Mock()
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 2, True]  # 2 attempts
        
        rate_limiter = RateLimiter(mock_redis)
        result = rate_limiter.check_rate_limit("test:key", 5, 900)
        
        assert result["allowed"] == True
        assert result["remaining"] == 3
        assert result["attempts"] == 2
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded scenario."""
        mock_redis = Mock()
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 5, True]  # 5 attempts
        
        rate_limiter = RateLimiter(mock_redis)
        result = rate_limiter.check_rate_limit("test:key", 5, 900)
        
        assert result["allowed"] == False
        assert result["remaining"] == 0
        assert result["attempts"] == 5
    
    def test_increment_failed_attempt(self):
        """Test incrementing failed attempts."""
        mock_redis = Mock()
        rate_limiter = RateLimiter(mock_redis)
        
        rate_limiter.increment_failed_attempt("test:key", 900)
        
        # Verify Redis calls
        mock_redis.zadd.assert_called_once()
        mock_redis.expire.assert_called_once_with("test:key", 900)


class TestSecurityAuditor:
    """Test security audit logging features."""
    
    def test_security_auditor_initialization(self):
        """Test security auditor initialization."""
        mock_redis = Mock()
        auditor = SecurityAuditor(mock_redis)
        assert auditor.redis == mock_redis
    
    def test_log_security_event(self):
        """Test security event logging."""
        mock_redis = Mock()
        auditor = SecurityAuditor(mock_redis)
        
        event_type = "login_success"
        user_id = "user123"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        auditor.log_security_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            details={"test": "data"},
            severity="medium"
        )
        
        # Verify Redis calls
        mock_redis.setex.assert_called_once()
        mock_redis.lpush.assert_called_once()
        mock_redis.ltrim.assert_called_once_with("security_events", 0, 9999)
    
    def test_get_recent_events(self):
        """Test getting recent security events."""
        mock_redis = Mock()
        
        # Mock event data
        event_data = {
            "id": "event123",
            "event_type": "login_success",
            "timestamp": datetime.now().isoformat()
        }
        
        mock_redis.keys.return_value = ["security_event:event123"]
        mock_redis.get.return_value = json.dumps(event_data)
        
        auditor = SecurityAuditor(mock_redis)
        events = auditor.get_recent_events(hours=24)
        
        assert len(events) == 1
        assert events[0]["id"] == "event123"
        assert events[0]["event_type"] == "login_success"


class TestUserModel:
    """Test enhanced user model features."""
    
    def test_user_creation(self):
        """Test user creation with security features."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            tenant_id="tenant123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.failed_login_attempts == 0
        assert user.is_active == True
        assert user.max_concurrent_sessions == 5
        assert user.session_timeout_minutes == 30
    
    def test_user_lockout_functionality(self):
        """Test user account lockout functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            tenant_id="tenant123"
        )
        
        # Initially not locked
        assert user.is_locked() == False
        
        # Increment failed attempts
        user.increment_failed_login_attempts()
        assert user.failed_login_attempts == 1
        assert user.is_locked() == True
        
        # Reset failed attempts
        user.reset_failed_login_attempts()
        assert user.failed_login_attempts == 0
        assert user.is_locked() == False
    
    def test_password_expiration(self):
        """Test password expiration functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            tenant_id="tenant123",
            password_changed_at=datetime.utcnow() - timedelta(days=100)
        )
        
        # Password should be expired (default 90 days)
        assert user.is_password_expired() == True
        
        # Set recent password change
        user.password_changed_at = datetime.utcnow()
        assert user.is_password_expired() == False
    
    def test_password_history(self):
        """Test password history functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            tenant_id="tenant123"
        )
        
        # Initially empty history
        assert len(user.get_password_history()) == 0
        
        # Add password to history
        user.add_password_to_history("old_hash1")
        user.add_password_to_history("old_hash2")
        
        history = user.get_password_history()
        assert len(history) == 2
        assert "old_hash1" in history
        assert "old_hash2" in history
        
        # Check if password is in history
        assert user.is_password_in_history("old_hash1") == True
        assert user.is_password_in_history("new_hash") == False
    
    def test_device_management(self):
        """Test trusted device management."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            tenant_id="tenant123"
        )
        
        # Initially no trusted devices
        assert len(user.get_trusted_devices()) == 0
        
        # Add trusted device
        device_info = {
            "fingerprint": "device123",
            "name": "Test Device",
            "type": "desktop",
            "ip_address": "192.168.1.100"
        }
        
        user.add_trusted_device(device_info)
        devices = user.get_trusted_devices()
        
        assert len(devices) == 1
        assert devices[0]["fingerprint"] == "device123"
        assert devices[0]["name"] == "Test Device"
        
        # Remove trusted device
        assert user.remove_trusted_device("device123") == True
        assert len(user.get_trusted_devices()) == 0
    
    def test_login_status_check(self):
        """Test user login status checking."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            tenant_id="tenant123"
        )
        
        # Normal user should be able to login
        status = user.can_login()
        assert status["can_login"] == True
        assert status["requires_mfa"] == False
        
        # Locked user should not be able to login
        user.increment_failed_login_attempts()
        status = user.can_login()
        assert status["can_login"] == False
        assert "locked" in status["reason"]
        
        # Inactive user should not be able to login
        user.is_active = False
        user.reset_failed_login_attempts()
        status = user.can_login()
        assert status["can_login"] == False
        assert "deactivated" in status["reason"]


class TestUserSession:
    """Test user session model features."""
    
    def test_session_creation(self):
        """Test user session creation."""
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
        assert session.device_fingerprint == "device123"
        assert session.is_active == True
    
    def test_session_expiration(self):
        """Test session expiration checking."""
        # Create expired session
        session = UserSession(
            user_id="user123",
            session_token="token123",
            refresh_token="refresh123",
            device_fingerprint="device123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        assert session.is_expired() == True
        
        # Create valid session
        session.expires_at = datetime.utcnow() + timedelta(hours=1)
        assert session.is_expired() == False
    
    def test_session_activity_update(self):
        """Test session activity updating."""
        session = UserSession(
            user_id="user123",
            session_token="token123",
            refresh_token="refresh123",
            device_fingerprint="device123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        original_activity = session.last_activity
        session.update_activity()
        
        assert session.last_activity > original_activity


class TestSecurityEvent:
    """Test security event model features."""
    
    def test_security_event_creation(self):
        """Test security event creation."""
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
    
    def test_event_details_management(self):
        """Test security event details management."""
        event = SecurityEvent(
            user_id="user123",
            event_type="login_success",
            severity="low",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            success=True
        )
        
        # Set details
        details = {"username": "testuser", "device": "desktop"}
        event.set_details(details)
        
        # Get details
        retrieved_details = event.get_details()
        assert retrieved_details["username"] == "testuser"
        assert retrieved_details["device"] == "desktop"
    
    def test_risk_factors_management(self):
        """Test security event risk factors management."""
        event = SecurityEvent(
            user_id="user123",
            event_type="login_success",
            severity="low",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            success=True
        )
        
        # Set risk factors
        risk_factors = ["unusual_location", "new_device"]
        event.set_risk_factors(risk_factors)
        
        # Get risk factors
        retrieved_factors = event.get_risk_factors()
        assert "unusual_location" in retrieved_factors
        assert "new_device" in retrieved_factors


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 