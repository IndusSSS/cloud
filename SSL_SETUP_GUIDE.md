# SSL Certificate Setup Guide for Smart Security Cloud

This guide will help you set up SSL certificates for both `cloud.smartsecurity.solutions` and `admin.smartsecurity.solutions` domains.

## Prerequisites

- VPS with Docker and Docker Compose installed
- Domains pointing to your VPS IP address
- Root or sudo access
- Ports 80 and 443 open in firewall

## Quick Setup (Recommended)

### Step 1: Run the Automated Setup Script

```bash
# Make the script executable
chmod +x setup_ssl_certificates.sh

# Run the setup script
sudo ./setup_ssl_certificates.sh
```

This script will:
- Stop the nginx container
- Obtain SSL certificates from Let's Encrypt
- Copy certificates to the project directory
- Set proper permissions
- Start the nginx container
- Test the setup
- Set up automatic renewal

### Step 2: Verify the Setup

```bash
# Run the test script
python3 test_https_setup.py
```

## Manual Setup (Alternative)

If the automated script doesn't work, follow these manual steps:

### Step 1: Stop Services

```bash
# Stop nginx container to free up port 80
sudo docker-compose stop nginx

# Stop system nginx if running
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### Step 2: Create SSL Directories

```bash
# Create directories for SSL certificates
mkdir -p ssl/certs
mkdir -p ssl/private
```

### Step 3: Obtain SSL Certificates

```bash
# Get certificates using certbot standalone mode
sudo certbot certonly --standalone \
  -d admin.smartsecurity.solutions \
  -d cloud.smartsecurity.solutions \
  --non-interactive \
  --agree-tos \
  --email admin@smartsecurity.solutions
```

### Step 4: Copy Certificates

```bash
# Copy certificates to project directory
sudo cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/fullchain.pem ssl/certs/cloud.smartsecurity.solutions.fullchain.pem
sudo cp /etc/letsencrypt/live/cloud.smartsecurity.solutions/privkey.pem ssl/private/cloud.smartsecurity.solutions.privkey.pem
sudo cp /etc/letsencrypt/live/admin.smartsecurity.solutions/fullchain.pem ssl/certs/admin.smartsecurity.solutions.fullchain.pem
sudo cp /etc/letsencrypt/live/admin.smartsecurity.solutions/privkey.pem ssl/private/admin.smartsecurity.solutions.privkey.pem

# Set proper permissions
sudo chmod 644 ssl/certs/*
sudo chmod 600 ssl/private/*
sudo chown -R $USER:$USER ssl/
```

### Step 5: Start Services

```bash
# Start nginx container
sudo docker-compose start nginx

# Verify containers are running
sudo docker-compose ps
```

## Configuration Files Updated

The following files have been updated for SSL support:

### 1. docker-compose.yml
- Added port 443 mapping
- Added SSL certificate volume mounts
- Enabled frontend_admin service
- Updated nginx configuration path

### 2. nginx/conf.d/cloud.conf
- Enabled both domain configurations
- Updated SSL certificate paths
- Added HTTP to HTTPS redirects
- Enhanced security headers

## Testing Your Setup

### Test HTTPS Access

```bash
# Test cloud domain
curl -I https://cloud.smartsecurity.solutions

# Test admin domain
curl -I https://admin.smartsecurity.solutions
```

### Test HTTP Redirects

```bash
# Test HTTP to HTTPS redirect
curl -I http://cloud.smartsecurity.solutions
curl -I http://admin.smartsecurity.solutions
```

### Run Comprehensive Test

```bash
# Run the automated test script
python3 test_https_setup.py
```

## Troubleshooting

### Port 80 Already in Use

If you get "Address already in use" errors:

```bash
# Check what's using port 80
sudo netstat -tlnp | grep :80

# Stop conflicting services
sudo docker-compose stop nginx
sudo systemctl stop nginx
```

### Certificate Not Found

If certificates are not found:

```bash
# Check if certificates exist
sudo ls -la /etc/letsencrypt/live/

# Re-run certbot
sudo certbot certonly --standalone -d admin.smartsecurity.solutions -d cloud.smartsecurity.solutions
```

### Nginx Configuration Errors

If nginx fails to start:

```bash
# Check nginx configuration
sudo docker-compose logs nginx

# Test nginx configuration
sudo docker exec cloud-nginx-1 nginx -t
```

## Automatic Renewal

The setup script creates a cron job for automatic certificate renewal:

```bash
# Check renewal cron job
sudo cat /etc/cron.d/ssl-renewal

# Check renewal logs
sudo tail -f /var/log/ssl-renewal.log
```

## Security Features

Your setup includes:

- **HSTS (HTTP Strict Transport Security)**: Forces HTTPS connections
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **Modern SSL Configuration**: TLS 1.2/1.3 only
- **HTTP to HTTPS Redirects**: Automatic redirection
- **Certificate Auto-Renewal**: Automatic Let's Encrypt renewal

## Access Your Applications

After successful setup, you can access:

- **Customer Portal**: https://cloud.smartsecurity.solutions
- **Admin Console**: https://admin.smartsecurity.solutions

## Next Steps

1. **Create Admin User**: Use the admin creation script to set up your first admin user
2. **Configure DNS**: Ensure your domains point to your VPS IP
3. **Set Up Monitoring**: Consider setting up monitoring for certificate expiration
4. **Backup Certificates**: Regularly backup your SSL certificates

## Support

If you encounter issues:

1. Check the logs: `sudo docker-compose logs nginx`
2. Run the test script: `python3 test_https_setup.py`
3. Verify DNS settings for your domains
4. Check firewall settings for ports 80 and 443

## Files Created/Modified

- `setup_ssl_certificates.sh` - Automated SSL setup script
- `test_https_setup.py` - HTTPS testing script
- `renew_ssl_certificates.sh` - Certificate renewal script
- `docker-compose.yml` - Updated for SSL support
- `nginx/conf.d/cloud.conf` - Updated nginx configuration
- `ssl/certs/` - SSL certificate directory
- `ssl/private/` - SSL private key directory 