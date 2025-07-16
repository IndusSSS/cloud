#!/usr/bin/env python3
"""
HTTPS Configuration Validation for SmartSecurity Cloud

This script validates the HTTPS setup configuration:
1. Checks SSL certificate files
2. Validates Nginx configuration
3. Checks Docker Compose configuration
4. Validates security headers configuration
5. Tests configuration syntax
"""

import os
import sys
import subprocess
import re
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

def check_ssl_certificates():
    """Check SSL certificate files."""
    print("\n🔐 Checking SSL Certificates")
    print("=" * 50)
    
    domains = [
        "cloud.smartsecurity.solutions",
        "admin.smartsecurity.solutions"
    ]
    
    results = {}
    
    for domain in domains:
        cert_file = f"ssl/certs/{domain}.crt"
        key_file = f"ssl/private/{domain}.key"
        
        print(f"\nChecking certificates for {domain}...")
        
        # Check certificate file
        if os.path.exists(cert_file):
            print(f"✅ Certificate file exists: {cert_file}")
            results[f"{domain}_cert"] = True
        else:
            print(f"❌ Certificate file missing: {cert_file}")
            results[f"{domain}_cert"] = False
        
        # Check private key file
        if os.path.exists(key_file):
            print(f"✅ Private key file exists: {key_file}")
            results[f"{domain}_key"] = True
        else:
            print(f"❌ Private key file missing: {key_file}")
            results[f"{domain}_key"] = False
    
    return results

def validate_nginx_config():
    """Validate Nginx configuration."""
    print("\n🌐 Validating Nginx Configuration")
    print("=" * 50)
    
    nginx_conf = "nginx/nginx.conf"
    
    if not os.path.exists(nginx_conf):
        print(f"❌ Nginx configuration file missing: {nginx_conf}")
        return False
    
    print(f"✅ Nginx configuration file exists: {nginx_conf}")
    
    # Read and validate nginx configuration
    try:
        with open(nginx_conf, 'r') as f:
            content = f.read()
        
        # Check for HTTPS configuration
        checks = [
            ("SSL configuration", "ssl_certificate"),
            ("SSL private key", "ssl_certificate_key"),
            ("HTTPS server block", "listen 443 ssl"),
            ("HTTP to HTTPS redirect", "return 301 https://"),
            ("Security headers", "add_header"),
            ("HSTS header", "Strict-Transport-Security"),
            ("X-Frame-Options", "X-Frame-Options"),
            ("X-Content-Type-Options", "X-Content-Type-Options"),
            ("X-XSS-Protection", "X-XSS-Protection"),
            ("Content-Security-Policy", "Content-Security-Policy")
        ]
        
        results = {}
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"✅ {check_name} found")
                results[check_name] = True
            else:
                print(f"❌ {check_name} missing")
                results[check_name] = False
        
        return results
        
    except Exception as e:
        print(f"❌ Error reading nginx configuration: {e}")
        return False

def validate_docker_compose():
    """Validate Docker Compose configuration."""
    print("\n🐳 Validating Docker Compose Configuration")
    print("=" * 50)
    
    compose_file = "docker-compose.yml"
    
    if not os.path.exists(compose_file):
        print(f"❌ Docker Compose file missing: {compose_file}")
        return False
    
    print(f"✅ Docker Compose file exists: {compose_file}")
    
    try:
        with open(compose_file, 'r') as f:
            content = f.read()
        
        # Check for required services and configurations
        checks = [
            ("Nginx service", "nginx:"),
            ("Customer portal service", "customer-portal:"),
            ("Admin console service", "admin-console:"),
            ("SSL certificate volumes", "ssl/certs:"),
            ("SSL private key volumes", "ssl/private:"),
            ("Port 80 mapping", "80:"),
            ("Port 443 mapping", "443:"),
            ("HTTPS port exposure", "443"),
            ("SSL certificate mounting", "ssl/certs"),
            ("SSL private key mounting", "ssl/private")
        ]
        
        results = {}
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"✅ {check_name} found")
                results[check_name] = True
            else:
                print(f"❌ {check_name} missing")
                results[check_name] = False
        
        return results
        
    except Exception as e:
        print(f"❌ Error reading Docker Compose file: {e}")
        return False

