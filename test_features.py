#!/usr/bin/env python3
"""
Comprehensive feature testing for SmartSecurity.Solutions Cloud
Tests all major functionality including authentication, device management, and data ingestion.
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

class SmartSecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_openapi_docs(self) -> bool:
        """Test OpenAPI documentation"""
        try:
            response = self.session.get(f"{API_BASE}/docs")
            if response.status_code == 200:
                self.log_test("OpenAPI Documentation", True, "Docs accessible")
                return True
            else:
                self.log_test("OpenAPI Documentation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("OpenAPI Documentation", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self) -> bool:
        """Test user registration"""
        try:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            }
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("User Registration", True, f"User ID: {data.get('id')}")
                return True
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """Test user login and token generation"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, f"Token received for user: {data.get('username')}")
                    return True
                else:
                    self.log_test("User Login", False, "No token in response")
                    return False
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            return False
    
    def test_get_current_user(self) -> bool:
        """Test getting current user info"""
        if not self.auth_token:
            self.log_test("Get Current User", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Current User", True, f"User: {data.get('username')}")
                return True
            else:
                self.log_test("Get Current User", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Current User", False, f"Error: {str(e)}")
            return False
    
    def test_device_creation(self) -> bool:
        """Test device creation"""
        if not self.auth_token:
            self.log_test("Device Creation", False, "No auth token available")
            return False
            
        try:
            device_data = {
                "name": "Test Device",
                "description": "Test device for API testing"
            }
            response = self.session.post(f"{API_BASE}/devices", json=device_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Device Creation", True, f"Device ID: {data.get('id')}")
                return True
            else:
                self.log_test("Device Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Device Creation", False, f"Error: {str(e)}")
            return False
    
    def test_device_listing(self) -> bool:
        """Test device listing"""
        if not self.auth_token:
            self.log_test("Device Listing", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/devices")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Device Listing", True, f"Found {len(data)} devices")
                return True
            else:
                self.log_test("Device Listing", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Device Listing", False, f"Error: {str(e)}")
            return False
    
    def test_data_ingestion(self) -> bool:
        """Test sensor data ingestion"""
        try:
            # First create a device if we have auth
            device_id = None
            if self.auth_token:
                device_data = {"name": "Ingest Test Device", "description": "For ingestion testing"}
                response = self.session.post(f"{API_BASE}/devices", json=device_data)
                if response.status_code in [200, 201]:
                    device_id = response.json().get("id")
            
            # Test health beacon endpoint (doesn't require auth)
            health_data = {
                "deviceId": device_id or "test-device-123",
                "timestamp": datetime.now().isoformat(),
                "batteryPercent": 85.5,
                "lteRssi": -65,
                "wifiRssi": -45
            }
            
            response = self.session.post(f"{API_BASE}/ingest/root/v1/health", json=health_data)
            if response.status_code in [200, 201]:
                self.log_test("Data Ingestion", True, "Health beacon data ingested")
                return True
            else:
                self.log_test("Data Ingestion", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Data Ingestion", False, f"Error: {str(e)}")
            return False
    
    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        try:
            import websocket
            ws = websocket.create_connection(f"ws://localhost:8001/ws/default")
            ws.send("ping")
            response = ws.recv()
            ws.close()
            self.log_test("WebSocket Connection", True, "Connection established")
            return True
        except ImportError:
            self.log_test("WebSocket Connection", False, "websocket-client not installed")
            return False
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting SmartSecurity.Solutions Cloud Feature Tests")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_health_check()
        self.test_openapi_docs()
        
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        
        # Device management tests
        self.test_device_creation()
        self.test_device_listing()
        
        # Data ingestion tests
        self.test_data_ingestion()
        
        # Real-time features
        self.test_websocket_connection()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Save results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results.json")
        
        if passed == total:
            print("\n🎉 All tests passed! The SmartSecurity.Solutions Cloud is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Check the details above.")
        
        return passed == total

def main():
    """Main test runner"""
    tester = SmartSecurityTester()
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 