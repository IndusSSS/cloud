#!/usr/bin/env python3
"""
SmartSecurity Cloud API Token Generator

This script generates secure API tokens for external service authentication
with the SmartSecurity Cloud platform.

Usage:
    python generate_api_token.py
"""

import secrets
import string
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional


def generate_api_token(
    client_id: str,
    permissions: Optional[list] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a long-lived API token for external service authentication."""
    if permissions is None:
        permissions = ["read", "write"]
    
    if expires_delta is None:
        expires_delta = timedelta(days=365)  # 1 year expiration
    
    # API Token configuration
    API_TOKEN_SECRET = "smartsecurity-cloud-api-token-secret-key-2024"
    API_TOKEN_ALGORITHM = "HS256"
    
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
        API_TOKEN_SECRET, 
        algorithm=API_TOKEN_ALGORITHM
    )
    
    return api_token


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


def main():
    """Generate and display the SmartSecurity Cloud API token."""
    print("🔐 SmartSecurity Cloud API Token Generator")
    print("=" * 50)
    
    try:
        # Generate the API token
        token_data = create_smartsecurity_api_token()
        
        print("\n✅ API Token Generated Successfully!")
        print("\n📋 Token Details:")
        print(f"   Client ID: {token_data['client_id']}")
        print(f"   Token Type: {token_data['token_type']}")
        print(f"   Expires At: {token_data['expires_at']}")
        print(f"   Permissions: {', '.join(token_data['permissions'])}")
        
        print("\n🔑 API Token:")
        print(f"   {token_data['api_token']}")
        
        print("\n📖 Usage Instructions:")
        print("   1. Include this token in the Authorization header of your HTTP requests")
        print("   2. Format: Authorization: Bearer <api_token>")
        print("   3. Example: Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        
        print("\n🌐 API Endpoints:")
        print("   Base URL: https://cloud.smartsecurity.solutions/api/v1")
        print("   Health Check: GET /health")
        print("   Devices: GET /devices")
        print("   Sensors: GET /sensors")
        print("   Data Ingestion: POST /ingest")
        
        print("\n⚠️  Security Notes:")
        print("   - Keep this token secure and do not share it publicly")
        print("   - The token expires in 1 year")
        print("   - Store the token in environment variables or secure configuration")
        print("   - Rotate the token regularly for enhanced security")
        
        print("\n" + "=" * 50)
        print("🎉 Your SmartSecurity Cloud API token is ready to use!")
        
    except Exception as e:
        print(f"\n❌ Error generating API token: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 