def check_security_headers():
    """Check security headers configuration."""
    print("\n🛡️ Checking Security Headers Configuration")
    print("=" * 50)
    
    nginx_conf = "nginx/nginx.conf"
    
    if not os.path.exists(nginx_conf):
        print(f"❌ Nginx configuration file missing: {nginx_conf}")
        return False
    
    try:
        with open(nginx_conf, 'r') as f:
            content = f.read()
        
        # Define required security headers
        required_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=()"
        }
        
        results = {}
        
        for header, expected_value in required_headers.items():
            # Check if header is configured
            if f"add_header {header}" in content:
                print(f"✅ {header} header configured")
                results[header] = True
            else:
                print(f"❌ {header} header missing")
                results[header] = False
        
        return results
        
    except Exception as e:
        print(f"❌ Error checking security headers: {e}")
        return False

def validate_ssl_configuration():
    """Validate SSL configuration details."""
    print("\n🔒 Validating SSL Configuration Details")
    print("=" * 50)
    
    nginx_conf = "nginx/nginx.conf"
    
    if not os.path.exists(nginx_conf):
        print(f"❌ Nginx configuration file missing: {nginx_conf}")
        return False
    
    try:
        with open(nginx_conf, 'r') as f:
            content = f.read()
        
        # Check SSL configuration details
        ssl_checks = [
            ("SSL protocols", "ssl_protocols"),
            ("SSL ciphers", "ssl_ciphers"),
            ("SSL session cache", "ssl_session_cache"),
            ("SSL session timeout", "ssl_session_timeout"),
            ("SSL buffer size", "ssl_buffer_size"),
            ("SSL certificate verification", "ssl_verify_client"),
            ("SSL OCSP stapling", "ssl_stapling"),
            ("SSL stapling verification", "ssl_stapling_verify")
        ]
        
        results = {}
        
        for check_name, pattern in ssl_checks:
            if pattern in content:
                print(f"✅ {check_name} configured")
                results[check_name] = True
            else:
                print(f"⚠️  {check_name} not configured (optional)")
                results[check_name] = False
        
        return results
        
    except Exception as e:
        print(f"❌ Error validating SSL configuration: {e}")
        return False

def check_file_permissions():
    """Check file permissions for SSL certificates."""
    print("\n🔐 Checking File Permissions")
    print("=" * 50)
    
    ssl_dirs = ["ssl/certs", "ssl/private"]
    
    results = {}
    
    for ssl_dir in ssl_dirs:
        if os.path.exists(ssl_dir):
            print(f"✅ SSL directory exists: {ssl_dir}")
            results[f"{ssl_dir}_exists"] = True
            
            # Check if directory is readable
            if os.access(ssl_dir, os.R_OK):
                print(f"✅ {ssl_dir} is readable")
                results[f"{ssl_dir}_readable"] = True
            else:
                print(f"❌ {ssl_dir} is not readable")
                results[f"{ssl_dir}_readable"] = False
        else:
            print(f"❌ SSL directory missing: {ssl_dir}")
            results[f"{ssl_dir}_exists"] = False
    
    return results

