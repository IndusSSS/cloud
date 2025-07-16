# Manual SSL Certificate Setup for Windows

Since OpenSSL is not installed on your system, here are the steps to manually set up SSL certificates for HTTPS-only access.

## Option 1: Install OpenSSL (Recommended)

### Using Chocolatey (Easiest)
1. Open PowerShell as Administrator
2. Run the following command to install Chocolatey:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. Install OpenSSL:
   ```powershell
   choco install openssl -y
   ```
4. Restart PowerShell and run: `python generate_ssl_certs.py`

### Manual Installation
1. Download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html
2. Install and add to PATH
3. Restart PowerShell and run: `python generate_ssl_certs.py`

## Option 2: Use Windows Certificate Store (Alternative)

### Generate Certificates with PowerShell
1. Open PowerShell as Administrator
2. Run the following commands:

```powershell
# Create SSL directories
New-Item -ItemType Directory -Path "ssl\certs" -Force
New-Item -ItemType Directory -Path "ssl\private" -Force

# Generate certificate for cloud domain
$cloudCert = New-SelfSignedCertificate -DnsName "cloud.smartsecurity.solutions" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(1)
$cloudCertBytes = $cloudCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
[System.IO.File]::WriteAllBytes("ssl\certs\cloud.smartsecurity.solutions.crt", $cloudCertBytes)

# Generate certificate for admin domain
$adminCert = New-SelfSignedCertificate -DnsName "admin.smartsecurity.solutions" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(1)
$adminCertBytes = $adminCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
[System.IO.File]::WriteAllBytes("ssl\certs\admin.smartsecurity.solutions.crt", $adminCertBytes)

Write-Host "Certificates generated successfully!" -ForegroundColor Green
```

## Option 3: Use Docker with Built-in Certificates

If you want to proceed without generating certificates locally, you can use Docker with a simple HTTP setup for development:

### Temporary HTTP Setup
1. Edit `nginx/conf.d/cloud.conf` to use HTTP only temporarily
2. Start the application: `docker-compose up -d`
3. Access via HTTP:
   - http://localhost:8083 (Customer Portal)
   - http://localhost:8084 (Admin Console)

## Option 4: Download Pre-generated Certificates

For development purposes, you can download pre-generated self-signed certificates:

1. Create the SSL directories:
   ```powershell
   New-Item -ItemType Directory -Path "ssl\certs" -Force
   New-Item -ItemType Directory -Path "ssl\private" -Force
   ```

2. Download certificates from a trusted source or generate them on a Linux system

## Next Steps After Certificate Generation

1. **Add to hosts file** (`C:\Windows\System32\drivers\etc\hosts`):
   ```
   127.0.0.1 cloud.smartsecurity.solutions
   127.0.0.1 admin.smartsecurity.solutions
   ```

2. **Start Docker containers**:
   ```bash
   docker-compose up -d
   ```

3. **Access via HTTPS**:
   - Customer Portal: https://cloud.smartsecurity.solutions
   - Admin Console: https://admin.smartsecurity.solutions

## Troubleshooting

### Certificate Warnings
- Self-signed certificates will show browser warnings
- Click "Advanced" and "Proceed" for development
- For production, use Let's Encrypt or a proper CA

### Permission Issues
- Run PowerShell as Administrator for certificate generation
- Ensure you have write permissions to the project directory

### Docker Issues
- Ensure Docker Desktop is running
- Check container logs: `docker-compose logs nginx`

## Production Deployment

For production deployment:
1. Use Let's Encrypt certificates
2. Configure proper domain names
3. Set up automatic certificate renewal
4. Use proper SSL configuration

---

**Note**: These are development certificates. For production, always use proper SSL certificates from a trusted Certificate Authority. 