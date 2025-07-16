Write-Host "SmartSecurity SSL Certificate Generator" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Create SSL directories
if (!(Test-Path "ssl\certs")) {
    New-Item -ItemType Directory -Path "ssl\certs" -Force
    Write-Host "Created ssl\certs directory" -ForegroundColor Green
}

if (!(Test-Path "ssl\private")) {
    New-Item -ItemType Directory -Path "ssl\private" -Force
    Write-Host "Created ssl\private directory" -ForegroundColor Green
}

Write-Host "Generating certificate for cloud.smartsecurity.solutions..." -ForegroundColor Cyan

# Generate certificate for cloud domain
$cloudCert = New-SelfSignedCertificate -DnsName "cloud.smartsecurity.solutions" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(1)
$cloudCertBytes = $cloudCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
[System.IO.File]::WriteAllBytes("ssl\certs\cloud.smartsecurity.solutions.crt", $cloudCertBytes)

Write-Host "Generating certificate for admin.smartsecurity.solutions..." -ForegroundColor Cyan

# Generate certificate for admin domain
$adminCert = New-SelfSignedCertificate -DnsName "admin.smartsecurity.solutions" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(1)
$adminCertBytes = $adminCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
[System.IO.File]::WriteAllBytes("ssl\certs\admin.smartsecurity.solutions.crt", $adminCertBytes)

Write-Host "Certificates generated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add to your C:\Windows\System32\drivers\etc\hosts file:" -ForegroundColor White
Write-Host "   127.0.0.1 cloud.smartsecurity.solutions" -ForegroundColor Gray
Write-Host "   127.0.0.1 admin.smartsecurity.solutions" -ForegroundColor Gray
Write-Host "2. Start Docker containers: docker-compose up -d" -ForegroundColor White
Write-Host "3. Access via HTTPS:" -ForegroundColor White
Write-Host "   - Cloud: https://cloud.smartsecurity.solutions" -ForegroundColor Gray
Write-Host "   - Admin: https://admin.smartsecurity.solutions" -ForegroundColor Gray 