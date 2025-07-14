#!/usr/bin/env python3
"""
Test the generated API token with the SmartSecurity Cloud API.
"""

import json
import jwt
from datetime import datetime, timezone
from generate_api_token import generate_api_token

def test_api_token():
    """Test the generated API token."""
    
    # Load the saved configuration
    try:
        with open("api_token_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ api_token_config.json not found. Run save_api_token.py first.")
        return False
    
    api_token = config["api_token"]
    client_id = config["client_id"]
    
    print("🔍 Testing API Token...")
    print(f"   Client ID: {client_id}")
    print(f"   Token: {api_token[:50]}...")
    
    # Test token verification
    try:
        # Use the same secret key as in generate_api_token.py
        API_TOKEN_SECRET = "smartsecurity-cloud-api-token-secret-key-2024"
        API_TOKEN_ALGORITHM = "HS256"
        
        # Decode the token
        payload = jwt.decode(
            api_token, 
            API_TOKEN_SECRET, 
            algorithms=[API_TOKEN_ALGORITHM]
        )
        
        print("\n✅ Token verification successful!")
        print(f"   Token Type: {payload.get('token_type')}")
        print(f"   Permissions: {payload.get('permissions')}")
        print(f"   Expires: {datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)}")
        
        # Check if token is expired
        current_time = datetime.now(timezone.utc)
        exp_time = datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)
        
        if current_time < exp_time:
            print(f"   Status: ✅ Valid (expires in {exp_time - current_time})")
        else:
            print(f"   Status: ❌ Expired")
            return False
        
        # Test token generation with same parameters
        test_token = generate_api_token(
            client_id=client_id,
            permissions=payload.get('permissions'),
            expires_delta=None  # Use default 1 year
        )
        
        print(f"\n🔄 Token regeneration test: {'✅ Passed' if test_token else '❌ Failed'}")
        
        return True
        
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        return False
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 SmartSecurity Cloud API Token Test")
    print("=" * 50)
    
    success = test_api_token()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 API Token test completed successfully!")
        print("\n📋 Usage Example:")
        print("   curl -H 'Authorization: Bearer <your-api-token>' \\")
        print("        https://cloud.smartsecurity.solutions/api/v1/health")
    else:
        print("\n" + "=" * 50)
        print("❌ API Token test failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 