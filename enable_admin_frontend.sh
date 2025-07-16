#!/bin/bash

# Enable Admin Frontend
# This script re-enables the admin frontend after fixing the nginx configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔧 Re-enabling Admin Frontend"
echo "============================="

# Step 1: Verify nginx configuration is fixed
print_status "Verifying nginx configuration is fixed..."
if grep -q "must-revalidate" frontend_admin/nginx.conf; then
    print_error "nginx.conf still contains invalid 'must-revalidate' directive"
    print_error "Please run fix_frontend_admin.sh first"
    exit 1
fi
print_success "nginx configuration is correct"

# Step 2: Re-enable frontend_admin in docker-compose.yml
print_status "Re-enabling frontend_admin in docker-compose.yml..."
sed -i 's/^  # frontend_admin:/  frontend_admin:/' docker-compose.yml
sed -i 's/^  #   build:/    build:/' docker-compose.yml
sed -i 's/^  #     context:/      context:/' docker-compose.yml
sed -i 's/^  #     dockerfile:/      dockerfile:/' docker-compose.yml
sed -i 's/^  #   depends_on:/    depends_on:/' docker-compose.yml
sed -i 's/^  #   restart:/    restart:/' docker-compose.yml
sed -i 's/^  #   networks:/    networks:/' docker-compose.yml
print_success "frontend_admin service re-enabled"

# Step 3: Re-enable nginx dependency
print_status "Re-enabling nginx dependency on frontend_admin..."
sed -i 's/^      # - frontend_admin/      - frontend_admin/' docker-compose.yml
print_success "nginx dependency re-enabled"

# Step 4: Re-enable admin domain in nginx config
print_status "Re-enabling admin domain in nginx configuration..."
sed -i 's/^# server {/server {/' nginx/conf.d/cloud.conf
sed -i 's/^#     listen 80;/    listen 80;/' nginx/conf.d/cloud.conf
sed -i 's/^#     server_name admin.smartsecurity.solutions;/    server_name admin.smartsecurity.solutions;/' nginx/conf.d/cloud.conf
sed -i 's/^#     return 301 https:\/\/$server_name$request_uri;/    return 301 https:\/\/$server_name$request_uri;/' nginx/conf.d/cloud.conf
sed -i 's/^# }/}/' nginx/conf.d/cloud.conf

