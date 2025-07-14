#!/usr/bin/env python3
"""
Save the generated API token to a configuration file.
"""

import json
from datetime import datetime
from generate_api_token import create_smartsecurity_api_token

def save_api_token():
    """Generate and save API token to configuration file."""
    
    # Generate the API token
    token_data = create_smartsecurity_api_token()
    
    # Create configuration object
    config = {
        "api_token": token_data["api_token"],
        "client_id": token_data["client_id"],
        "permissions": token_data["permissions"],
        "expires_at": token_data["expires_at"],
        "token_type": token_data["token_type"],
        "base_url": "https://cloud.smartsecurity.solutions/api/v1",
        "generated_at": datetime.now().isoformat(),
        "usage_instructions": {
            "header_format": "Authorization: Bearer <api_token>",
            "example": f"Authorization: Bearer {token_data['api_token'][:50]}...",
            "endpoints": [
                "GET /health",
                "GET /devices", 
                "GET /sensors",
                "POST /ingest",
                "GET /alerts"
            ]
        }
    }
    
    # Save to JSON file
    with open("api_token_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Save to environment file format
    with open("api_token.env", "w") as f:
        f.write(f"# SmartSecurity Cloud API Token Configuration\n")
        f.write(f"# Generated: {config['generated_at']}\n")
        f.write(f"# Expires: {config['expires_at']}\n\n")
        f.write(f"API_TOKEN={config['api_token']}\n")
        f.write(f"API_CLIENT_ID={config['client_id']}\n")
        f.write(f"API_BASE_URL={config['base_url']}\n")
        f.write(f"API_TOKEN_TYPE={config['token_type']}\n")
    
    print("✅ API Token saved to configuration files:")
    print("   - api_token_config.json (full configuration)")
    print("   - api_token.env (environment variables)")
    print(f"\n🔑 API Token: {config['api_token']}")
    print(f"📅 Expires: {config['expires_at']}")
    
    return config

if __name__ == "__main__":
    save_api_token() 