# SmartSecurity SSL Certificate Generator for Windows
# This script creates self-signed certificates for development

Write-Host "SmartSecurity SSL Certificate Generator for Windows" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Function to check if OpenSSL is available
function Test-OpenSSL {
    try {
        $opensslVersion = openssl version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OpenSSL found: $opensslVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        # Continue to next check
    }
    
    # Check if OpenSSL is in common installation paths
    $opensslPaths = @(
        "C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
        "C:\Program Files (x86)\OpenSSL-Win32\bin\openssl.exe",
        "C:\OpenSSL-Win64\bin\openssl.exe",
        "C:\OpenSSL-Win32\bin\openssl.exe"
    )
    
    foreach ($path in $opensslPaths) {
        if (Test-Path $path) {
            Write-Host "OpenSSL found at: $path" -ForegroundColor Green
            $env:PATH += ";$(Split-Path $path)"
            return $true
        }
    }
    
    return $false
}

# Function to install OpenSSL using Chocolatey
function Install-OpenSSLChocolatey {
    Write-Host "Attempting to install OpenSSL using Chocolatey..." -ForegroundColor Yellow
    
    # Check if Chocolatey is installed
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Chocolatey not found. Installing Chocolatey..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    
    Write-Host "Installing OpenSSL..." -ForegroundColor Yellow
    choco install openssl -y
    refreshenv
    
    # Test if installation was successful
    if (Test-OpenSSL) {
        Write-Host "OpenSSL installed successfully!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Failed to install OpenSSL via Chocolatey" -ForegroundColor Red
        return $false
    }
}

