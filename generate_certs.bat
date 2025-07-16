@echo off
echo SmartSecurity SSL Certificate Generator
echo ======================================

REM Create SSL directories
if not exist "ssl\certs" mkdir "ssl\certs"
if not exist "ssl\private" mkdir "ssl\private"

echo Creating SSL directories...

REM Generate certificates using PowerShell
powershell -Command "& {
    Write-Host 'Generating certificate for cloud.smartsecurity.solutions...' -ForegroundColor Cyan
    
    # Generate certificate for cloud domain
    $cloudCert = New-SelfSignedCertificate -DnsName 'cloud.smartsecurity.solutions' -CertStoreLocation 'Cert:\CurrentUser\My' -NotAfter (Get-Date).AddYears(1)
    $cloudCertBytes = $cloudCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    [System.IO.File]::WriteAllBytes('ssl\certs\cloud.smartsecurity.solutions.crt', $cloudCertBytes)
    
    Write-Host 'Generating certificate for admin.smartsecurity.solutions...' -ForegroundColor Cyan
    
    # Generate certificate for admin domain
    $adminCert = New-SelfSignedCertificate -DnsName 'admin.smartsecurity.solutions' -CertStoreLocation 'Cert:\CurrentUser\My' -NotAfter (Get-Date).AddYears(1)
    $adminCertBytes = $adminCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    [System.IO.File]::WriteAllBytes('ssl\certs\admin.smartsecurity.solutions.crt', $adminCertBytes)
    
    Write-Host 'Certificates generated successfully!' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Next steps:' -ForegroundColor Yellow
    Write-Host '1. Add to your C:\Windows\System32\drivers\etc\hosts file:' -ForegroundColor White
    Write-Host '   127.0.0.1 cloud.smartsecurity.solutions' -ForegroundColor Gray
    Write-Host '   127.0.0.1 admin.smartsecurity.solutions' -ForegroundColor Gray
    Write-Host '2. Start Docker containers: docker-compose up -d' -ForegroundColor White
    Write-Host '3. Access via HTTPS:' -ForegroundColor White
    Write-Host '   - Cloud: https://cloud.smartsecurity.solutions' -ForegroundColor Gray
    Write-Host '   - Admin: https://admin.smartsecurity.solutions' -ForegroundColor Gray
}"

echo.
echo Certificate generation complete!
pause 