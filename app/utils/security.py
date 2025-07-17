# app/utils/security.py
"""
Essential security utilities for MESSS framework - Phase 1 Implementation.

• Password hashing with Argon2 (industry standard)
• JWT token creation and validation
• Rate limiting and brute force protection
• Basic audit logging
• Password validation and breach detection
• Session management
"""

import secrets
import string
import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
import jwt
import redis
import json

from app.core.config import settings

# Password hashing context - Argon2 is the most secure option
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Common passwords to prevent (top 100 most common)
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password123",
    "admin", "letmein", "welcome", "monkey", "dragon", "master", "hello",
    "freedom", "whatever", "qazwsx", "trustno1", "jordan", "harley",
    "ranger", "iwantu", "jennifer", "hunter", "buster", "soccer",
    "baseball", "tiger", "charlie", "andrew", "michelle", "love",
    "sunshine", "jessica", "asshole", "696969", "amanda", "access",
    "computer", "cookie", "mickey", "starwars", "shadow", "maggie",
    "654321", "george", "carol", "michael", "jessie", "diamond",
    "oliver", "mercedes", "benjamin", "secret", "maverick", "fishing",
    "hockey", "cookie", "charlie", "gateway", "bailey", "raiders",
    "porn", "badass", "blowme", "spider", "green", "purple", "frank",
    "hacker", "michelle", "legend", "rocket", "thomas", "sweeper",
    "merlin", "casper", "midnight", "skywalker", "shelby", "orange",
    "888888", "ncc1701", "charles", "brian", "mark", "startrek",
    "sierra", "leather", "232323", "4444", "beavis", "bigcock",
    "happy", "sophie", "ladies", "naughty", "giants", "booty"
}


def hash_password(password: str) -> str:
    """Hash a password using Argon2 (industry standard)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength and return detailed feedback.
    
    Returns:
        Dict with 'valid' (bool), 'score' (int 0-4), 'issues' (list), 'suggestions' (list)
    """
    issues = []
    suggestions = []
    score = 0
    
    # Check length
    if len(password) < 12:
        issues.append("Password must be at least 12 characters long")
    elif len(password) >= 16:
        score += 1
    else:
        score += 0.5
    
    # Check for common passwords
    if password.lower() in COMMON_PASSWORDS:
        issues.append("Password is too common")
        suggestions.append("Choose a more unique password")
    
    # Check character types
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
    
    if has_upper:
        score += 1
    else:
        issues.append("Include at least one uppercase letter")
        suggestions.append("Add uppercase letters (A-Z)")
    
    if has_lower:
        score += 1
    else:
        issues.append("Include at least one lowercase letter")
        suggestions.append("Add lowercase letters (a-z)")
    
    if has_digit:
        score += 1
    else:
        issues.append("Include at least one number")
        suggestions.append("Add numbers (0-9)")
    
    if has_special:
        score += 1
    else:
        issues.append("Include at least one special character")
        suggestions.append("Add special characters (!@#$%^&*)")
    
    # Check for patterns
    if re.search(r'(.)\1{2,}', password):
        issues.append("Avoid repeated characters")
        suggestions.append("Don't repeat the same character more than twice")
    
    if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
        issues.append("Avoid sequential characters")
        suggestions.append("Don't use sequential letters (abc, def, etc.)")
    
    if re.search(r'(123|234|345|456|567|678|789|012)', password):
        issues.append("Avoid sequential numbers")
        suggestions.append("Don't use sequential numbers (123, 456, etc.)")
    
    # Check for keyboard patterns
    keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', 'qazwsx', 'edcrfv', 'tgbyhn']
    if any(pattern in password.lower() for pattern in keyboard_patterns):
        issues.append("Avoid keyboard patterns")
        suggestions.append("Don't use keyboard patterns (qwerty, asdfgh, etc.)")
    
    # Determine if password is valid
    valid = len(issues) == 0 and score >= 3
    
    return {
        "valid": valid,
        "score": int(score),
        "issues": issues,
        "suggestions": suggestions,
        "strength": "weak" if score < 2 else "medium" if score < 3 else "strong" if score < 4 else "very_strong"
    }


