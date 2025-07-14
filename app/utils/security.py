# app/utils/security.py
"""
Security utilities for authentication and authorization.

• Password hashing with Argon2.
• JWT token creation and validation.
• API token generation and validation.
• Password verification functions.
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
import jwt

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


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
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + expires_delta
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
        "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "token_type": "Bearer",
        "usage": "Include this token in the Authorization header: Authorization: Bearer <api_token>"
    }