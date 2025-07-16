#!/usr/bin/env python3
"""
VPS HTTPS Test for SmartSecurity Cloud

This script should be run on the VPS after deployment to verify:
1. HTTPS connectivity
2. SSL certificate validity
3. Security headers
4. HTTP to HTTPS redirects
5. API endpoints
"""

import os
import sys
import subprocess
import time
import requests
import ssl
import socket
from datetime import datetime

def test_https_connectivity():
    """Test HTTPS connectivity to both domains."""
    print("🔒 Testing HTTPS Connectivity")
    print("=" * 50)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    results = {}
    
    for domain in domains:
        print(f"\nTesting {domain}...")
        
        try:
            # Test HTTPS connection
            response = requests.get(f"https://{domain}", timeout=10)
            print(f"✅ HTTPS connection successful (Status: {response.status_code})")
            
            # Check for security headers
            security_headers = {
                'Strict-Transport-Security': 'HSTS',
                'X-Frame-Options': 'Clickjacking Protection',
                'X-Content-Type-Options': 'MIME Sniffing Protection',
                'X-XSS-Protection': 'XSS Protection',
                'Content-Security-Policy': 'CSP',
                'Referrer-Policy': 'Referrer Policy',
                'Permissions-Policy': 'Permissions Policy'
            }
            
            print("Security headers:")
            for header, description in security_headers.items():
                if header in response.headers:
                    print(f"  ✅ {description}: {response.headers[header]}")
                else:
                    print(f"  ⚠️  {description}: Missing")
            
            results[domain] = True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTPS connection failed: {e}")
            results[domain] = False
    
    return results

def test_ssl_certificates():
    """Test SSL certificate validity."""
    print("\n🔐 Testing SSL Certificates")
    print("=" * 50)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    results = {}
    
    for domain in domains:
        print(f"\nTesting SSL certificate for {domain}...")
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to the server
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    print(f"✅ SSL connection successful")
                    print(f"✅ SSL certificate valid")
                    results[domain] = True
                        
        except Exception as e:
            print(f"❌ SSL certificate test failed: {e}")
            results[domain] = False
    
    return results

def test_http_redirects():
    """Test HTTP to HTTPS redirects."""
    print("\n🔄 Testing HTTP to HTTPS Redirects")
    print("=" * 50)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    results = {}
    
    for domain in domains:
        print(f"\nTesting redirect from http://{domain}...")
        
        try:
            response = requests.get(f"http://{domain}", allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302]:
                print(f"✅ Redirect successful (Status: {response.status_code})")
                print(f"   Redirects to: {response.headers.get('Location', 'Unknown')}")
                
                # Check if redirect goes to HTTPS
                location = response.headers.get('Location', '')
                if location.startswith('https://'):
                    print(f"   ✅ Redirects to HTTPS")
                    results[domain] = True
                else:
                    print(f"   ❌ Does not redirect to HTTPS")
                    results[domain] = False
            else:
                print(f"❌ No redirect (Status: {response.status_code})")
                results[domain] = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Redirect test failed: {e}")
            results[domain] = False
    
    return results

def test_api_endpoints():
    """Test API endpoints over HTTPS."""
    print("\n🔌 Testing API Endpoints")
    print("=" * 50)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    api_endpoints = [
        "/api/v1/health",
        "/api/v1/status",
        "/health",
        "/status"
    ]
    
    results = {}
    
    for domain in domains:
        print(f"\nTesting API endpoints for {domain}...")
        domain_results = {}
        
        for endpoint in api_endpoints:
            url = f"https://{domain}{endpoint}"
            print(f"  Testing {url}...")
            
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"    ✅ Accessible (Status: {response.status_code})")
                    domain_results[endpoint] = True
                else:
                    print(f"    ⚠️  Returns status: {response.status_code}")
                    domain_results[endpoint] = False
                    
            except requests.exceptions.RequestException as e:
                print(f"    ❌ Failed: {e}")
                domain_results[endpoint] = False
        
        results[domain] = domain_results
    
    return results

