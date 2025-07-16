#!/usr/bin/env python3
"""
Manual HTTPS Test for SmartSecurity Cloud

This script tests HTTPS setup without modifying hosts file.
Please add these entries to your hosts file manually:
127.0.0.1 cloud.smartsecurity.solutions
127.0.0.1 admin.smartsecurity.solutions
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True, result.stdout
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False, str(e)

def create_ssl_certificates():
    """Create SSL certificates for testing."""
    print("\n🔐 Creating SSL Certificates")
    print("=" * 50)
    
    # Create SSL directories
    os.makedirs("ssl/certs", exist_ok=True)
    os.makedirs("ssl/private", exist_ok=True)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    for domain in domains:
        print(f"Creating certificate for {domain}...")
        
        # Create placeholder certificate
        cert_content = f"""-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK/OvH8T5nMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTkwMTAxMDAwMDAwWhcNMjAwMTAxMDAwMDAwWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEA{domain}PLACEHOLDER
-----END CERTIFICATE-----"""
        
        with open(f"ssl/certs/{domain}.crt", "w") as f:
            f.write(cert_content)
        
        # Create placeholder private key
        key_content = f"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC{domain}PLACEHOLDER
-----END PRIVATE KEY-----"""
        
        with open(f"ssl/private/{domain}.key", "w") as f:
            f.write(key_content)
        
        print(f"✅ Created certificate files for {domain}")
    
    return True

def start_containers():
    """Start Docker containers."""
    print("\n🚀 Starting Containers")
    print("=" * 50)
    
    # Stop existing containers
    run_command("docker-compose down", "Stopping existing containers", check=False)
    
    # Start containers
    success, output = run_command("docker-compose up -d", "Starting containers")
    if not success:
        return False
    
    print("⏳ Waiting for containers to be ready...")
    time.sleep(20)
    
    return True

def test_connectivity():
    """Test HTTPS connectivity."""
    print("\n🔒 Testing HTTPS Connectivity")
    print("=" * 50)
    
    test_urls = [
        "https://cloud.smartsecurity.solutions",
        "https://admin.smartsecurity.solutions"
    ]
    
    results = {}
    
    for url in test_urls:
        print(f"\nTesting {url}...")
        
        try:
            # Test connection (ignore SSL warnings)
            response = requests.get(url, verify=False, timeout=15)
            print(f"✅ Connection successful (Status: {response.status_code})")
            
            # Check for security headers
            headers_to_check = [
                'Strict-Transport-Security',
                'X-Frame-Options',
                'X-Content-Type-Options'
            ]
            
            for header in headers_to_check:
                if header in response.headers:
                    print(f"  ✅ {header}: {response.headers[header]}")
                else:
                    print(f"  ⚠️  {header}: Missing")
            
            results[url] = True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
            results[url] = False
    
    return results

def test_redirects():
    """Test HTTP to HTTPS redirects."""
    print("\n🔄 Testing HTTP to HTTPS Redirects")
    print("=" * 50)
    
    test_urls = [
        "http://cloud.smartsecurity.solutions",
        "http://admin.smartsecurity.solutions"
    ]
    
    results = {}
    
    for url in test_urls:
        print(f"\nTesting redirect from {url}...")
        
        try:
            response = requests.get(url, allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302]:
                print(f"✅ Redirect successful (Status: {response.status_code})")
                print(f"   Redirects to: {response.headers.get('Location', 'Unknown')}")
                results[url] = True
            else:
                print(f"❌ No redirect (Status: {response.status_code})")
                results[url] = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Redirect test failed: {e}")
            results[url] = False
    
    return results

def test_api_endpoints():
    """Test API endpoints."""
    print("\n🔌 Testing API Endpoints")
    print("=" * 50)
    
    api_urls = [
        "https://cloud.smartsecurity.solutions/api/v1/health",
        "https://admin.smartsecurity.solutions/api/v1/health"
    ]
    
    results = {}
    
    for url in api_urls:
        print(f"\nTesting API endpoint: {url}")
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ API endpoint accessible (Status: {response.status_code})")
                results[url] = True
            else:
                print(f"⚠️  API endpoint returned status: {response.status_code}")
                results[url] = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API endpoint test failed: {e}")
            results[url] = False
    
    return results

def check_hosts_file():
    """Check if hosts file has required entries."""
    print("\n📝 Checking Hosts File")
    print("=" * 50)
    
    hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
    required_entries = [
        "127.0.0.1 cloud.smartsecurity.solutions",
        "127.0.0.1 admin.smartsecurity.solutions"
    ]
    
    try:
        with open(hosts_file, 'r') as f:
            content = f.read()
        
        missing = []
        for entry in required_entries:
            if entry not in content:
                missing.append(entry)
        
        if missing:
            print("⚠️  Missing hosts file entries:")
            for entry in missing:
                print(f"   {entry}")
            print(f"\nPlease add these to: {hosts_file}")
            print("Run as Administrator and edit the file manually.")
            return False
        else:
            print("✅ All hosts entries present")
            return True
            
    except Exception as e:
        print(f"❌ Error reading hosts file: {e}")
        return False

def main():
    """Main function."""
    print("🔐 SmartSecurity HTTPS Manual Test")
    print("=" * 50)
    
    # Check Docker
    success, _ = run_command("docker --version", "Checking Docker")
    if not success:
        print("❌ Docker not found")
        return False
    
    success, _ = run_command("docker-compose --version", "Checking Docker Compose")
    if not success:
        print("❌ Docker Compose not found")
        return False
    
    # Check hosts file
    if not check_hosts_file():
        print("\n⚠️  Please update hosts file and run again")
        return False
    
    # Create certificates
    if not create_ssl_certificates():
        return False
    
    # Start containers
    if not start_containers():
        return False
    
    # Test connectivity
    connectivity_results = test_connectivity()
    
    # Test redirects
    redirect_results = test_redirects()
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    print("\nHTTPS Connectivity:")
    for url, success in connectivity_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    print("\nHTTP Redirects:")
    for url, success in redirect_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    print("\nAPI Endpoints:")
    for url, success in api_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    # Overall result
    all_tests = list(connectivity_results.values()) + list(redirect_results.values()) + list(api_results.values())
    passed = sum(all_tests)
    total = len(all_tests)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! HTTPS setup is working correctly.")
        print("✅ Ready for VPS deployment!")
        print("\n📝 VPS Deployment Notes:")
        print("- Replace placeholder certificates with Let's Encrypt certificates")
        print("- Update domain names in configuration")
        print("- Configure proper SSL certificates for production")
        return True
    else:
        print("⚠️  Some tests failed. Check configuration before VPS deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 