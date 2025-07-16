# Generate SSL Certificates for Cloud Platform
# Industry Standard: RSA 2048-bit with SHA-256

Write-Host "Generating SSL certificates for Cloud Platform..." -ForegroundColor Green

# Create directories if they don't exist
$sslDir = "ssl"
$certsDir = "$sslDir\certs"
$privateDir = "$sslDir\private"

if (!(Test-Path $certsDir)) {
    New-Item -ItemType Directory -Path $certsDir -Force
    Write-Host "Created directory: $certsDir" -ForegroundColor Yellow
}

if (!(Test-Path $privateDir)) {
    New-Item -ItemType Directory -Path $privateDir -Force
    Write-Host "Created directory: $privateDir" -ForegroundColor Yellow
}

# Generate private key (RSA 2048-bit)
Write-Host "Generating private key..." -ForegroundColor Cyan
openssl genrsa -out "$privateDir\cloud.key" 2048

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Private key generated: $privateDir\cloud.key" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to generate private key" -ForegroundColor Red
    exit 1
}

# Generate certificate signing request (CSR)
Write-Host "Generating certificate signing request..." -ForegroundColor Cyan
openssl req -new -key "$privateDir\cloud.key" -out "$certsDir\cloud.csr" -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=cloud.smartsecurity.solutions"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ CSR generated: $certsDir\cloud.csr" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to generate CSR" -ForegroundColor Red
    exit 1
}

# Generate self-signed certificate (valid for 1 year)
Write-Host "Generating self-signed certificate..." -ForegroundColor Cyan
openssl x509 -req -in "$certsDir\cloud.csr" -signkey "$privateDir\cloud.key" -out "$certsDir\cloud.crt" -days 365 -sha256

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Certificate generated: $certsDir\cloud.crt" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to generate certificate" -ForegroundColor Red
    exit 1
}

# Generate admin certificate
Write-Host "Generating admin certificate..." -ForegroundColor Cyan
openssl req -new -key "$privateDir\cloud.key" -out "$certsDir\admin.csr" -subj "/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=admin.smartsecurity.solutions"
openssl x509 -req -in "$certsDir\admin.csr" -signkey "$privateDir\cloud.key" -out "$certsDir\admin.crt" -days 365 -sha256

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Admin certificate generated: $certsDir\admin.crt" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to generate admin certificate" -ForegroundColor Red
    exit 1
}

# Set proper permissions (for Linux compatibility)
Write-Host "Setting file permissions..." -ForegroundColor Cyan
icacls "$privateDir\cloud.key" /inheritance:r /grant:r "$env:USERNAME:(R)"
icacls "$certsDir\*.crt" /inheritance:r /grant:r "$env:USERNAME:(R)"

# Verify certificates
Write-Host "Verifying certificates..." -ForegroundColor Cyan
openssl x509 -in "$certsDir\cloud.crt" -text -noout | Select-String "Subject:"
openssl x509 -in "$certsDir\admin.crt" -text -noout | Select-String "Subject:"

Write-Host "`n✓ SSL certificates generated successfully!" -ForegroundColor Green
Write-Host "Files created:" -ForegroundColor Yellow
Write-Host "  Private Key: $privateDir\cloud.key" -ForegroundColor White
Write-Host "  Cloud Cert:  $certsDir\cloud.crt" -ForegroundColor White
Write-Host "  Admin Cert:  $certsDir\admin.crt" -ForegroundColor White
Write-Host "  CSR Files:   $certsDir\*.csr" -ForegroundColor White

Write-Host "`nNote: These are self-signed certificates for development/testing." -ForegroundColor Yellow
Write-Host "For production, use Let's Encrypt or a trusted CA." -ForegroundColor Yellow 