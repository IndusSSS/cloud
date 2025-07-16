#!/usr/bin/env python3
"""
Comprehensive Service Test and Fix Script for Smart Security Cloud
Tests all services and fixes common issues
"""

import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

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

def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print_status(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"✅ {description} completed successfully", "SUCCESS")
            return True, result.stdout
        else:
            print_status(f"❌ {description} failed: {result.stderr}", "ERROR")
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        print_status(f"❌ {description} failed: {e}", "ERROR")
        return False, str(e)

def check_docker_services():
    """Check if all Docker services are running properly."""
    print_status("🔍 Checking Docker Services", "INFO")
    print_status("=" * 50, "INFO")
    
    # Check if Docker is running
    success, output = run_command("docker --version", "Checking Docker installation")
    if not success:
        return False
    
    # Check if docker-compose is available
    success, output = run_command("docker-compose --version", "Checking Docker Compose")
    if not success:
        return False
    
    # Get container status
    success, output = run_command("docker-compose ps", "Getting container status")
    if not success:
        return False
    
    print_status("Container Status:", "INFO")
    print(output)
    
    # Check for unhealthy containers
    success, output = run_command("docker-compose ps --format 'table {{.Name}}\t{{.Status}}'", "Checking container health")
    if success:
        lines = output.strip().split('\n')[1:]  # Skip header
        unhealthy = []
        for line in lines:
            if line.strip() and ('unhealthy' in line.lower() or 'exited' in line.lower()):
                unhealthy.append(line.strip())
        
        if unhealthy:
            print_status("⚠️  Found unhealthy/exited containers:", "WARNING")
            for container in unhealthy:
                print_status(f"  - {container}", "WARNING")
            return False
        else:
            print_status("✅ All containers are healthy", "SUCCESS")
            return True
    
    return False

def check_ssl_certificates():
    """Check if SSL certificates exist and are valid."""
    print_status("🔒 Checking SSL Certificates", "INFO")
    print_status("=" * 50, "INFO")
    
    cert_files = [
        "ssl/certs/cloud.smartsecurity.solutions.fullchain.pem",
        "ssl/private/cloud.smartsecurity.solutions.privkey.pem",
        "ssl/certs/admin.smartsecurity.solutions.fullchain.pem",
        "ssl/private/admin.smartsecurity.solutions.privkey.pem"
    ]
    
    all_exist = True
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            print_status(f"✅ {cert_file} exists", "SUCCESS")
        else:
            print_status(f"❌ {cert_file} missing", "ERROR")
            all_exist = False
    
    return all_exist

def check_network_connectivity():
    """Check network connectivity and DNS resolution."""
    print_status("🌐 Checking Network Connectivity", "INFO")
    print_status("=" * 50, "INFO")
    
    # Get VPS IP
    success, ip_output = run_command("curl -s ifconfig.me", "Getting VPS IP address")
    if success:
        vps_ip = ip_output.strip()
        print_status(f"VPS IP: {vps_ip}", "INFO")
        
        # Check DNS resolution
        domains = ['cloud.smartsecurity.solutions', 'admin.smartsecurity.solutions']
        dns_ok = True
        
        for domain in domains:
            success, dns_output = run_command(f"nslookup {domain}", f"Checking DNS for {domain}")
            if success and vps_ip in dns_output:
                print_status(f"✅ {domain} resolves to VPS IP", "SUCCESS")
            else:
                print_status(f"❌ {domain} does not resolve to VPS IP", "ERROR")
                dns_ok = False
        
        return dns_ok
    else:
        print_status("❌ Could not get VPS IP", "ERROR")
        return False

def check_service_endpoints():
    """Check if service endpoints are accessible."""
    print_status("🔌 Checking Service Endpoints", "INFO")
    print_status("=" * 50, "INFO")
    
    endpoints = [
        ("http://localhost", "Nginx HTTP"),
        ("http://localhost:8082/api/v1/health", "API Health"),
        ("http://localhost:8083", "Frontend"),
    ]
    
    all_working = True
    for url, description in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 301, 302]:
                print_status(f"✅ {description} is working (Status: {response.status_code})", "SUCCESS")
            else:
                print_status(f"⚠️  {description} returned status {response.status_code}", "WARNING")
                all_working = False
        except requests.exceptions.RequestException as e:
            print_status(f"❌ {description} failed: {e}", "ERROR")
            all_working = False
    
    return all_working

