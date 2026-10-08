# generate_cert.ps1 — Generate + trust self-signed SSL cert (Windows PowerShell 5.1+)
# Only creates cert + trusts it + exports PFX. Server converts PFX→PEM at startup.
param(
    [string]$CertDir = "$env:USERPROFILE\.office-addin-dev-certs"
)

if (-not (Test-Path $CertDir)) { New-Item -ItemType Directory -Path $CertDir -Force | Out-Null }

$pfxPath = Join-Path $CertDir "localhost.pfx"

# Skip if PFX already exists and is valid
if (Test-Path $pfxPath) {
    Write-Host "       [OK] Certificate already exists. Skipping."
    exit 0
}

Write-Host "       Generating self-signed certificate..."

# Remove old localhost certs from stores
Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq "CN=localhost" } | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Subject -eq "CN=localhost" } | Remove-Item -Force -ErrorAction SilentlyContinue

# Create new self-signed cert
$cert = New-SelfSignedCertificate `
    -Subject "CN=localhost" `
    -DnsName "localhost","127.0.0.1" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -NotAfter (Get-Date).AddYears(5) `
    -KeyUsage DigitalSignature,KeyEncipherment `
    -KeyExportPolicy Exportable `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1")

Write-Host "       [OK] Certificate created."

# Export PFX (server will convert to PEM at startup)
$pwd = ConvertTo-SecureString -String "localhost" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pwd | Out-Null
Write-Host "       [OK] PFX exported: $pfxPath"

# Trust in CurrentUser\Root
$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","CurrentUser")
$store.Open("ReadWrite")
$store.Add($cert)
$store.Close()
Write-Host "       [OK] Certificate trusted in CurrentUser\Root"

# Also trust in LocalMachine\Root (needs admin, may fail — that's ok)
try {
    $storeM = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","LocalMachine")
    $storeM.Open("ReadWrite")
    $storeM.Add($cert)
    $storeM.Close()
    Write-Host "       [OK] Certificate trusted in LocalMachine\Root"
} catch {
    Write-Host "       [INFO] LocalMachine\Root skipped (needs admin)."
}

Write-Host "       [OK] Done. Server will auto-convert PFX to PEM."
