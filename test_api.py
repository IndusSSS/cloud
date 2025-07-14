#!/usr/bin/env python3
"""
Test script for cloud API endpoints.
"""

import requests
import json
import time
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health_beacon_endpoint():
    """Test the health beacon endpoint."""
    print("\nTesting health beacon endpoint...")
    
    # Create test data
    test_data = {
        "deviceId": str(uuid4()),
        "timestamp": "2025-07-10T12:00:00Z",
        "batteryPercent": 85,
        "lteRssi": -70,
        "wifiRssi": -45
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/root/v1/health",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_openapi_docs():
    """Test if OpenAPI docs are accessible."""
    print("\nTesting OpenAPI docs...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting API tests...")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(3)
    
    # Run tests
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Health Beacon Endpoint", test_health_beacon_endpoint),
        ("OpenAPI Docs", test_openapi_docs),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("=" * 50)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    main() 