def generate_secure_password(length: int = 16) -> str:
    """Generate a cryptographically secure password."""
    if length < 12:
        length = 12
    
    # Ensure at least one of each character type
    password_chars = []
    password_chars.append(secrets.choice(string.ascii_uppercase))  # At least one uppercase
    password_chars.append(secrets.choice(string.ascii_lowercase))  # At least one lowercase
    password_chars.append(secrets.choice(string.digits))           # At least one digit
    password_chars.append(secrets.choice('!@#$%^&*()_+-=[]{}|;:,.<>?'))  # At least one special
    
    # Fill the rest with random characters
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
    password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))
    
    # Shuffle the password to avoid predictable patterns
    password_list = list(password_chars)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with enhanced security."""
    to_encode = data.copy()
    
    # Add standard JWT claims
    now = datetime.now(timezone.utc)
    to_encode.update({
        "iat": now,  # Issued at
        "iss": "SmartSecurity Cloud",  # Issuer
        "aud": "SmartSecurity Users",  # Audience
        "type": "access"  # Token type
    })
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Use RS256 for better security (asymmetric)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    now = datetime.now(timezone.utc)
    to_encode.update({
        "iat": now,
        "iss": "SmartSecurity Cloud",
        "aud": "SmartSecurity Users",
        "type": "refresh"
    })
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)  # 7 days for refresh tokens
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_device_fingerprint(user_agent: str, ip_address: str) -> str:
    """Generate a device fingerprint for tracking."""
    # Create a hash of user agent and IP for device identification
    fingerprint_data = f"{user_agent}:{ip_address}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]


class RateLimiter:
    """Rate limiting implementation using Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def check_rate_limit(self, key: str, max_attempts: int, window_seconds: int) -> Dict[str, Any]:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Rate limit key (e.g., "login:192.168.1.1")
            max_attempts: Maximum attempts allowed
            window_seconds: Time window in seconds
            
        Returns:
            Dict with 'allowed' (bool), 'remaining' (int), 'reset_time' (int)
        """
        current_time = int(datetime.now().timestamp())
        window_start = current_time - window_seconds
        
        # Use Redis sorted set for sliding window
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.zcard(key)
        pipe.expire(key, window_seconds)
        results = pipe.execute()
        
        attempts = results[2]
        remaining = max(0, max_attempts - attempts)
        reset_time = current_time + window_seconds
        
        return {
            "allowed": attempts < max_attempts,
            "remaining": remaining,
            "reset_time": reset_time,
            "attempts": attempts
        }
    
    def increment_failed_attempt(self, key: str, window_seconds: int):
        """Increment failed attempt counter."""
        current_time = int(datetime.now().timestamp())
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window_seconds)


class SecurityAuditor:
    """Basic security audit logging."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "medium"
    ):
        """Log a security event."""
        event = {
            "id": secrets.token_hex(16),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "severity": severity,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Redis for recent events (last 24 hours)
        event_key = f"security_event:{event['id']}"
        self.redis.setex(event_key, 86400, json.dumps(event))
        
        # Add to event list
        self.redis.lpush("security_events", json.dumps(event))
        self.redis.ltrim("security_events", 0, 9999)  # Keep last 10,000 events
        
        # Log to console for development
        if settings.DEBUG:
            print(f"SECURITY EVENT: {event_type} - {ip_address} - {'SUCCESS' if success else 'FAILURE'}")
    
    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent security events."""
        events = []
        event_keys = self.redis.keys("security_event:*")
        
        for key in event_keys:
            event_data = self.redis.get(key)
            if event_data:
                event = json.loads(event_data)
                event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                if (datetime.now(timezone.utc) - event_time).total_seconds() <= hours * 3600:
                    events.append(event)
        
        return sorted(events, key=lambda x: x['timestamp'], reverse=True)


def check_password_breach(password: str) -> bool:
    """
    Check if password has been compromised in known breaches.
    This is a simplified version - in production, use HaveIBeenPwned API.
    """
    # Hash the password for comparison
    password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    
    # This is a placeholder - in production, check against breach databases
    # For now, we'll just check against our common passwords list
    return password.lower() in COMMON_PASSWORDS


def sanitize_input(input_string: str) -> str:
    """Basic input sanitization to prevent XSS."""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'vbscript:', 'onload=']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_api_token(
    client_id: str,
    permissions: Optional[list] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a long-lived API token for external service authentication."""
    if permissions is None:
        permissions = ["read", "write"]
    
    if expires_delta is None:
        expires_delta = timedelta(days=settings.API_TOKEN_EXPIRE_DAYS)
    
    # Create token payload
    token_data = {
        "client_id": client_id,
        "permissions": permissions,
        "token_type": "api",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta
    }
    
    # Generate the API token
    api_token = jwt.encode(
        token_data, 
        settings.API_TOKEN_SECRET, 
        algorithm=settings.API_TOKEN_ALGORITHM
    )
    
    return api_token


def verify_api_token(token: str) -> Optional[dict]:
    """Verify and decode an API token."""
    try:
        payload = jwt.decode(
            token, 
            settings.API_TOKEN_SECRET, 
            algorithms=[settings.API_TOKEN_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None


def generate_secure_api_key(length: int = 64) -> str:
    """Generate a secure API key for external services."""
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_smartsecurity_api_token() -> dict:
    """Create a SmartSecurity Cloud API token for external service authentication."""
    # Generate a unique client ID
    client_id = f"smartsecurity-cloud-{secrets.token_hex(8)}"
    
    # Define permissions for the API token
    permissions = [
        "devices:read",
        "devices:write", 
        "sensors:read",
        "sensors:write",
        "data:ingest",
        "data:query",
        "alerts:read",
        "alerts:write"
    ]
    
    # Generate the API token
    api_token = generate_api_token(
        client_id=client_id,
        permissions=permissions,
        expires_delta=timedelta(days=365)  # 1 year expiration
    )
    
    return {
        "api_token": api_token,
        "client_id": client_id,
        "permissions": permissions,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
        "token_type": "Bearer",
        "usage": "Include this token in the Authorization header: Authorization: Bearer <api_token>"
    }