# install_cert.ps1 — Copy bundled SSL cert + trust CA root
param(
    [Parameter(Mandatory=$true)]
    [string]$CertSource
)

$CertDir = Join-Path $env:USERPROFILE ".office-addin-dev-certs"

if (-not (Test-Path $CertDir)) {
    New-Item -ItemType Directory -Path $CertDir -Force | Out-Null
}

# Copy all cert files
$files = @("ca.crt", "localhost.crt", "localhost.key")
foreach ($f in $files) {
    $src = Join-Path $CertSource $f
    if (Test-Path $src) {
        Copy-Item $src (Join-Path $CertDir $f) -Force
    } else {
        Write-Host "       [WARN] Missing: $f"
    }
}
Write-Host "       [OK] Certificate files copied."

# Trust the CA root cert (NOT localhost.crt!)
$caCrt = Join-Path $CertDir "ca.crt"
if (Test-Path $caCrt) {
    # LocalMachine\Root (requires admin)
    certutil -addstore Root "$caCrt" 2>&1 | Out-Null
    Write-Host "       [OK] CA trusted in LocalMachine\Root"
    
    # CurrentUser\Root (backup)
    certutil -addstore -user Root "$caCrt" 2>&1 | Out-Null
    Write-Host "       [OK] CA trusted in CurrentUser\Root"
} else {
    Write-Host "       [ERROR] ca.crt not found!"
}