def test_docker_containers():
    """Test if Docker containers are running."""
    print("\n🐳 Testing Docker Containers")
    print("=" * 50)
    
    try:
        # Check if docker-compose is running
        result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Docker Compose containers:")
            print(result.stdout)
            
            # Check if all expected services are running
            services = ["nginx", "customer-portal", "admin-console"]
            running_services = []
            
            for service in services:
                if service in result.stdout and "Up" in result.stdout:
                    print(f"  ✅ {service} is running")
                    running_services.append(service)
                else:
                    print(f"  ❌ {service} is not running")
            
            return len(running_services) == len(services)
        else:
            print(f"❌ Docker Compose check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Docker container test failed: {e}")
        return False

def test_ssl_labs_grade():
    """Test SSL Labs grade (if available)."""
    print("\n🏆 Testing SSL Labs Grade")
    print("=" * 50)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    for domain in domains:
        print(f"\nTesting SSL Labs grade for {domain}...")
        print("Note: This requires the domain to be publicly accessible")
        print(f"Check manually at: https://www.ssllabs.com/ssltest/analyze.html?d={domain}")
        print("Expected grade: A or A+")

def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n📊 HTTPS Test Report")
    print("=" * 50)
    
    report = f"""
SmartSecurity Cloud HTTPS Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Test Results:
"""
    
    # HTTPS Connectivity
    report += "\nHTTPS Connectivity:\n"
    for domain, success in results.get('https_connectivity', {}).items():
        status = "✅ PASS" if success else "❌ FAIL"
        report += f"  {status} {domain}\n"
    
    # SSL Certificates
    report += "\nSSL Certificates:\n"
    for domain, success in results.get('ssl_certificates', {}).items():
        status = "✅ PASS" if success else "❌ FAIL"
        report += f"  {status} {domain}\n"
    
    # HTTP Redirects
    report += "\nHTTP to HTTPS Redirects:\n"
    for domain, success in results.get('http_redirects', {}).items():
        status = "✅ PASS" if success else "❌ FAIL"
        report += f"  {status} {domain}\n"
    
    # Docker Containers
    docker_ok = results.get('docker_containers', False)
    report += f"\nDocker Containers: {'✅ PASS' if docker_ok else '❌ FAIL'}\n"
    
    # Overall result
    all_tests = []
    all_tests.extend(results.get('https_connectivity', {}).values())
    all_tests.extend(results.get('ssl_certificates', {}).values())
    all_tests.extend(results.get('http_redirects', {}).values())
    all_tests.append(results.get('docker_containers', False))
    
    passed = sum(all_tests)
    total = len(all_tests)
    
    report += f"\nOverall Result: {passed}/{total} tests passed\n"
    
    if passed == total:
        report += "\n🎉 All tests passed! HTTPS setup is working correctly.\n"
        report += "✅ Production ready!\n"
    else:
        report += "\n⚠️  Some tests failed. Please check configuration.\n"
    
    print(report)
    
    # Save report to file
    with open("https_test_report.txt", "w") as f:
        f.write(report)
    
    print("✅ Test report saved to https_test_report.txt")
    
    return passed == total

def main():
    """Main test function."""
    print("🔐 SmartSecurity Cloud VPS HTTPS Test")
    print("=" * 50)
    
    results = {}
    
    # Test HTTPS connectivity
    results['https_connectivity'] = test_https_connectivity()
    
    # Test SSL certificates
    results['ssl_certificates'] = test_ssl_certificates()
    
    # Test HTTP redirects
    results['http_redirects'] = test_http_redirects()
    
    # Test API endpoints
    results['api_endpoints'] = test_api_endpoints()
    
    # Test Docker containers
    results['docker_containers'] = test_docker_containers()
    
    # Test SSL Labs grade (informational)
    test_ssl_labs_grade()
    
    # Generate report
    success = generate_test_report(results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 