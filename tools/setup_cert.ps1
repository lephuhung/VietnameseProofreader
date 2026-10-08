# VN Grammar Assistant - SSL Certificate Generator
# Creates self-signed cert for localhost (required by Office Add-in)

$certDir = Join-Path $env:USERPROFILE ".office-addin-dev-certs"
$keyPath = Join-Path $certDir "localhost.key"
$crtPath = Join-Path $certDir "localhost.crt"

if ((Test-Path $keyPath) -and (Test-Path $crtPath)) {
    Write-Host "      SSL cert already exists."
    exit 0
}

if (!(Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir -Force | Out-Null
}

try {
    # Create self-signed certificate
    $cert = New-SelfSignedCertificate `
        -DnsName "localhost" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(10) `
        -FriendlyName "VNGrammar Dev Cert" `
        -TextExtension @("2.5.29.17={text}DNS=localhost&IPAddress=127.0.0.1")

    # Export private key via PFX
    $pfxPath = Join-Path $env:TEMP "vngrammar_temp.pfx"
    $pwd = ConvertTo-SecureString -String "vngrammar" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pwd | Out-Null

    # Try openssl to convert PFX to PEM
    $opensslFound = $false
    try {
        openssl version 2>$null | Out-Null
        $opensslFound = $true
    } catch {}

    if ($opensslFound) {
        openssl pkcs12 -in $pfxPath -nocerts -nodes -out $keyPath -passin pass:vngrammar 2>$null
        openssl pkcs12 -in $pfxPath -clcerts -nokeys -out $crtPath -passin pass:vngrammar 2>$null
    }

    # Fallback: export using .NET if openssl not available
    if (!(Test-Path $keyPath)) {
        # Export certificate (public)
        $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
        $pemCert = "-----BEGIN CERTIFICATE-----`r`n"
        $pemCert += [Convert]::ToBase64String($certBytes, "InsertLineBreaks")
        $pemCert += "`r`n-----END CERTIFICATE-----"
        Set-Content -Path $crtPath -Value $pemCert -NoNewline

        # Export private key
        $rsaKey = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
        $keyBytes = $rsaKey.ExportRSAPrivateKey()
        $pemKey = "-----BEGIN RSA PRIVATE KEY-----`r`n"
        $pemKey += [Convert]::ToBase64String($keyBytes, "InsertLineBreaks")
        $pemKey += "`r`n-----END RSA PRIVATE KEY-----"
        Set-Content -Path $keyPath -Value $pemKey -NoNewline
    }

    # Trust the certificate
    try {
        Import-Certificate -FilePath $crtPath -CertStoreLocation "Cert:\CurrentUser\Root" -Confirm:$false | Out-Null
        Write-Host "      Certificate trusted."
    } catch {
        Write-Host "      [WARN] Could not auto-trust cert."
    }

    # Cleanup
    Remove-Item $pfxPath -ErrorAction SilentlyContinue

    Write-Host "      SSL cert created at: $certDir"
} catch {
    Write-Host "      [ERROR] Failed to create SSL cert: $_"
    exit 1
}