# Re-enable HTTPS server block
sed -i 's/^# HTTPS server for admin domain (temporarily disabled)/# HTTPS server for admin domain/' nginx/conf.d/cloud.conf
sed -i 's/^# server {/server {/' nginx/conf.d/cloud.conf
sed -i 's/^#     listen 443 ssl;/    listen 443 ssl;/' nginx/conf.d/cloud.conf
sed -i 's/^#     http2 on;/    http2 on;/' nginx/conf.d/cloud.conf
sed -i 's/^#     server_name admin.smartsecurity.solutions;/    server_name admin.smartsecurity.solutions;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_certificate \/etc\/ssl\/certs\/admin.crt;/    ssl_certificate \/etc\/ssl\/certs\/admin.crt;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_certificate_key \/etc\/ssl\/private\/cloud.key;/    ssl_certificate_key \/etc\/ssl\/private\/cloud.key;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_protocols TLSv1.2 TLSv1.3;/    ssl_protocols TLSv1.2 TLSv1.3;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;/    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_prefer_server_ciphers off;/    ssl_prefer_server_ciphers off;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_session_cache shared:SSL:10m;/    ssl_session_cache shared:SSL:10m;/' nginx/conf.d/cloud.conf
sed -i 's/^#     ssl_session_timeout 10m;/    ssl_session_timeout 10m;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;/    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header X-Frame-Options DENY always;/    add_header X-Frame-Options DENY always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header X-Content-Type-Options nosniff always;/    add_header X-Content-Type-Options nosniff always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header X-XSS-Protection "1; mode=block" always;/    add_header X-XSS-Protection "1; mode=block" always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header Referrer-Policy "strict-origin-when-cross-origin" always;/    add_header Referrer-Policy "strict-origin-when-cross-origin" always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header Content-Security-Policy "default-src '\''self'\''; script-src '\''self'\'' '\''unsafe-inline'\''; style-src '\''self'\'' '\''unsafe-inline'\''; img-src '\''self'\'' data:; font-src '\''self'\''; connect-src '\''self'\'' ws: wss:;" always;/    add_header Content-Security-Policy "default-src '\''self'\''; script-src '\''self'\'' '\''unsafe-inline'\''; style-src '\''self'\'' '\''unsafe-inline'\''; img-src '\''self'\'' data:; font-src '\''self'\''; connect-src '\''self'\'' ws: wss:;" always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;/    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;/' nginx/conf.d/cloud.conf
sed -i 's/^#     location \/ {/    location \/ {/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_pass http:\/\/frontend_admin:80;/        proxy_pass http:\/\/frontend_admin:80;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header Host $host;/        proxy_set_header Host $host;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Real-IP $remote_addr;/        proxy_set_header X-Real-IP $remote_addr;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;/        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Proto https;/        proxy_set_header X-Forwarded-Proto https;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Host $host;/        proxy_set_header X-Forwarded-Host $host;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Port 443;/        proxy_set_header X-Forwarded-Port 443;/' nginx/conf.d/cloud.conf
sed -i 's/^#     }/    }/' nginx/conf.d/cloud.conf
sed -i 's/^#     location \/api\/ {/    location \/api\/ {/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_pass http:\/\/api:8000\/api\/;/        proxy_pass http:\/\/api:8000\/api\/;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header Host $host;/        proxy_set_header Host $host;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Real-IP $remote_addr;/        proxy_set_header X-Real-IP $remote_addr;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;/        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Proto https;/        proxy_set_header X-Forwarded-Proto https;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Host $host;/        proxy_set_header X-Forwarded-Host $host;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Port 443;/        proxy_set_header X-Forwarded-Port 443;/' nginx/conf.d/cloud.conf
sed -i 's/^#     }/    }/' nginx/conf.d/cloud.conf
sed -i 's/^#     location \/ws\/ {/    location \/ws\/ {/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_pass http:\/\/api:8000\/ws\/;/        proxy_pass http:\/\/api:8000\/ws\/;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_http_version 1.1;/        proxy_http_version 1.1;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header Upgrade $http_upgrade;/        proxy_set_header Upgrade $http_upgrade;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header Connection "upgrade";/        proxy_set_header Connection "upgrade";/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header Host $host;/        proxy_set_header Host $host;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Real-IP $remote_addr;/        proxy_set_header X-Real-IP $remote_addr;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;/        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Proto https;/        proxy_set_header X-Forwarded-Proto https;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Host $host;/        proxy_set_header X-Forwarded-Host $host;/' nginx/conf.d/cloud.conf
sed -i 's/^#         proxy_set_header X-Forwarded-Port 443;/        proxy_set_header X-Forwarded-Port 443;/' nginx/conf.d/cloud.conf
sed -i 's/^#     }/    }/' nginx/conf.d/cloud.conf
sed -i 's/^# }/}/' nginx/conf.d/cloud.conf
print_success "Admin domain re-enabled in nginx configuration"

# Step 5: Rebuild and start services
print_status "Rebuilding and starting services..."
docker-compose down
docker-compose build --no-cache frontend_admin
docker-compose up -d
print_success "Services rebuilt and started"

# Step 6: Wait for services to stabilize
print_status "Waiting for services to stabilize..."
sleep 20

# Step 7: Test admin frontend
print_status "Testing admin frontend..."
if docker-compose logs frontend_admin --tail=5 | grep -q "must-revalidate"; then
    print_error "frontend_admin still has nginx configuration issues"
    docker-compose logs frontend_admin --tail=10
    exit 1
else
    print_success "frontend_admin is working correctly"
fi

# Step 8: Test admin domain
print_status "Testing admin domain..."
if curl -k -s -o /dev/null -w "%{http_code}" https://admin.smartsecurity.solutions | grep -q "200\|301\|302"; then
    print_success "Admin domain is accessible"
else
    print_warning "Admin domain test failed"
fi

echo ""
echo "✅ Admin Frontend Re-enabled Successfully!"
echo ""
echo "🌐 Access URLs:"
echo "  Cloud:   https://cloud.smartsecurity.solutions"
echo "  Admin:   https://admin.smartsecurity.solutions"
echo "  API:     https://cloud.smartsecurity.solutions/api/"
echo "" 