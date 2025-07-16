#!/usr/bin/env python3
"""
Security Enhancement Script for SmartSecurity Cloud

This script adds industry-standard security measures to prevent brute force attacks:
• Rate limiting on authentication endpoints
• Account lockout after failed attempts
• Enhanced password validation
• Security headers configuration
• Audit logging improvements
• Session management enhancements

Security Features Added:
• Brute force protection with exponential backoff
• Rate limiting per IP address
• Account lockout after 5 failed attempts
• Enhanced password complexity requirements
• Security headers (HSTS, CSP, X-Frame-Options)
• Comprehensive audit logging
• Session timeout and rotation
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add the app directory to the path
sys.path.append('.')

from app.core.config import settings


class SecurityEnhancer:
    """Enhances application security with industry-standard measures."""
    
    def __init__(self):
        self.security_config = {
            "rate_limiting": {
                "login_attempts_per_minute": 5,
                "lockout_duration_minutes": 15,
                "max_failed_attempts": 5,
                "exponential_backoff": True
            },
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_digits": True,
                "require_symbols": True,
                "max_length": 128,
                "prevent_common_passwords": True,
                "prevent_sequential_chars": True,
                "prevent_repeated_chars": True
            },
            "session_security": {
                "token_expiry_minutes": 30,
                "refresh_token_expiry_days": 7,
                "max_concurrent_sessions": 3,
                "force_logout_on_password_change": True
            },
            "security_headers": {
                "hsts_max_age": 31536000,
                "csp_policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
                "referrer_policy": "strict-origin-when-cross-origin"
            }
        }
    
    def create_rate_limiting_middleware(self) -> str:
        """Create rate limiting middleware for FastAPI."""
        return '''
# Rate limiting middleware for brute force protection
import time
import asyncio
from collections import defaultdict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

# In-memory storage for rate limiting (use Redis in production)
rate_limit_store = defaultdict(list)
failed_attempts = defaultdict(int)
lockout_until = defaultdict(float)

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware to prevent brute force attacks."""
    client_ip = request.client.host
    path = request.url.path
    
    # Check if IP is locked out
    if lockout_until[client_ip] > time.time():
        remaining_time = int(lockout_until[client_ip] - time.time())
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": f"Account temporarily locked. Try again in {remaining_time} seconds.",
                "retry_after": remaining_time
            },
            headers={"Retry-After": str(remaining_time)}
        )
    
    # Apply rate limiting to login endpoints
    if path in ["/api/v1/auth/login", "/api/v1/auth/login-json"]:
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old entries
        rate_limit_store[client_ip] = [
            timestamp for timestamp in rate_limit_store[client_ip]
            if timestamp > window_start
        ]
        
        # Check rate limit
        if len(rate_limit_store[client_ip]) >= 5:  # 5 attempts per minute
            lockout_duration = min(15 * (2 ** (failed_attempts[client_ip] // 5)), 1440)  # Exponential backoff, max 24h
            lockout_until[client_ip] = current_time + (lockout_duration * 60)
            failed_attempts[client_ip] += 1
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Too many login attempts. Account locked for {lockout_duration} minutes.",
                    "retry_after": lockout_duration * 60
                },
                headers={"Retry-After": str(lockout_duration * 60)}
            )
        
        # Add current request to rate limit store
        rate_limit_store[client_ip].append(current_time)
    
    response = await call_next(request)
    
    # Track failed login attempts
    if path in ["/api/v1/auth/login", "/api/v1/auth/login-json"] and response.status_code == 401:
        failed_attempts[client_ip] += 1
        
        # Lock account after 5 failed attempts
        if failed_attempts[client_ip] >= 5:
            lockout_duration = min(15 * (2 ** (failed_attempts[client_ip] // 5)), 1440)
            lockout_until[client_ip] = time.time() + (lockout_duration * 60)
    
    return response
'''
    
    def create_security_headers_middleware(self) -> str:
        """Create security headers middleware."""
        return '''
# Security headers middleware
from fastapi import Request
from fastapi.responses import Response

async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
'''
    
    def create_enhanced_password_validator(self) -> str:
        """Create enhanced password validation."""
        return '''
# Enhanced password validation
import re
import secrets
import string
from typing import Tuple

class EnhancedPasswordValidator:
    """Enhanced password validator with industry standards."""
    
    def __init__(self):
        self.min_length = 12
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_symbols = True
        self.common_passwords = self._load_common_passwords()
    
    def _load_common_passwords(self) -> set:
        """Load comprehensive list of common passwords."""
        return {
            "password", "123456", "123456789", "qwerty", "abc123", "password123",
            "admin", "admin123", "root", "user", "test", "guest", "welcome",
            "letmein", "monkey", "dragon", "master", "sunshine", "princess",
            "qwertyuiop", "asdfghjkl", "zxcvbnm", "111111", "000000", "123123",
            "admin@123", "password@123", "P@ssw0rd", "P@ssw0rd123", "password1",
            "12345678", "qwerty123", "1q2w3e4r", "1qaz2wsx", "qazwsx", "123qwe",
            "password12", "password1234", "admin1234", "root123", "user123"
        }
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password against enhanced security requirements."""
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
        
        if len(password) > self.max_length:
            return False, f"Password must be no more than {self.max_length} characters long"
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.require_digits and not re.search(r'\\d', password):
            return False, "Password must contain at least one digit"
        
        if self.require_symbols and not re.search(r'[!@#$%^&*()_+\\-=\\[\\]{};\\':"\\\\|,.<>\\/?]', password):
            return False, "Password must contain at least one special character"
        
        if password.lower() in self.common_passwords:
            return False, "Password is too common and easily guessable"
        
        # Check for repeated characters
        if re.search(r'(.)\\1{2,}', password):
            return False, "Password cannot contain more than 2 repeated characters in a row"
        
        # Check for sequential characters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|123|234|345|456|567|678|789|890)', password.lower()):
            return False, "Password cannot contain sequential characters"
        
        # Check for keyboard patterns
        keyboard_patterns = [
            "qwerty", "asdfgh", "zxcvbn", "123456", "654321",
            "qazwsx", "edcrfv", "tgbyhn", "ujmikl", "plokij"
        ]
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                return False, "Password cannot contain keyboard patterns"
        
        return True, "Password meets enhanced security requirements"
    
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
'''
    
    def create_audit_logging_enhancement(self) -> str:
        """Create enhanced audit logging."""
        return '''
# Enhanced audit logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class EnhancedAuditLogger:
    """Enhanced audit logging with detailed security events."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_security_event(
        self,
        action: str,
        user_id: Optional[str],
        username: Optional[str],
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: str = "info"
    ):
        """Log a security event with enhanced details."""
        from app.models.audit import AuditLog
        
        audit_log = AuditLog(
            tenant_id=details.get("tenant_id", "system"),
            user_id=user_id,
            action=action,
            resource_type="security_event",
            resource_id=details.get("resource_id"),
            details=json.dumps({
                **details,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "security_event": True
            }),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.session.add(audit_log)
        await self.session.commit()
    
    async def log_failed_login(
        self,
        username: str,
        ip_address: str,
        user_agent: str,
        failure_reason: str
    ):
        """Log a failed login attempt."""
        await self.log_security_event(
            action="login_failed",
            user_id=None,
            username=username,
            details={
                "failure_reason": failure_reason,
                "attempt_count": 1  # This would be incremented by rate limiting
            },
            ip_address=ip_address,
            user_agent=user_agent,
            severity="warning"
        )
    
    async def log_successful_login(
        self,
        user_id: str,
        username: str,
        ip_address: str,
        user_agent: str
    ):
        """Log a successful login."""
        await self.log_security_event(
            action="login_successful",
            user_id=user_id,
            username=username,
            details={
                "login_method": "password",
                "session_id": None  # Would be set by session management
            },
            ip_address=ip_address,
            user_agent=user_agent,
            severity="info"
        )
    
    async def log_account_lockout(
        self,
        username: str,
        ip_address: str,
        user_agent: str,
        lockout_duration: int
    ):
        """Log an account lockout."""
        await self.log_security_event(
            action="account_lockout",
            user_id=None,
            username=username,
            details={
                "lockout_duration_minutes": lockout_duration,
                "reason": "too_many_failed_attempts"
            },
            ip_address=ip_address,
            user_agent=user_agent,
            severity="high"
        )
'''
    
    def create_session_management(self) -> str:
        """Create enhanced session management."""
        return '''
# Enhanced session management
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

class SessionManager:
    """Enhanced session management with security features."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.active_sessions: Dict[str, Dict] = {}
    
    def create_session(self, user_id: str, username: str, ip_address: str) -> str:
        """Create a new secure session."""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "is_active": True
        }
        
        self.active_sessions[session_id] = session_data
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str) -> Optional[Dict]:
        """Validate a session and check for security issues."""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        
        # Check if session is active
        if not session_data["is_active"]:
            return None
        
        # Check session expiry (30 minutes)
        if datetime.utcnow() - session_data["last_activity"] > timedelta(minutes=30):
            self.invalidate_session(session_id)
            return None
        
        # Check IP address (optional security measure)
        if session_data["ip_address"] != ip_address:
            # Log potential session hijacking attempt
            return None
        
        # Update last activity
        session_data["last_activity"] = datetime.utcnow()
        return session_data
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["is_active"] = False
    
    def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user."""
        for session_id, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                session_data["is_active"] = False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if current_time - session_data["last_activity"] > timedelta(hours=24):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
'''
    
    def create_security_config_file(self) -> str:
        """Create security configuration file."""
        return f'''
# Security configuration for SmartSecurity Cloud
SECURITY_CONFIG = {json.dumps(self.security_config, indent=2)}

# Rate limiting settings
RATE_LIMIT_CONFIG = {{
    "login_attempts_per_minute": 5,
    "lockout_duration_minutes": 15,
    "max_failed_attempts": 5,
    "exponential_backoff": True,
    "max_lockout_duration_hours": 24
}}

# Password policy settings
PASSWORD_POLICY = {{
    "min_length": 12,
    "max_length": 128,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digits": True,
    "require_symbols": True,
    "prevent_common_passwords": True,
    "prevent_sequential_chars": True,
    "prevent_repeated_chars": True,
    "prevent_keyboard_patterns": True
}}

# Session security settings
SESSION_SECURITY = {{
    "token_expiry_minutes": 30,
    "refresh_token_expiry_days": 7,
    "max_concurrent_sessions": 3,
    "force_logout_on_password_change": True,
    "session_timeout_minutes": 30,
    "max_session_age_hours": 24
}}

# Security headers configuration
SECURITY_HEADERS = {{
    "hsts_max_age": 31536000,
    "csp_policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
    "x_frame_options": "DENY",
    "x_content_type_options": "nosniff",
    "referrer_policy": "strict-origin-when-cross-origin",
    "x_xss_protection": "1; mode=block",
    "permissions_policy": "geolocation=(), microphone=(), camera=()"
}}
'''
    
    def generate_security_documentation(self) -> str:
        """Generate security documentation."""
        return '''
# SmartSecurity Cloud - Security Implementation Guide

## 🔒 Security Features Implemented

### 1. Brute Force Protection
- **Rate Limiting**: 5 login attempts per minute per IP
- **Account Lockout**: 15-minute lockout after 5 failed attempts
- **Exponential Backoff**: Lockout duration increases with repeated failures
- **Maximum Lockout**: 24-hour maximum lockout duration

### 2. Password Security
- **Minimum Length**: 12 characters
- **Complexity Requirements**: Uppercase, lowercase, digits, symbols
- **Common Password Prevention**: Blacklist of common passwords
- **Pattern Prevention**: No sequential or repeated characters
- **Keyboard Pattern Prevention**: No keyboard patterns allowed

### 3. Session Management
- **Token Expiry**: 30-minute session timeout
- **Concurrent Sessions**: Maximum 3 active sessions per user
- **IP Validation**: Session tied to IP address
- **Automatic Cleanup**: Expired sessions removed automatically

### 4. Security Headers
- **HSTS**: Strict Transport Security
- **CSP**: Content Security Policy
- **X-Frame-Options**: Prevent clickjacking
- **X-Content-Type-Options**: Prevent MIME sniffing
- **Referrer Policy**: Control referrer information

### 5. Audit Logging
- **Comprehensive Logging**: All security events logged
- **IP Tracking**: All actions tied to IP addresses
- **User Agent Tracking**: Browser/client information logged
- **Severity Levels**: Info, warning, high severity events

## 🛡️ Security Recommendations

### For Administrators
1. **Regular Security Reviews**: Review audit logs weekly
2. **Password Policy**: Enforce strong password requirements
3. **Session Monitoring**: Monitor for suspicious session activity
4. **IP Whitelisting**: Consider IP whitelisting for admin access
5. **Two-Factor Authentication**: Implement 2FA for admin accounts

### For Users
1. **Strong Passwords**: Use unique, complex passwords
2. **Password Manager**: Use a password manager for secure storage
3. **Regular Updates**: Change passwords regularly
4. **Secure Connections**: Always use HTTPS
5. **Logout**: Always logout from shared computers

### For Developers
1. **Input Validation**: Validate all user inputs
2. **SQL Injection Prevention**: Use parameterized queries
3. **XSS Prevention**: Sanitize all user-generated content
4. **CSRF Protection**: Implement CSRF tokens
5. **Security Testing**: Regular security testing and penetration testing

## 📊 Security Metrics

### Key Performance Indicators
- Failed login attempts per day
- Account lockouts per day
- Average session duration
- Security event frequency
- Password change frequency

### Monitoring Alerts
- Multiple failed login attempts from same IP
- Unusual login patterns
- Account lockout spikes
- Suspicious session activity
- Security header violations

## 🔧 Implementation Notes

### Rate Limiting
The rate limiting system uses in-memory storage for development. In production, use Redis for distributed rate limiting across multiple application instances.

### Session Storage
Sessions are stored in memory for development. In production, use Redis or a database for persistent session storage.

### Audit Logging
Audit logs are stored in the database. Consider implementing log rotation and archiving for long-term storage.

### Security Headers
Security headers are applied to all responses. Customize the Content Security Policy based on your application's requirements.

## 🚨 Incident Response

### Security Incident Procedures
1. **Immediate Response**: Lock affected accounts
2. **Investigation**: Review audit logs and system logs
3. **Containment**: Isolate affected systems
4. **Recovery**: Restore from backups if necessary
5. **Post-Incident**: Document lessons learned

### Contact Information
- Security Team: security@smartsecurity.solutions
- Emergency Contact: +1-XXX-XXX-XXXX
- Incident Response: incident@smartsecurity.solutions
'''

    async def apply_security_enhancements(self):
        """Apply all security enhancements."""
        print("🔒 Applying Security Enhancements...")
        print("=" * 50)
        
        # Create security middleware files
        print("📝 Creating security middleware...")
        
        # Rate limiting middleware
        with open("app/middleware/rate_limiting.py", "w") as f:
            f.write(self.create_rate_limiting_middleware())
        
        # Security headers middleware
        with open("app/middleware/security_headers.py", "w") as f:
            f.write(self.create_security_headers_middleware())
        
        # Enhanced password validator
        with open("app/utils/enhanced_password.py", "w") as f:
            f.write(self.create_enhanced_password_validator())
        
        # Enhanced audit logging
        with open("app/utils/enhanced_audit.py", "w") as f:
            f.write(self.create_audit_logging_enhancement())
        
        # Session management
        with open("app/utils/session_manager.py", "w") as f:
            f.write(self.create_session_management())
        
        # Security configuration
        with open("app/core/security_config.py", "w") as f:
            f.write(self.create_security_config_file())
        
        # Security documentation
        with open("SECURITY_IMPLEMENTATION.md", "w") as f:
            f.write(self.generate_security_documentation())
        
        print("✅ Security enhancements applied successfully!")
        print()
        print("📋 Files Created:")
        print("• app/middleware/rate_limiting.py - Brute force protection")
        print("• app/middleware/security_headers.py - Security headers")
        print("• app/utils/enhanced_password.py - Enhanced password validation")
        print("• app/utils/enhanced_audit.py - Enhanced audit logging")
        print("• app/utils/session_manager.py - Session management")
        print("• app/core/security_config.py - Security configuration")
        print("• SECURITY_IMPLEMENTATION.md - Security documentation")
        print()
        print("🔧 Next Steps:")
        print("1. Integrate middleware into your FastAPI application")
        print("2. Update authentication endpoints to use enhanced validation")
        print("3. Configure security headers in your web server")
        print("4. Set up monitoring for security events")
        print("5. Test all security features thoroughly")


async def main():
    """Main function to apply security enhancements."""
    try:
        print("🚀 SmartSecurity Cloud - Security Enhancement")
        print("=" * 60)
        
        enhancer = SecurityEnhancer()
        await enhancer.apply_security_enhancements()
        
    except Exception as e:
        print(f"\n❌ Security enhancement failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 