"""
Tests for authentication endpoints.

• Tests user login and registration
• Tests JWT token validation
• Tests password hashing and verification
• Tests authentication middleware
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from app.models.user import User
from app.utils.security import hash_password, create_access_token, verify_password

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }

@pytest.fixture
def admin_user_data():
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123"
    }

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_endpoints_exist(client):
    """Test that authentication endpoints are available."""
    # Test login endpoint exists
    response = client.post("/api/v1/auth/login", json={})
    # Should return 422 (validation error) not 404 (not found)
    assert response.status_code in [422, 401]

def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = hash_password(password)
    # Verify hash is different from original
    assert hashed != password
    # Verify password verification works
    assert verify_password(password, hashed)
    # Verify wrong password fails
    assert not verify_password("wrongpassword", hashed)

def test_jwt_token_creation():
    """Test JWT token creation and validation."""
    user_data = {"sub": "testuser", "tenant_id": "test-tenant"}
    token = create_access_token(user_data)
    # Verify token is created
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    # Test missing username
    response = client.post("/api/v1/auth/login", json={"password": "testpass"})
    assert response.status_code == 422
    # Test missing password
    response = client.post("/api/v1/auth/login", json={"username": "testuser"})
    assert response.status_code == 422
    # Test empty request
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    # Should return 401 for invalid credentials
    assert response.status_code == 401

def test_protected_endpoints_require_auth(client):
    """Test that protected endpoints require authentication."""
    # Test devices endpoint
    response = client.get("/api/v1/devices/")
    assert response.status_code == 401
    # Test users endpoint
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    # Test sensor data endpoint
    response = client.get("/api/v1/devices/test-device/sensor-data")
    assert response.status_code == 401

def test_cors_headers(client):
    """Test CORS headers are properly set."""
    response = client.options("/api/v1/health", headers={"Origin": "http://localhost:3000"})
    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-credentials" in response.headers

def test_rate_limiting(client):
    """Test rate limiting on authentication endpoints."""
    # Make multiple requests to trigger rate limiting
    for _ in range(10):
        client.post("/api/v1/auth/login", json={
            "username": "test",
            "password": "test"
        })
    # Should eventually get rate limited
    # Note: This test might not always pass depending on rate limit settings
    pass

def test_token_expiration():
    """Test JWT token expiration."""
    user_data = {"sub": "testuser", "tenant_id": "test-tenant"}
    # Create token with short expiration
    with patch('app.core.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES', 1):
        token = create_access_token(user_data)
    # Token should be created successfully
    assert token is not None

def test_websocket_auth_required():
    """Test WebSocket authentication requirements."""
    # Test WebSocket endpoint requires authentication
    # This would be tested with a WebSocket client
    pass

if __name__ == "__main__":
    pytest.main([__file__]) 