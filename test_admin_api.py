#!/usr/bin/env python3
"""
Test script for SmartSecurity Admin API endpoints.
Tests all admin functionality including RBAC, CRUD operations, and audit logging.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_BASE_URL = f"{BASE_URL}/admin"

class AdminAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.tenant_admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_health_check(self) -> bool:
        """Test basic health check."""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log_test("Health Check", True)
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {e}")
            return False
    
    def test_admin_login(self) -> bool:
        """Test admin login."""
        try:
            # First, try to register a system admin if needed
            register_data = {
                "username": "sysadmin",
                "email": "sysadmin@smartsecurity.solutions",
                "password": "admin123"
            }
            
            # Try to create system admin (this might fail if already exists)
            try:
                response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
                if response.status_code == 200:
                    print("   Created system admin user")
            except:
                pass  # User might already exist
            
            # Login as system admin
            login_data = {
                "username": "sysadmin",
                "password": "admin123"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", data=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Login", True)
                return True
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {e}")
            return False
    
    def test_tenant_creation(self) -> bool:
        """Test tenant creation."""
        try:
            tenant_data = {
                "name": "Test Tenant",
                "plan": "pro"
            }
            
            response = self.session.post(f"{ADMIN_BASE_URL}/tenants/", json=tenant_data)
            if response.status_code == 200:
                tenant = response.json()
                self.test_tenant_id = tenant.get("id")
                self.log_test("Tenant Creation", True, f"Tenant ID: {self.test_tenant_id}")
                return True
            else:
                self.log_test("Tenant Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Tenant Creation", False, f"Error: {e}")
            return False
    
    def test_tenant_listing(self) -> bool:
        """Test tenant listing."""
        try:
            response = self.session.get(f"{ADMIN_BASE_URL}/tenants/")
            if response.status_code == 200:
                tenants = response.json()
                self.log_test("Tenant Listing", True, f"Found {len(tenants)} tenants")
                return True
            else:
                self.log_test("Tenant Listing", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Tenant Listing", False, f"Error: {e}")
            return False
    
    def test_user_creation(self) -> bool:
        """Test user creation within tenant."""
        try:
            user_data = {
                "username": "tenantuser",
                "email": "user@testtenant.com",
                "password": "user123",
                "is_admin": True
            }
            
            response = self.session.post(f"{ADMIN_BASE_URL}/users/", json=user_data)
            if response.status_code == 200:
                user = response.json()
                self.test_user_id = user.get("id")
                self.log_test("User Creation", True, f"User ID: {self.test_user_id}")
                return True
            else:
                self.log_test("User Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Creation", False, f"Error: {e}")
            return False
    
    def test_device_creation(self) -> bool:
        """Test device creation with specifications."""
        try:
            device_data = {
                "name": "Test Device",
                "description": "Test device for admin console",
                "specifications": {
                    "type": "temperature_sensor",
                    "model": "TS-100",
                    "manufacturer": "TestCorp",
                    "location": "Test Location"
                }
            }
            
            response = self.session.post(f"{ADMIN_BASE_URL}/devices/", json=device_data)
            if response.status_code == 200:
                device = response.json()
                self.test_device_id = device.get("id")
                self.log_test("Device Creation", True, f"Device ID: {self.test_device_id}")
                return True
            else:
                self.log_test("Device Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Device Creation", False, f"Error: {e}")
            return False
    
    def test_audit_logs(self) -> bool:
        """Test audit log access."""
        try:
            response = self.session.get(f"{ADMIN_BASE_URL}/audit/")
            if response.status_code == 200:
                logs = response.json()
                self.log_test("Audit Logs", True, f"Found {len(logs)} audit entries")
                return True
            else:
                self.log_test("Audit Logs", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Audit Logs", False, f"Error: {e}")
            return False
    
    def test_ota_rollout(self) -> bool:
        """Test OTA firmware rollout."""
        try:
            ota_data = {
                "device_ids": [self.test_device_id] if hasattr(self, 'test_device_id') else ["test-device-123"],
                "firmware_version": "v2.1.0",
                "rollout_schedule": {
                    "start_time": "2024-01-01T00:00:00Z",
                    "batch_size": 10
                }
            }
            
            response = self.session.post(f"{ADMIN_BASE_URL}/ota/firmware/rollout", json=ota_data)
            if response.status_code == 200:
                result = response.json()
                self.log_test("OTA Rollout", True, f"Status: {result.get('status')}")
                return True
            else:
                self.log_test("OTA Rollout", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("OTA Rollout", False, f"Error: {e}")
            return False
    
    def test_rbac_protection(self) -> bool:
        """Test RBAC protection - non-admin should get 403."""
        try:
            # Create a non-admin session
            non_admin_session = requests.Session()
            
            # Try to access admin endpoints without token
            response = non_admin_session.get(f"{ADMIN_BASE_URL}/tenants/")
            if response.status_code == 401 or response.status_code == 403:
                self.log_test("RBAC Protection", True, "Non-admin access properly blocked")
                return True
            else:
                self.log_test("RBAC Protection", False, f"Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("RBAC Protection", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all admin API tests."""
        print("🚀 Testing SmartSecurity Admin API")
        print("=" * 50)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Login", self.test_admin_login),
            ("RBAC Protection", self.test_rbac_protection),
            ("Tenant Creation", self.test_tenant_creation),
            ("Tenant Listing", self.test_tenant_listing),
            ("User Creation", self.test_user_creation),
            ("Device Creation", self.test_device_creation),
            ("Audit Logs", self.test_audit_logs),
            ("OTA Rollout", self.test_ota_rollout),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! Admin API is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the details above.")
        
        return passed == total

def main():
    """Main test function."""
    tester = AdminAPITester()
    success = tester.run_all_tests()
    
    # Save results
    with open("admin_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 