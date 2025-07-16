#!/usr/bin/env python3
"""
HTTPS Setup Test Script for Smart Security Cloud
Tests the SSL certificate setup and domain accessibility
"""

import requests
import subprocess
import sys
import time
from urllib.parse import urlparse
import json

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[0;32m",    # Green
        "WARNING": "\033[1;33m", # Yellow
        "ERROR": "\033[0;31m",   # Red
        "SUCCESS": "\033[0;36m"  # Cyan
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['INFO'])}[{status}]{reset} {message}")

def test_domain_https(domain):
    """Test if a domain is accessible via HTTPS"""
    url = f"https://{domain}"
    try:
        response = requests.get(url, timeout=10, verify=True)
        if response.status_code in [200, 301, 302]:
            print_status(f"✅ {domain} HTTPS is working (Status: {response.status_code})", "SUCCESS")
            return True
        else:
            print_status(f"⚠️  {domain} returned status {response.status_code}", "WARNING")
            return False
    except requests.exceptions.SSLError as e:
        print_status(f"❌ {domain} SSL error: {e}", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        print_status(f"❌ {domain} connection error: {e}", "ERROR")
        return False

def test_domain_http_redirect(domain):
    """Test if HTTP redirects to HTTPS"""
    url = f"http://{domain}"
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        if response.status_code == 301 and 'https://' in response.headers.get('Location', ''):
            print_status(f"✅ {domain} HTTP to HTTPS redirect working", "SUCCESS")
            return True
        else:
            print_status(f"⚠️  {domain} HTTP redirect not working properly", "WARNING")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"❌ {domain} HTTP redirect test failed: {e}", "ERROR")
        return False

def check_ssl_certificates():
    """Check if SSL certificates exist and are valid"""
    print_status("Checking SSL certificates...")
    
    cert_files = [
        "ssl/certs/cloud.smartsecurity.solutions.fullchain.pem",
        "ssl/private/cloud.smartsecurity.solutions.privkey.pem",
        "ssl/certs/admin.smartsecurity.solutions.fullchain.pem",
        "ssl/private/admin.smartsecurity.solutions.privkey.pem"
    ]
    
    all_exist = True
    for cert_file in cert_files:
        try:
            with open(cert_file, 'r') as f:
                content = f.read()
                if "BEGIN CERTIFICATE" in content or "BEGIN PRIVATE KEY" in content:
                    print_status(f"✅ {cert_file} exists and appears valid", "SUCCESS")
                else:
                    print_status(f"⚠️  {cert_file} exists but content seems invalid", "WARNING")
                    all_exist = False
        except FileNotFoundError:
            print_status(f"❌ {cert_file} not found", "ERROR")
            all_exist = False
        except Exception as e:
            print_status(f"❌ Error reading {cert_file}: {e}", "ERROR")
            all_exist = False
    
    return all_exist

def check_docker_containers():
    """Check if Docker containers are running"""
    print_status("Checking Docker containers...")
    
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, check=True)
        output = result.stdout
        
        containers = ['nginx', 'api', 'frontend_cloud', 'frontend_admin', 'db', 'redis', 'broker', 'worker']
        running_containers = []
        
        for line in output.split('\n'):
            for container in containers:
                if container in line and 'Up' in line:
                    running_containers.append(container)
        
        for container in containers:
            if container in running_containers:
                print_status(f"✅ {container} container is running", "SUCCESS")
            else:
                print_status(f"❌ {container} container is not running", "ERROR")
        
        return len(running_containers) == len(containers)
    except subprocess.CalledProcessError as e:
        print_status(f"❌ Error checking Docker containers: {e}", "ERROR")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print_status("Testing API endpoints...")
    
    api_urls = [
        "https://cloud.smartsecurity.solutions/api/v1/health",
        "https://admin.smartsecurity.solutions/api/v1/health"
    ]
    
    all_working = True
    for url in api_urls:
        try:
            response = requests.get(url, timeout=10, verify=True)
            if response.status_code == 200:
                print_status(f"✅ {url} is working", "SUCCESS")
            else:
                print_status(f"⚠️  {url} returned status {response.status_code}", "WARNING")
                all_working = False
        except requests.exceptions.RequestException as e:
            print_status(f"❌ {url} failed: {e}", "ERROR")
            all_working = False
    
    return all_working

def main():
    """Main test function"""
    print_status("🔒 Starting HTTPS Setup Test for Smart Security Cloud", "INFO")
    print_status("=" * 60, "INFO")
    
    # Test 1: Check SSL certificates
    certs_ok = check_ssl_certificates()
    print()
    
    # Test 2: Check Docker containers
    containers_ok = check_docker_containers()
    print()
    
    # Test 3: Test domain accessibility
    print_status("Testing domain accessibility...")
    domains = ['cloud.smartsecurity.solutions', 'admin.smartsecurity.solutions']
    
    https_ok = True
    redirect_ok = True
    
    for domain in domains:
        print_status(f"Testing {domain}...")
        if not test_domain_https(domain):
            https_ok = False
        if not test_domain_http_redirect(domain):
            redirect_ok = False
        print()
    
    # Test 4: Test API endpoints
    api_ok = test_api_endpoints()
    print()
    
    # Summary
    print_status("=" * 60, "INFO")
    print_status("📊 TEST SUMMARY", "INFO")
    print_status("=" * 60, "INFO")
    
    tests = [
        ("SSL Certificates", certs_ok),
        ("Docker Containers", containers_ok),
        ("HTTPS Accessibility", https_ok),
        ("HTTP to HTTPS Redirects", redirect_ok),
        ("API Endpoints", api_ok)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        color = "SUCCESS" if passed else "ERROR"
        print_status(f"{test_name}: {status}", color)
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print_status("🎉 All tests passed! Your HTTPS setup is working correctly.", "SUCCESS")
        print_status("Your domains are now secure and accessible via HTTPS:", "INFO")
        print_status("  - https://cloud.smartsecurity.solutions", "INFO")
        print_status("  - https://admin.smartsecurity.solutions", "INFO")
    else:
        print_status("⚠️  Some tests failed. Please check the issues above.", "WARNING")
        print_status("You may need to run the setup_ssl_certificates.sh script again.", "INFO")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 