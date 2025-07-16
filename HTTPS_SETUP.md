# HTTPS-Only Setup for SmartSecurity Cloud

This document explains how to configure HTTPS-only access for the SmartSecurity Cloud platform, ensuring secure access to both the customer portal and admin console.

## 🎯 Overview

The SmartSecurity Cloud platform now enforces HTTPS-only access for:
- **Customer Portal**: `https://cloud.smartsecurity.solutions`
- **Admin Console**: `https://admin.smartsecurity.solutions`

All HTTP traffic is automatically redirected to HTTPS with proper security headers and SSL/TLS configuration.

## 🔐 Security Features

### SSL/TLS Configuration
- **Protocols**: TLSv1.2 and TLSv1.3 only
- **Ciphers**: Strong cipher suites with forward secrecy
- **Certificate**: Self-signed for development, Let's Encrypt for production
- **HSTS**: HTTP Strict Transport Security enabled
- **Security Headers**: Comprehensive security headers for protection

### Security Headers
- `Strict-Transport-Security`: Enforces HTTPS-only access
- `X-Frame-Options`: Prevents clickjacking attacks
- `X-Content-Type-Options`: Prevents MIME type sniffing
- `X-XSS-Protection`: XSS protection
- `Referrer-Policy`: Controls referrer information
- `Content-Security-Policy`: Content security policy
- `Permissions-Policy`: Controls browser features (admin only)

## 🚀 Quick Setup

### 1. Generate SSL Certificates

#### Option A: Using Makefile (Recommended)
```bash
make ssl-certs
```

#### Option B: Using Python Script
```bash
python generate_ssl_certs.py
```

#### Option C: Using PowerShell Script (Windows)
```powershell
.\generate_ssl_certs.ps1
```

### 2. Configure Hosts File

Add the following entries to your hosts file:

**Linux/Mac** (`/etc/hosts`):
```
127.0.0.1 cloud.smartsecurity.solutions
127.0.0.1 admin.smartsecurity.solutions
```

**Windows** (`C:\Windows\System32\drivers\etc\hosts`):
```
127.0.0.1 cloud.smartsecurity.solutions
127.0.0.1 admin.smartsecurity.solutions
```

### 3. Start the Application

```bash
# Generate certificates and start Docker containers
make setup-https

# Or manually:
make ssl-certs
docker-compose up -d
```

### 4. Access the Applications

- **Customer Portal**: https://cloud.smartsecurity.solutions
- **Admin Console**: https://admin.smartsecurity.solutions

## 📁 File Structure

```
ssl/
├── certs/
│   ├── cloud.smartsecurity.solutions.crt
│   └── admin.smartsecurity.solutions.crt
└── private/
    ├── cloud.smartsecurity.solutions.key
    └── admin.smartsecurity.solutions.key
```

## 🔧 Configuration Details

### Nginx Configuration

The Nginx configuration (`nginx/conf.d/cloud.conf`) includes:

1. **HTTP to HTTPS Redirects**
   - All HTTP traffic (port 80) is redirected to HTTPS (port 443)
   - 301 permanent redirects for SEO and caching

2. **SSL Server Blocks**
   - Separate SSL configurations for each domain
   - Strong cipher suites and security settings
   - HTTP/2 support enabled

3. **Security Headers**
   - Comprehensive security headers for both domains
   - Enhanced headers for admin console

4. **Proxy Configuration**
   - Proper forwarding of HTTPS headers
   - WebSocket support over HTTPS

### Docker Compose Configuration

The `docker-compose.yml` includes:

1. **SSL Certificate Volumes**
   - Mounts SSL certificates and private keys
   - Support for Let's Encrypt certificates
   - Read-only access for security

2. **Port Configuration**
   - Port 80: HTTP redirects only
   - Port 443: HTTPS traffic

## 🛠️ Development vs Production

### Development Environment
- **Certificates**: Self-signed certificates
- **Domains**: Local development domains
- **Setup**: Automated with Makefile targets

### Production Environment
- **Certificates**: Let's Encrypt or commercial CA
- **Domains**: Real domain names
- **Setup**: Manual certificate installation

## 🔍 Troubleshooting

### Common Issues

1. **Certificate Warnings**
   - Self-signed certificates will show browser warnings
   - Click "Advanced" and "Proceed" for development
   - Use proper CA certificates for production

2. **Hosts File Issues**
   - Ensure hosts file entries are correct
   - Clear DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)

3. **Port Conflicts**
   - Ensure ports 80 and 443 are available
   - Stop other web servers (Apache, IIS, etc.)

4. **Docker Issues**
   - Restart Docker containers: `docker-compose down && docker-compose up -d`
   - Check container logs: `docker-compose logs nginx`

### Verification Commands

```bash
# Check SSL certificate
openssl s_client -connect cloud.smartsecurity.solutions:443 -servername cloud.smartsecurity.solutions

# Test HTTPS redirect
curl -I http://cloud.smartsecurity.solutions

# Verify security headers
curl -I https://cloud.smartsecurity.solutions
```

## 🔒 Security Best Practices

1. **Certificate Management**
   - Use strong private keys (2048-bit minimum)
   - Regular certificate renewal
   - Secure private key storage

2. **Configuration Security**
   - Disable weak SSL protocols
   - Use strong cipher suites
   - Enable security headers

3. **Monitoring**
   - Monitor certificate expiration
   - Check security headers
   - Regular security audits

## 📚 Additional Resources

- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)

## 🆘 Support

For issues with HTTPS setup:

1. Check the troubleshooting section above
2. Review Docker container logs
3. Verify SSL certificate validity
4. Test with different browsers
5. Check firewall and network settings

---

**Note**: This setup provides HTTPS-only access for development and production environments. For production deployment, always use proper SSL certificates from a trusted Certificate Authority. 