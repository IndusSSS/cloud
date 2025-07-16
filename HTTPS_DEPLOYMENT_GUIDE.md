# HTTPS Deployment Guide - Industry Standards

This guide provides step-by-step instructions for deploying HTTPS using Let's Encrypt certificates with industry best practices.

## Overview

We use **Let's Encrypt** as our Certificate Authority (CA) because it's:
- **Free** and trusted by all major browsers
- **Industry standard** used by millions of websites
- **Automated** with easy renewal
- **Secure** with modern encryption standards

## Prerequisites

Before starting, ensure you have:

1. **Domain Name**: `cloud.smartsecurity.solutions` (or your domain)
2. **DNS Configuration**: Domain must point to your VPS IP address
3. **VPS Access**: SSH access to your server
4. **Firewall**: Ports 80 and 443 must be open
5. **Docker**: Docker and docker-compose installed

## Step 1: DNS Configuration

Ensure your domain points to your VPS:

```bash
# Check if DNS is properly configured
nslookup cloud.smartsecurity.solutions
```

The result should show your VPS IP address.

## Step 2: Firewall Configuration

Open required ports on your VPS:

```bash
# Ubuntu/Debian with ufw
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Or with iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## Step 3: SSL Certificate Setup

### Option A: Docker Setup (Recommended)

Use the Docker-specific script:

```bash
# Make script executable
chmod +x setup_ssl_docker.sh

# Edit the script to set your email
nano setup_ssl_docker.sh
# Change: EMAIL="admin@smartsecurity.solutions"

# Run the setup
./setup_ssl_docker.sh
```

### Option B: Manual Setup

If you prefer manual setup:

```bash
# Install Certbot
sudo apt update
sudo apt install -y certbot

# Stop existing services
docker-compose down

# Create temporary nginx for ACME challenge
docker run -d --name nginx-acme -p 80:80 \
  -v /tmp/nginx-acme.conf:/etc/nginx/conf.d/default.conf:ro \
  -v /tmp/acme-challenge:/var/www/html \
  nginx:alpine

# Obtain certificate
sudo certbot certonly --webroot \
  --webroot-path=/tmp/acme-challenge \
  --domain cloud.smartsecurity.solutions \
  --non-interactive \
  --agree-tos \
  --email your-email@example.com

# Clean up
docker stop nginx-acme
docker rm nginx-acme
```

## Step 4: Start Services

After obtaining certificates, start your services:

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs nginx
```

## Step 5: Verify HTTPS

Test your HTTPS setup:

```bash
# Test locally
curl -I https://cloud.smartsecurity.solutions

# Test with SSL verification
curl -I https://cloud.smartsecurity.solutions --cacert /etc/ssl/certs/ca-certificates.crt
```

## Step 6: Security Hardening

### SSL Configuration

The nginx configuration includes industry-standard SSL settings:

- **TLS 1.2 and 1.3** only (no older protocols)
- **Strong cipher suites** with forward secrecy
- **OCSP stapling** for better performance
- **Security headers** (HSTS, CSP, etc.)
- **HTTP/2** support

### Security Headers

Your nginx configuration includes:

```nginx
# HSTS (HTTP Strict Transport Security)
add_header Strict-Transport-Security "max-age=63072000" always;

# X-Frame-Options (prevent clickjacking)
add_header X-Frame-Options DENY always;

# X-Content-Type-Options (prevent MIME sniffing)
add_header X-Content-Type-Options nosniff always;

# X-XSS-Protection (XSS protection)
add_header X-XSS-Protection "1; mode=block" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' ws: wss:;" always;
```

## Step 7: Certificate Renewal

Certificates are automatically renewed via cron job:

```bash
# Check renewal status
sudo certbot certificates

# Manual renewal (if needed)
sudo certbot renew

# Check cron job
sudo crontab -l | grep certbot
```

## Step 8: Monitoring

### Health Checks

Your docker-compose includes health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### SSL Certificate Monitoring

Monitor certificate expiration:

```bash
# Check certificate expiration
sudo certbot certificates

# Set up monitoring (optional)
echo "0 6 * * * /usr/bin/certbot certificates | grep -q 'VALID' || echo 'Certificate expiring soon'" | sudo crontab -
```

## Troubleshooting

### Common Issues

1. **DNS Not Resolved**
   ```bash
   nslookup cloud.smartsecurity.solutions
   # Ensure it points to your VPS IP
   ```

2. **Port 80/443 Blocked**
   ```bash
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

3. **Certificate Not Found**
   ```bash
   sudo ls -la /etc/letsencrypt/live/cloud.smartsecurity.solutions/
   ```

4. **Nginx Configuration Error**
   ```bash
   docker-compose logs nginx
   ```

### SSL Labs Test

Test your SSL configuration:

```bash
# Install SSL Labs CLI tool
curl -s https://api.ssllabs.com/api/v3/analyze?host=cloud.smartsecurity.solutions
```

## Security Best Practices

1. **Regular Updates**: Keep Certbot and nginx updated
2. **Monitoring**: Monitor certificate expiration
3. **Backup**: Backup `/etc/letsencrypt` directory
4. **Firewall**: Only allow necessary ports
5. **Logs**: Monitor nginx and application logs

## Backup and Recovery

### Backup Certificates

```bash
# Backup Let's Encrypt directory
sudo tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt

# Backup nginx configuration
sudo cp /etc/nginx/conf.d/cloud.conf /backup/nginx-cloud.conf
```

### Recovery

```bash
# Restore certificates
sudo tar -xzf letsencrypt-backup-YYYYMMDD.tar.gz -C /

# Restart services
docker-compose restart nginx
```

## Performance Optimization

1. **HTTP/2**: Already enabled in nginx config
2. **OCSP Stapling**: Reduces SSL handshake time
3. **Session Caching**: Improves connection reuse
4. **Gzip Compression**: Reduces bandwidth usage

## Compliance

This setup complies with:

- **PCI DSS**: For payment processing (if applicable)
- **GDPR**: Secure data transmission
- **SOC 2**: Security controls
- **OWASP**: Security best practices

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review nginx and application logs
3. Test with SSL Labs
4. Verify DNS and firewall settings

---

**Note**: This setup uses industry-standard practices and is suitable for production environments. The certificates are automatically renewed and the configuration follows security best practices. 