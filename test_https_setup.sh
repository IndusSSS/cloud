#!/bin/bash

# HTTPS Setup Test Script
# Tests all aspects of the HTTPS configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="cloud.smartsecurity.solutions"
EMAIL="admin@smartsecurity.solutions"

echo -e "${BLUE}=== HTTPS Setup Test Script ===${NC}"
echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo -e "${YELLOW}Email:${NC} $EMAIL"
echo

# Function to print test results
print_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name: $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗${NC} $test_name: $message"
    else
        echo -e "${YELLOW}?${NC} $test_name: $message"
    fi
}

# Test 1: DNS Resolution
echo -e "${BLUE}Testing DNS Resolution...${NC}"
if nslookup $DOMAIN > /dev/null 2>&1; then
    IP=$(nslookup $DOMAIN | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    print_result "DNS Resolution" "PASS" "Domain resolves to $IP"
else
    print_result "DNS Resolution" "FAIL" "Domain does not resolve"
    exit 1
fi

# Test 2: Port 80 Accessibility
echo -e "${BLUE}Testing Port 80...${NC}"
if curl -s --connect-timeout 5 http://$DOMAIN > /dev/null 2>&1; then
    print_result "Port 80" "PASS" "HTTP is accessible"
else
    print_result "Port 80" "FAIL" "HTTP is not accessible"
fi

# Test 3: Port 443 Accessibility
echo -e "${BLUE}Testing Port 443...${NC}"
if curl -s --connect-timeout 5 -k https://$DOMAIN > /dev/null 2>&1; then
    print_result "Port 443" "PASS" "HTTPS is accessible"
else
    print_result "Port 443" "FAIL" "HTTPS is not accessible"
fi

# Test 4: SSL Certificate
echo -e "${BLUE}Testing SSL Certificate...${NC}"
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    CERT_EXPIRY=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -enddate | cut -d= -f2)
    print_result "SSL Certificate" "PASS" "Certificate found, expires: $CERT_EXPIRY"
else
    print_result "SSL Certificate" "FAIL" "Certificate not found"
fi

# Test 5: Certificate Chain
echo -e "${BLUE}Testing Certificate Chain...${NC}"
if openssl verify -CAfile /etc/letsencrypt/live/$DOMAIN/chain.pem /etc/letsencrypt/live/$DOMAIN/cert.pem > /dev/null 2>&1; then
    print_result "Certificate Chain" "PASS" "Certificate chain is valid"
else
    print_result "Certificate Chain" "FAIL" "Certificate chain is invalid"
fi

# Test 6: SSL/TLS Protocols
echo -e "${BLUE}Testing SSL/TLS Protocols...${NC}"
PROTOCOLS=$(nmap --script ssl-enum-ciphers -p 443 $DOMAIN 2>/dev/null | grep -E "TLSv1\.2|TLSv1\.3" | wc -l)
if [ "$PROTOCOLS" -ge 2 ]; then
    print_result "SSL/TLS Protocols" "PASS" "TLS 1.2 and 1.3 supported"
else
    print_result "SSL/TLS Protocols" "FAIL" "Insufficient protocol support"
fi

# Test 7: HTTP to HTTPS Redirect
echo -e "${BLUE}Testing HTTP to HTTPS Redirect...${NC}"
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN)
if [ "$REDIRECT_STATUS" = "301" ] || [ "$REDIRECT_STATUS" = "302" ]; then
    print_result "HTTP Redirect" "PASS" "HTTP redirects to HTTPS (Status: $REDIRECT_STATUS)"
else
    print_result "HTTP Redirect" "FAIL" "No redirect (Status: $REDIRECT_STATUS)"
fi

# Test 8: Security Headers
echo -e "${BLUE}Testing Security Headers...${NC}"
HSTS=$(curl -s -I https://$DOMAIN | grep -i "strict-transport-security" | wc -l)
CSP=$(curl -s -I https://$DOMAIN | grep -i "content-security-policy" | wc -l)
XFO=$(curl -s -I https://$DOMAIN | grep -i "x-frame-options" | wc -l)

if [ "$HSTS" -gt 0 ] && [ "$CSP" -gt 0 ] && [ "$XFO" -gt 0 ]; then
    print_result "Security Headers" "PASS" "HSTS, CSP, and X-Frame-Options present"
else
    print_result "Security Headers" "FAIL" "Missing security headers"
fi

# Test 9: Docker Services
echo -e "${BLUE}Testing Docker Services...${NC}"
if command -v docker-compose > /dev/null 2>&1; then
    if docker-compose ps | grep -q "Up"; then
        print_result "Docker Services" "PASS" "Docker services are running"
    else
        print_result "Docker Services" "FAIL" "Docker services are not running"
    fi
else
    print_result "Docker Services" "FAIL" "docker-compose not found"
fi

# Test 10: Nginx Configuration
echo -e "${BLUE}Testing Nginx Configuration...${NC}"
if docker-compose exec nginx nginx -t > /dev/null 2>&1; then
    print_result "Nginx Config" "PASS" "Nginx configuration is valid"
else
    print_result "Nginx Config" "FAIL" "Nginx configuration is invalid"
fi

# Test 11: Certificate Renewal
echo -e "${BLUE}Testing Certificate Renewal...${NC}"
if sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
    print_result "Auto Renewal" "PASS" "Certificate auto-renewal configured"
else
    print_result "Auto Renewal" "FAIL" "Certificate auto-renewal not configured"
fi

# Test 12: SSL Labs Grade (if available)
echo -e "${BLUE}Testing SSL Labs Grade...${NC}"
SSL_GRADE=$(curl -s "https://api.ssllabs.com/api/v3/analyze?host=$DOMAIN" | grep -o '"grade":"[A-F]"' | cut -d'"' -f4 2>/dev/null || echo "N/A")
if [ "$SSL_GRADE" != "N/A" ]; then
    if [[ "$SSL_GRADE" =~ ^[AB]$ ]]; then
        print_result "SSL Labs Grade" "PASS" "Grade: $SSL_GRADE (Good)"
    else
        print_result "SSL Labs Grade" "FAIL" "Grade: $SSL_GRADE (Needs improvement)"
    fi
else
    print_result "SSL Labs Grade" "SKIP" "Could not retrieve grade"
fi

# Summary
echo
echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo -e "${YELLOW}IP Address:${NC} $IP"
echo -e "${YELLOW}SSL Grade:${NC} $SSL_GRADE"
echo

# Recommendations
echo -e "${BLUE}=== Recommendations ===${NC}"
if [ "$SSL_GRADE" != "N/A" ] && [[ ! "$SSL_GRADE" =~ ^[AB]$ ]]; then
    echo -e "${YELLOW}•${NC} Improve SSL configuration to achieve A or B grade"
fi

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${YELLOW}•${NC} Run SSL setup script: ./setup_ssl_docker.sh"
fi

if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
    echo -e "${YELLOW}•${NC} Set up certificate auto-renewal"
fi

echo
echo -e "${GREEN}=== Test Complete ===${NC}"
echo "For detailed SSL analysis, visit: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN" 