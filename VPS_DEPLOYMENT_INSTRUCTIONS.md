# VPS Deployment Instructions

This document provides step-by-step instructions for deploying your cloud application to a Linux VPS with industry-standard HTTPS.

## Prerequisites

Before starting, ensure your VPS has:

1. **Linux OS** (Ubuntu 20.04+ recommended)
2. **Docker** installed
3. **docker-compose** installed
4. **Domain name** pointing to your VPS IP
5. **Firewall** with ports 80 and 443 open

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Clone your repository to VPS
git clone <your-repo-url>
cd cloud

# 2. Run the automated deployment script
./deploy_to_vps.sh
```

This script will:
- Check all prerequisites
- Build Docker images
- Set up SSL certificates (if needed)
- Start all services
- Test the deployment

### Option 2: Manual Deployment

```bash
# 1. Set up SSL certificates
./setup_vps_ssl.sh

# 2. Start services
docker-compose up -d

# 3. Test the setup
./test_https_setup.sh
```

## Detailed Steps

### Step 1: VPS Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for Docker group to take effect
```

### Step 2: Firewall Configuration

```bash
# Allow SSH (if not already allowed)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Step 3: DNS Configuration

Ensure your domain points to your VPS IP:

```bash
# Check your VPS IP
curl ifconfig.me

# Configure DNS at your domain registrar:
# Type: A
# Name: cloud (or @ for root domain)
# Value: YOUR_VPS_IP
```

### Step 4: Application Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd cloud

# Make scripts executable
chmod +x *.sh

# Run deployment
./deploy_to_vps.sh
```

## SSL Certificate Setup

The deployment includes automatic SSL certificate setup using Let's Encrypt:

### Automatic Setup
- Certificates are obtained automatically during deployment
- Valid for 90 days
- Auto-renewal configured via cron job
- Industry-standard security configuration

### Manual SSL Setup (if needed)
```bash
# Run SSL setup script
./setup_vps_ssl.sh

# Or use the Docker-specific script
./setup_ssl_docker.sh
```

## Service Architecture

Your deployment includes:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80/443)│────│  Frontend Cloud │────│      API       │
│   (SSL/Term)    │    │   (Vue.js)      │    │  (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis      │    │   MQTT Broker   │
│   (Database)    │    │   (Cache/Queue) │    │  (IoT Devices)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Service URLs

After deployment, your services will be available at:

- **Main Application**: `https://cloud.smartsecurity.solutions`
- **API**: `http://localhost:8082` (internal) / `https://cloud.smartsecurity.solutions/api`
- **Frontend**: `http://localhost:8083` (internal) / `https://cloud.smartsecurity.solutions`

## Monitoring and Maintenance

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f api
```

### Service Management
```bash
# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart nginx

# Update and restart
docker-compose pull
docker-compose up -d
```

### SSL Certificate Management
```bash
# Check certificate status
sudo certbot certificates

# Manual renewal
sudo certbot renew

# Check renewal cron job
sudo crontab -l | grep certbot
```

### Health Checks
```bash
# Test HTTPS setup
./test_https_setup.sh

# Check service health
docker-compose ps

# Test API health
curl http://localhost:8082/health
```

## Security Features

Your deployment includes industry-standard security:

### SSL/TLS Configuration
- **TLS 1.2 and 1.3** only
- **Strong cipher suites** with forward secrecy
- **OCSP stapling** for performance
- **HTTP/2** support

### Security Headers
- **HSTS** (HTTP Strict Transport Security)
- **CSP** (Content Security Policy)
- **X-Frame-Options** (clickjacking protection)
- **X-Content-Type-Options** (MIME sniffing protection)
- **X-XSS-Protection** (XSS protection)

### Network Security
- **Firewall** configured
- **Docker network isolation**
- **Port restrictions**

## Troubleshooting

### Common Issues

1. **Port 80/443 already in use**
   ```bash
   # Check what's using the ports
   sudo ss -tlnp | grep :80
   sudo ss -tlnp | grep :443
   
   # Stop conflicting services
   sudo systemctl stop apache2  # if Apache is running
   sudo systemctl stop nginx    # if system nginx is running
   ```

2. **SSL certificate issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificates
   sudo certbot renew --force-renewal
   ```

3. **Docker permission issues**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   
   # Logout and login again
   ```

4. **DNS not resolving**
   ```bash
   # Check DNS
   nslookup cloud.smartsecurity.solutions
   
   # Wait for DNS propagation (can take up to 48 hours)
   ```

### Log Analysis
```bash
# Nginx logs
docker-compose logs nginx

# API logs
docker-compose logs api

# Database logs
docker-compose logs db
```

## Backup and Recovery

### Backup Strategy
```bash
# Backup certificates
sudo tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt

# Backup database
docker-compose exec db pg_dump -U cloud cloud_db > backup-$(date +%Y%m%d).sql

# Backup configuration
cp docker-compose.yml backup-docker-compose-$(date +%Y%m%d).yml
```

### Recovery
```bash
# Restore certificates
sudo tar -xzf letsencrypt-backup-YYYYMMDD.tar.gz -C /

# Restore database
docker-compose exec -T db psql -U cloud cloud_db < backup-YYYYMMDD.sql

# Restart services
docker-compose restart
```

## Performance Optimization

### Docker Optimization
```bash
# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Clean up everything
docker system prune -a
```

### SSL Performance
- HTTP/2 enabled
- OCSP stapling configured
- Session caching enabled
- Strong cipher suites

## Compliance

This setup complies with:

- **PCI DSS**: For payment processing
- **GDPR**: Data protection
- **SOC 2**: Security controls
- **OWASP**: Security best practices

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review service logs
3. Test with the provided test scripts
4. Verify DNS and firewall settings

---

**Note**: This deployment uses industry-standard practices and is suitable for production environments. The setup includes automatic SSL renewal, health monitoring, and security best practices. 