# Function to generate certificates using PowerShell and .NET
function Generate-CertificatePowerShell {
    param(
        [string]$Domain,
        [string]$CertPath,
        [string]$KeyPath
    )
    
    Write-Host "Generating certificate for $Domain using PowerShell..." -ForegroundColor Cyan
    
    try {
        # Create directories
        $certDir = Split-Path $CertPath -Parent
        $keyDir = Split-Path $KeyPath -Parent
        
        if (!(Test-Path $certDir)) {
            New-Item -ItemType Directory -Path $certDir -Force | Out-Null
        }
        if (!(Test-Path $keyDir)) {
            New-Item -ItemType Directory -Path $keyDir -Force | Out-Null
        }
        
        # Generate certificate using PowerShell
        $cert = New-SelfSignedCertificate -DnsName $Domain -CertStoreLocation "Cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1)
        
        # Export certificate
        $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
        [System.IO.File]::WriteAllBytes($CertPath, $certBytes)
        
        # Export private key (this is a simplified approach)
        $keyBytes = $cert.PrivateKey.ExportCspBlob($true)
        [System.IO.File]::WriteAllBytes($KeyPath, $keyBytes)
        
        Write-Host "Certificate generated successfully for $Domain" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "Failed to generate certificate for $Domain: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
if (!(Test-OpenSSL)) {
    Write-Host "OpenSSL not found. Attempting to install..." -ForegroundColor Yellow
    
    $installChoice = Read-Host "Do you want to install OpenSSL? (y/n)"
    if ($installChoice -eq 'y' -or $installChoice -eq 'Y') {
        if (!(Install-OpenSSLChocolatey)) {
            Write-Host "`nManual installation required:" -ForegroundColor Yellow
            Write-Host "1. Download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor White
            Write-Host "2. Install and add to PATH" -ForegroundColor White
            Write-Host "3. Restart PowerShell and run this script again" -ForegroundColor White
            exit 1
        }
    } else {
        Write-Host "`nUsing PowerShell alternative for certificate generation..." -ForegroundColor Yellow
        Write-Host "Note: This will create certificates in Windows certificate store" -ForegroundColor Yellow
    }
}

# Create SSL directories
$sslCertsDir = "ssl\certs"
$sslPrivateDir = "ssl\private"

if (!(Test-Path $sslCertsDir)) {
    New-Item -ItemType Directory -Path $sslCertsDir -Force | Out-Null
    Write-Host "Created directory: $sslCertsDir" -ForegroundColor Green
}

if (!(Test-Path $sslPrivateDir)) {
    New-Item -ItemType Directory -Path $sslPrivateDir -Force | Out-Null
    Write-Host "Created directory: $sslPrivateDir" -ForegroundColor Green
}

# Define domains and paths
$domains = @(
    @{
        Domain = "cloud.smartsecurity.solutions"
        CertPath = "ssl\certs\cloud.smartsecurity.solutions.crt"
        KeyPath = "ssl\private\cloud.smartsecurity.solutions.key"
    },
    @{
        Domain = "admin.smartsecurity.solutions"
        CertPath = "ssl\certs\admin.smartsecurity.solutions.crt"
        KeyPath = "ssl\private\admin.smartsecurity.solutions.key"
    }
)

# Generate certificates
$successCount = 0
foreach ($domainInfo in $domains) {
    if (Test-OpenSSL) {
        # Use OpenSSL if available
        Write-Host "`nGenerating certificate for $($domainInfo.Domain) using OpenSSL..." -ForegroundColor Cyan
        
        # Generate private key
        $keyCmd = "openssl genrsa -out `"$($domainInfo.KeyPath)`" 2048"
        Invoke-Expression $keyCmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Private key generated successfully" -ForegroundColor Green
        } else {
            Write-Host "Failed to generate private key" -ForegroundColor Red
            continue
        }
        
        # Create certificate signing request
        $csrPath = "ssl\$($domainInfo.Domain).csr"
        $csrCmd = "openssl req -new -key `"$($domainInfo.KeyPath)`" -out `"$csrPath`" -subj `/C=US/ST=State/L=City/O=SmartSecurity/OU=IT/CN=$($domainInfo.Domain)`"
        Invoke-Expression $csrCmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "CSR created successfully" -ForegroundColor Green
        } else {
            Write-Host "Failed to create CSR" -ForegroundColor Red
            continue
        }
        
        # Generate self-signed certificate
        $certCmd = "openssl x509 -req -in `"$csrPath`" -signkey `"$($domainInfo.KeyPath)`" -out `"$($domainInfo.CertPath)`" -days 365"
        Invoke-Expression $certCmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Certificate generated successfully" -ForegroundColor Green
        } else {
            Write-Host "Failed to generate certificate" -ForegroundColor Red
            continue
        }
        
        # Clean up CSR
        if (Test-Path $csrPath) {
            Remove-Item $csrPath -Force
        }
        
        $successCount++
        
    } else {
        # Use PowerShell alternative
        if (Generate-CertificatePowerShell -Domain $domainInfo.Domain -CertPath $domainInfo.CertPath -KeyPath $domainInfo.KeyPath) {
            $successCount++
        }
    }
}

Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "Successfully generated $successCount/$($domains.Count) certificates" -ForegroundColor Green

if ($successCount -eq $domains.Count) {
    Write-Host "`nAll certificates generated successfully!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Add to your C:\Windows\System32\drivers\etc\hosts file:" -ForegroundColor White
    Write-Host "   127.0.0.1 cloud.smartsecurity.solutions" -ForegroundColor Gray
    Write-Host "   127.0.0.1 admin.smartsecurity.solutions" -ForegroundColor Gray
    Write-Host "2. Start Docker containers: docker-compose up -d" -ForegroundColor White
    Write-Host "3. Access via HTTPS:" -ForegroundColor White
    Write-Host "   - Cloud: https://cloud.smartsecurity.solutions" -ForegroundColor Gray
    Write-Host "   - Admin: https://admin.smartsecurity.solutions" -ForegroundColor Gray
    Write-Host "`nNote: These are self-signed certificates for development only." -ForegroundColor Yellow
    Write-Host "For production, use Let's Encrypt or a proper CA." -ForegroundColor Yellow
} else {
    Write-Host "`nFailed to generate $($domains.Count - $successCount) certificates" -ForegroundColor Red
    exit 1
} 