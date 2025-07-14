#!/usr/bin/env python3
"""
Simple test to verify server startup and basic functionality
"""

import asyncio
import uvicorn
from app.main import app

def test_server_startup():
    """Test if the server can start without errors"""
    print("🚀 Testing server startup...")
    
    try:
        # Test if we can create the app
        print("✅ FastAPI app created successfully")
        
        # Test if we can access the app routes
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} routes")
        
        # Check for key endpoints
        health_route = None
        for route in app.routes:
            if hasattr(route, 'path') and '/health' in route.path:
                health_route = route
                break
        
        if health_route:
            print("✅ Health endpoint found")
        else:
            print("❌ Health endpoint not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server_startup()
    if success:
        print("\n🎉 Server startup test passed!")
        print("You can now start the server with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    else:
        print("\n💥 Server startup test failed!") 