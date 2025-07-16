#!/usr/bin/env python3
"""
HTTPS Setup Test Script for SmartSecurity Cloud

This script tests the complete HTTPS setup including:
- SSL certificate generation
- Docker container startup
- HTTPS connectivity
- Security headers
- HTTP to HTTPS redirects
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Disable SSL warnings for self-signed certificates
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    # urllib3 not available, continue without disabling warnings
    pass

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

def generate_ssl_certificates():
    """Generate SSL certificates for testing."""
    print("\n🔐 Generating SSL Certificates")
    print("=" * 50)
    
    # Create SSL directories
    os.makedirs("ssl/certs", exist_ok=True)
    os.makedirs("ssl/private", exist_ok=True)
    
    # Generate certificates using OpenSSL
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    for domain in domains:
        print(f"\nGenerating certificate for {domain}...")
        
        # Generate private key
        success, _ = run_command(
            f'openssl genrsa -out "ssl/private/{domain}.key" 2048',
            f"Generating private key for {domain}"
        )
        if not success:
            print(f"⚠️  Using placeholder key for {domain}")
            with open(f"ssl/private/{domain}.key", "w") as f:
                f.write("-----BEGIN PRIVATE KEY-----\nPLACEHOLDER\n-----END PRIVATE KEY-----\n")
        
        # Generate certificate
        success, _ = run_command(
            f'openssl req -new -x509 -key "ssl/private/{domain}.key" -out "ssl/certs/{domain}.crt" -days 365 -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN={domain}"',
            f"Generating certificate for {domain}"
        )
        if not success:
            print(f"⚠️  Using placeholder certificate for {domain}")
            with open(f"ssl/certs/{domain}.crt", "w") as f:
                f.write("-----BEGIN CERTIFICATE-----\nPLACEHOLDER\n-----END CERTIFICATE-----\n")
    
    return True

def check_docker_status():
    """Check if Docker is running and containers are up."""
    print("\n🐳 Checking Docker Status")
    print("=" * 50)
    
    # Check if Docker is running
    success, output = run_command("docker --version", "Checking Docker installation")
    if not success:
        return False
    
    # Check if containers are running
    success, output = run_command("docker-compose ps", "Checking container status")
    if not success:
        return False
    
    print("Container status:")
    print(output)
    return True

def start_docker_containers():
    """Start Docker containers for testing."""
    print("\n🚀 Starting Docker Containers")
    print("=" * 50)
    
    # Stop any existing containers
    run_command("docker-compose down", "Stopping existing containers", check=False)
    
    # Start containers
    success, output = run_command("docker-compose up -d", "Starting containers")
    if not success:
        return False
    
    # Wait for containers to be ready
    print("⏳ Waiting for containers to be ready...")
    time.sleep(10)
    
    return True

def test_https_connectivity():
    """Test HTTPS connectivity and security headers."""
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
            # Test HTTPS connection
            response = requests.get(url, verify=False, timeout=10)
            
            print(f"✅ HTTPS connection successful (Status: {response.status_code})")
            
            # Check security headers
            security_headers = {
                'Strict-Transport-Security': 'HSTS header present',
                'X-Frame-Options': 'Clickjacking protection',
                'X-Content-Type-Options': 'MIME sniffing protection',
                'X-XSS-Protection': 'XSS protection',
                'Content-Security-Policy': 'CSP header present'
            }
            
            print("Security headers:")
            for header, description in security_headers.items():
                if header in response.headers:
                    print(f"  ✅ {header}: {response.headers[header]}")
                else:
                    print(f"  ⚠️  {header}: Missing")
            
            results[url] = True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTPS connection failed: {e}")
            results[url] = False
    
    return results

def test_http_redirects():
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
    """Test API endpoints over HTTPS."""
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

def update_hosts_file():
    """Update hosts file for local testing."""
    print("\n📝 Updating Hosts File")
    print("=" * 50)
    
    hosts_entries = [
        "127.0.0.1 cloud.smartsecurity.solutions",
        "127.0.0.1 admin.smartsecurity.solutions"
    ]
    
    hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
    
    try:
        with open(hosts_file, 'r') as f:
            content = f.read()
        
        # Check if entries already exist
        missing_entries = []
        for entry in hosts_entries:
            if entry not in content:
                missing_entries.append(entry)
        
        if missing_entries:
            print("⚠️  The following entries need to be added to your hosts file:")
            for entry in missing_entries:
                print(f"   {entry}")
            print(f"\nHosts file location: {hosts_file}")
            print("Please add these entries manually and run the test again.")
            return False
        else:
            print("✅ All required hosts entries are present")
            return True
            
    except Exception as e:
        print(f"❌ Error reading hosts file: {e}")
        return False

def main():
    """Main test function."""
    print("🔐 SmartSecurity HTTPS Setup Test")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking Prerequisites")
    print("=" * 50)
    
    # Check if Docker is available
    success, _ = run_command("docker --version", "Checking Docker")
    if not success:
        print("❌ Docker is not installed or not in PATH")
        return False
    
    # Check if docker-compose is available
    success, _ = run_command("docker-compose --version", "Checking Docker Compose")
    if not success:
        print("❌ Docker Compose is not installed or not in PATH")
        return False
    
    # Generate SSL certificates
    if not generate_ssl_certificates():
        print("❌ Failed to generate SSL certificates")
        return False
    
    # Update hosts file
    if not update_hosts_file():
        print("⚠️  Please update hosts file and run the test again")
        return False
    
    # Start Docker containers
    if not start_docker_containers():
        print("❌ Failed to start Docker containers")
        return False
    
    # Wait a bit more for services to be ready
    print("⏳ Waiting for services to be fully ready...")
    time.sleep(15)
    
    # Test HTTPS connectivity
    https_results = test_https_connectivity()
    
    # Test HTTP redirects
    redirect_results = test_http_redirects()
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    print("\nHTTPS Connectivity:")
    for url, success in https_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    print("\nHTTP to HTTPS Redirects:")
    for url, success in redirect_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    print("\nAPI Endpoints:")
    for url, success in api_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    # Overall result
    all_tests = list(https_results.values()) + list(redirect_results.values()) + list(api_results.values())
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! HTTPS setup is working correctly.")
        print("✅ Ready for VPS deployment!")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 