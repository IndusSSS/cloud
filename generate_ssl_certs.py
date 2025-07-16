#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for development.

This script creates self-signed certificates for:
- cloud.smartsecurity.solutions
- admin.smartsecurity.solutions

For production, use Let's Encrypt or a proper CA.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def generate_certificate(domain, cert_path, key_path):
    """Generate a self-signed certificate for a domain."""
    print(f"\n🔐 Generating SSL certificate for {domain}")
    
    # Create certificate directory if it doesn't exist
    os.makedirs(os.path.dirname(cert_path), exist_ok=True)
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    
    # Generate private key
    key_cmd = f'openssl genrsa -out "{key_path}" 2048'
    if not run_command(key_cmd, f"Generating private key for {domain}"):
        return False
    
    # Create certificate signing request
    csr_path = f"ssl/{domain}.csr"
    csr_cmd = f'''openssl req -new -key "{key_path}" -out "{csr_path}" -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN={domain}"'''
    if not run_command(csr_cmd, f"Creating CSR for {domain}"):
        return False
    
    # Generate self-signed certificate
    cert_cmd = f'''openssl x509 -req -in "{csr_path}" -signkey "{key_path}" -out "{cert_path}" -days 365 -extensions v3_req -extfile <(echo -e "[v3_req]\nsubjectAltName=DNS:{domain}")'''
    if not run_command(cert_cmd, f"Generating certificate for {domain}"):
        return False
    
    # Clean up CSR
    if os.path.exists(csr_path):
        os.remove(csr_path)
    
    print(f"✅ SSL certificate for {domain} generated successfully")
    return True

def main():
    """Main function to generate all certificates."""
    print("🔐 SmartSecurity SSL Certificate Generator")
    print("=" * 50)
    
    # Check if OpenSSL is available
    try:
        subprocess.run(['openssl', 'version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL is not installed or not in PATH")
        print("Please install OpenSSL and try again")
        sys.exit(1)
    
    # Define domains and paths
    domains = [
        {
            'domain': 'cloud.smartsecurity.solutions',
            'cert_path': 'ssl/certs/cloud.smartsecurity.solutions.crt',
            'key_path': 'ssl/private/cloud.smartsecurity.solutions.key'
        },
        {
            'domain': 'admin.smartsecurity.solutions',
            'cert_path': 'ssl/certs/admin.smartsecurity.solutions.crt',
            'key_path': 'ssl/private/admin.smartsecurity.solutions.key'
        }
    ]
    
    # Generate certificates for each domain
    success_count = 0
    for domain_info in domains:
        if generate_certificate(
            domain_info['domain'],
            domain_info['cert_path'],
            domain_info['key_path']
        ):
            success_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Successfully generated {success_count}/{len(domains)} certificates")
    
    if success_count == len(domains):
        print("\n🎉 All certificates generated successfully!")
        print("\n📝 Next steps:")
        print("1. Add the domains to your /etc/hosts file:")
        print("   127.0.0.1 cloud.smartsecurity.solutions")
        print("   127.0.0.1 admin.smartsecurity.solutions")
        print("2. Start the Docker containers: docker-compose up -d")
        print("3. Access the applications via HTTPS:")
        print("   - Cloud: https://cloud.smartsecurity.solutions")
        print("   - Admin: https://admin.smartsecurity.solutions")
        print("\n⚠️  Note: These are self-signed certificates for development only.")
        print("   For production, use Let's Encrypt or a proper CA.")
    else:
        print(f"\n❌ Failed to generate {len(domains) - success_count} certificates")
        sys.exit(1)

if __name__ == "__main__":
    main() 