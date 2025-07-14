#!/usr/bin/env python3
"""
Quick test to verify the SmartSecurity.Solutions Cloud test server
"""

import requests
import time

def test_server():
    """Test the server on port 8001"""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing SmartSecurity.Solutions Cloud Test Server")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data.get('message')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Login
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful: {data.get('username')}")
            
            # Test 4: Get current user with token
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Get current user: {user_data.get('username')}")
            else:
                print(f"❌ Get current user failed: {response.status_code}")
                
            # Test 5: Create device
            response = requests.post(f"{base_url}/api/v1/devices", json={
                "name": "Test Device",
                "description": "Test device for API testing"
            }, headers=headers)
            if response.status_code == 200:
                device_data = response.json()
                print(f"✅ Device created: {device_data.get('name')}")
            else:
                print(f"❌ Device creation failed: {response.status_code}")
                
            # Test 6: Get devices
            response = requests.get(f"{base_url}/api/v1/devices", headers=headers)
            if response.status_code == 200:
                devices = response.json()
                print(f"✅ Get devices: {len(devices)} devices found")
            else:
                print(f"❌ Get devices failed: {response.status_code}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 7: Data ingestion
    try:
        health_data = {
            "deviceId": "test-device-123",
            "timestamp": time.time(),
            "batteryPercent": 85.5,
            "lteRssi": -65,
            "wifiRssi": -45
        }
        response = requests.post(f"{base_url}/api/v1/ingest/root/v1/health", json=health_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data ingestion: {data.get('message')}")
        else:
            print(f"❌ Data ingestion failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Data ingestion error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")

if __name__ == "__main__":
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    test_server() 