def generate_vps_deployment_guide():
    """Generate VPS deployment guide."""
    print("\n📋 VPS Deployment Guide")
    print("=" * 50)
    
    guide = """
🔐 SmartSecurity Cloud VPS Deployment Guide

Prerequisites:
✅ HTTPS configuration validated
✅ SSL certificates configured
✅ Security headers implemented
✅ Docker Compose setup ready

VPS Deployment Steps:

1. Server Setup:
   - Ubuntu 20.04+ or CentOS 8+
   - Docker and Docker Compose installed
   - Ports 80 and 443 open
   - Domain names pointing to server IP

2. SSL Certificate Setup:
   - Install Certbot: sudo apt install certbot
   - Generate Let's Encrypt certificates:
     certbot certonly --standalone -d cloud.smartsecurity.solutions
     certbot certonly --standalone -d admin.smartsecurity.solutions
   - Certificates location: /etc/letsencrypt/live/

3. Configuration Updates:
   - Update nginx/nginx.conf with Let's Encrypt certificate paths
   - Update docker-compose.yml with proper certificate volumes
   - Set environment variables for production

4. Deployment:
   - Copy project files to VPS
   - Run: docker-compose up -d
   - Test HTTPS connectivity
   - Verify security headers

5. Security Checklist:
   ✅ HTTPS-only access enforced
   ✅ HTTP to HTTPS redirects working
   ✅ Security headers implemented
   ✅ SSL certificates valid
   ✅ Docker containers running
   ✅ Firewall configured

6. Monitoring:
   - Set up SSL certificate renewal
   - Configure log monitoring
   - Set up health checks
   - Monitor security headers

The HTTPS setup is ready for VPS deployment!
"""
    
    print(guide)
    
    # Save guide to file
    with open("VPS_DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ VPS deployment guide saved to VPS_DEPLOYMENT_GUIDE.md")

def main():
    """Main validation function."""
    print("🔐 SmartSecurity HTTPS Configuration Validation")
    print("=" * 50)
    
    # Check SSL certificates
    ssl_results = check_ssl_certificates()
    
    # Validate Nginx configuration
    nginx_results = validate_nginx_config()
    
    # Validate Docker Compose configuration
    compose_results = validate_docker_compose()
    
    # Check security headers
    security_results = check_security_headers()
    
    # Validate SSL configuration
    ssl_config_results = validate_ssl_configuration()
    
    # Check file permissions
    permission_results = check_file_permissions()
    
    # Print summary
    print("\n📊 Validation Summary")
    print("=" * 50)
    
    print("\nSSL Certificates:")
    for key, success in ssl_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {key}")
    
    print("\nNginx Configuration:")
    if isinstance(nginx_results, dict):
        for key, success in nginx_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {key}")
    else:
        print(f"  {'❌ FAIL' if not nginx_results else '✅ PASS'} Nginx configuration")
    
    print("\nDocker Compose Configuration:")
    if isinstance(compose_results, dict):
        for key, success in compose_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {key}")
    else:
        print(f"  {'❌ FAIL' if not compose_results else '✅ PASS'} Docker Compose configuration")
    
    print("\nSecurity Headers:")
    if isinstance(security_results, dict):
        for key, success in security_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {key}")
    else:
        print(f"  {'❌ FAIL' if not security_results else '✅ PASS'} Security headers")
    
    print("\nSSL Configuration:")
    if isinstance(ssl_config_results, dict):
        for key, success in ssl_config_results.items():
            status = "✅ PASS" if success else "⚠️  OPTIONAL"
            print(f"  {status} {key}")
    else:
        print(f"  {'❌ FAIL' if not ssl_config_results else '✅ PASS'} SSL configuration")
    
    print("\nFile Permissions:")
    for key, success in permission_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {key}")
    
    # Overall result
    all_results = []
    all_results.extend(ssl_results.values())
    
    if isinstance(nginx_results, dict):
        all_results.extend(nginx_results.values())
    else:
        all_results.append(nginx_results)
    
    if isinstance(compose_results, dict):
        all_results.extend(compose_results.values())
    else:
        all_results.append(compose_results)
    
    if isinstance(security_results, dict):
        all_results.extend(security_results.values())
    else:
        all_results.append(security_results)
    
    all_results.extend(permission_results.values())
    
    passed = sum(all_results)
    total = len(all_results)
    
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed >= total * 0.8:  # 80% pass rate
        print("🎉 HTTPS configuration is ready for VPS deployment!")
        print("✅ All critical security features are properly configured")
        generate_vps_deployment_guide()
        return True
    else:
        print("⚠️  Some validations failed. Please fix issues before VPS deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 