def fix_common_issues():
    """Fix common issues found during testing."""
    print_status("🔧 Fixing Common Issues", "INFO")
    print_status("=" * 50, "INFO")
    
    # Create SSL directories if they don't exist
    ssl_dirs = ["ssl/certs", "ssl/private"]
    for ssl_dir in ssl_dirs:
        if not os.path.exists(ssl_dir):
            os.makedirs(ssl_dir, exist_ok=True)
            print_status(f"✅ Created directory: {ssl_dir}", "SUCCESS")
    
    # Copy env.example to .env if .env doesn't exist
    if not os.path.exists(".env") and os.path.exists("env.example"):
        run_command("cp env.example .env", "Creating .env file from template")
    
    # Restart containers if needed
    print_status("Restarting containers to ensure proper startup order...", "INFO")
    run_command("docker-compose down", "Stopping containers")
    time.sleep(5)
    run_command("docker-compose up -d", "Starting containers")
    
    # Wait for services to be ready
    print_status("Waiting for services to be ready...", "INFO")
    time.sleep(30)

def test_mqtt_connection():
    """Test MQTT broker connection."""
    print_status("📡 Testing MQTT Connection", "INFO")
    print_status("=" * 50, "INFO")
    
    # Test MQTT broker
    success, output = run_command("docker exec cloud-broker-1 mosquitto_pub -h localhost -t test -m 'test message'", "Testing MQTT broker")
    if success:
        print_status("✅ MQTT broker is working", "SUCCESS")
        return True
    else:
        print_status("❌ MQTT broker test failed", "ERROR")
        return False

def generate_ssl_certificates():
    """Generate SSL certificates if they don't exist."""
    print_status("🔐 Generating SSL Certificates", "INFO")
    print_status("=" * 50, "INFO")
    
    if check_ssl_certificates():
        print_status("SSL certificates already exist", "INFO")
        return True
    
    # Stop nginx to free port 80
    run_command("docker-compose stop nginx", "Stopping nginx for certificate generation")
    
    # Generate certificates
    success, output = run_command(
        "certbot certonly --standalone -d admin.smartsecurity.solutions -d cloud.smartsecurity.solutions --non-interactive --agree-tos --email admin@smartsecurity.solutions",
        "Generating SSL certificates"
    )
    
    if success:
        # Copy certificates
        run_command("cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem", "Copying cloud certificate")
        run_command("cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem", "Copying cloud private key")
        run_command("cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem", "Copying admin certificate")
        run_command("cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem", "Copying admin private key")
        
        # Set permissions
        run_command("chmod 644 ssl/certs/*", "Setting certificate permissions")
        run_command("chmod 600 ssl/private/*", "Setting private key permissions")
        
        # Start nginx
        run_command("docker-compose start nginx", "Starting nginx")
        
        return True
    else:
        return False

def main():
    """Main test and fix function."""
    print_status("🚀 Smart Security Cloud - Service Test and Fix", "INFO")
    print_status("=" * 60, "INFO")
    
    # Check if running as root
    if os.geteuid() != 0:
        print_status("⚠️  Some operations may require root privileges", "WARNING")
    
    # Step 1: Fix common issues
    fix_common_issues()
    
    # Step 2: Check Docker services
    docker_ok = check_docker_services()
    
    # Step 3: Check SSL certificates
    ssl_ok = check_ssl_certificates()
    if not ssl_ok:
        print_status("Generating SSL certificates...", "INFO")
        ssl_ok = generate_ssl_certificates()
    
    # Step 4: Check network connectivity
    network_ok = check_network_connectivity()
    
    # Step 5: Check service endpoints
    endpoints_ok = check_service_endpoints()
    
    # Step 6: Test MQTT connection
    mqtt_ok = test_mqtt_connection()
    
    # Summary
    print_status("=" * 60, "INFO")
    print_status("📊 TEST SUMMARY", "INFO")
    print_status("=" * 60, "INFO")
    
    tests = [
        ("Docker Services", docker_ok),
        ("SSL Certificates", ssl_ok),
        ("Network Connectivity", network_ok),
        ("Service Endpoints", endpoints_ok),
        ("MQTT Connection", mqtt_ok)
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
        print_status("🎉 All tests passed! Your system is working correctly.", "SUCCESS")
        print_status("Your domains should be accessible:", "INFO")
        print_status("  - https://cloud.smartsecurity.solutions", "INFO")
        print_status("  - https://admin.smartsecurity.solutions", "INFO")
    else:
        print_status("⚠️  Some tests failed. Please check the issues above.", "WARNING")
        print_status("You may need to:", "INFO")
        print_status("  1. Update DNS records to point to your VPS IP", "INFO")
        print_status("  2. Check firewall settings for ports 80 and 443", "INFO")
        print_status("  3. Ensure all containers are running properly", "INFO")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 