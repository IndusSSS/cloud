# Add hosts file entries for SmartSecurity Cloud testing
# Run this script as Administrator

$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
$entries = @(
    "127.0.0.1 cloud.smartsecurity.solutions",
    "127.0.0.1 admin.smartsecurity.solutions"
)

Write-Host "Adding hosts file entries for SmartSecurity Cloud testing..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Read current hosts file
$currentContent = Get-Content $hostsFile -Raw

# Check which entries are missing
$missingEntries = @()
foreach ($entry in $entries) {
    if ($currentContent -notlike "*$entry*") {
        $missingEntries += $entry
    }
}

if ($missingEntries.Count -eq 0) {
    Write-Host "All required entries are already present in hosts file." -ForegroundColor Green
} else {
    # Create backup
    $backupFile = "$hostsFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $hostsFile $backupFile
    Write-Host "Created backup: $backupFile" -ForegroundColor Yellow
    
    # Add missing entries
    $newContent = $currentContent + "`n# SmartSecurity Cloud Development`n"
    foreach ($entry in $missingEntries) {
        $newContent += "$entry`n"
        Write-Host "Added: $entry" -ForegroundColor Green
    }
    
    # Write back to hosts file
    Set-Content $hostsFile $newContent -Encoding ASCII
    Write-Host "Hosts file updated successfully!" -ForegroundColor Green
}

Write-Host "`nYou can now run the HTTPS test script." -ForegroundColor Cyan 