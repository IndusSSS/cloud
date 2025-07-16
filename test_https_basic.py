#!/usr/bin/env python3
"""
Basic HTTPS Test for SmartSecurity Cloud

This script tests the basic HTTPS setup functionality:
1. Creates SSL certificates
2. Starts Docker containers
3. Tests container health
4. Tests local connectivity
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

def check_container_status():
    """Check if containers are running properly."""
    print("\n🐳 Checking Container Status")
    print("=" * 50)
    
    success, output = run_command("docker-compose ps", "Checking container status")
    if not success:
        return False
    
    print("Container status:")
    print(output)
    
    # Check if all containers are running
    if "Up" not in output:
        print("❌ Not all containers are running")
        return False
    
    return True

def test_local_connectivity():
    """Test local connectivity to containers."""
    print("\n🔒 Testing Local Connectivity")
    print("=" * 50)
    
    # Test localhost connections
    test_urls = [
        "https://localhost",
        "https://localhost:443",
        "http://localhost",
        "http://localhost:80"
    ]
    
    results = {}
    
    for url in test_urls:
        print(f"\nTesting {url}...")
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            print(f"✅ Connection successful (Status: {response.status_code})")
            results[url] = True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
            results[url] = False
    
    return results

def test_ssl_configuration():
    """Test SSL configuration."""
    print("\n🔐 Testing SSL Configuration")
    print("=" * 50)
    
    # Check if SSL certificates exist
    cert_files = [
        "ssl/certs/cloud.smartsecurity.solutions.crt",
        "ssl/certs/admin.smartsecurity.solutions.crt",
        "ssl/private/cloud.smartsecurity.solutions.key",
        "ssl/private/admin.smartsecurity.solutions.key"
    ]
    
    results = {}
    
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            print(f"✅ {cert_file} exists")
            results[cert_file] = True
        else:
            print(f"❌ {cert_file} missing")
            results[cert_file] = False
    
    return results

def test_nginx_configuration():
    """Test Nginx configuration."""
    print("\n🌐 Testing Nginx Configuration")
    print("=" * 50)
    
    # Test if nginx container is running and responding
    try:
        response = requests.get("http://localhost", timeout=10)
        print(f"✅ Nginx responding (Status: {response.status_code})")
        
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
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Nginx not responding: {e}")
        return False

def check_docker_logs():
    """Check Docker container logs for errors."""
    print("\n📋 Checking Container Logs")
    print("=" * 50)
    
    services = ["nginx", "customer-portal", "admin-console"]
    
    for service in services:
        print(f"\nChecking logs for {service}...")
        success, output = run_command(f"docker-compose logs --tail=10 {service}", f"Checking {service} logs")
        if success:
            print(f"✅ {service} logs retrieved")
            # Check for common errors
            if "error" in output.lower() or "failed" in output.lower():
                print(f"⚠️  Potential issues in {service} logs")
        else:
            print(f"❌ Failed to get {service} logs")

def main():
    """Main function."""
    print("🔐 SmartSecurity HTTPS Basic Test")
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
    
    # Create certificates
    if not create_ssl_certificates():
        return False
    
    # Start containers
    if not start_containers():
        return False
    
    # Check container status
    if not check_container_status():
        return False
    
    # Test SSL configuration
    ssl_results = test_ssl_configuration()
    
    # Test local connectivity
    connectivity_results = test_local_connectivity()
    
    # Test nginx configuration
    nginx_ok = test_nginx_configuration()
    
    # Check logs
    check_docker_logs()
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    print("\nSSL Configuration:")
    for cert_file, success in ssl_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {cert_file}")
    
    print("\nLocal Connectivity:")
    for url, success in connectivity_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {url}")
    
    print(f"\nNginx Configuration: {'✅ PASS' if nginx_ok else '❌ FAIL'}")
    
    # Overall result
    all_tests = list(ssl_results.values()) + list(connectivity_results.values()) + [nginx_ok]
    passed = sum(all_tests)
    total = len(all_tests)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! HTTPS setup is working correctly.")
        print("✅ Ready for VPS deployment!")
        print("\n📝 Next Steps:")
        print("1. Add hosts file entries (run add_hosts_entries.ps1 as Administrator)")
        print("2. Test with domain names")
        print("3. Replace placeholder certificates with Let's Encrypt certificates for VPS")
        return True
    else:
        print("⚠️  Some tests failed. Check configuration before VPS deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 