@echo off
title VN Grammar Assistant - Uninstall
color 0C

:: Check admin rights
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ============================================
echo   VN Grammar Assistant - Uninstall
echo ============================================
echo.

echo [1/7] Closing Word and VNGrammar...
taskkill /IM WINWORD.EXE /F >nul 2>&1
taskkill /IM VNGrammar.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Done.

echo [2/7] Removing network share...
net share VNGrammarCatalog /delete >nul 2>&1
echo       Done.

echo [3/7] Removing SSL certificates...
:: Remove cert files
set "CERT_DIR=%USERPROFILE%\.office-addin-dev-certs"
if exist "%CERT_DIR%" (
    :: Remove from trusted root store
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "try { $certs = Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Subject -match 'localhost' }; foreach ($c in $certs) { $store = New-Object System.Security.Cryptography.X509Certificates.X509Store('Root','CurrentUser'); $store.Open('ReadWrite'); $store.Remove($c); $store.Close(); Write-Host '       Removed cert:' $c.Thumbprint }; } catch { Write-Host '       No certs to remove' }"
    :: Also remove from My store
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "try { $certs = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -match 'localhost' }; foreach ($c in $certs) { $store = New-Object System.Security.Cryptography.X509Certificates.X509Store('My','CurrentUser'); $store.Open('ReadWrite'); $store.Remove($c); $store.Close() }; } catch { }"
    rd /s /q "%CERT_DIR%" >nul 2>&1
)
echo       Done.

echo [4/7] Removing loopback exemption...
CheckNetIsolation LoopbackExempt -d -n="microsoft.win32webviewhost_cw5n1h2txyewy" >nul 2>&1
echo       Done.

echo [5/7] Removing auto-start...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\VNGrammar.lnk" >nul 2>&1
echo       Done.

echo [6/7] Removing manifest folder...
rd /s /q "%LOCALAPPDATA%\VNGrammarManifests" >nul 2>&1
echo       Done.

echo [7/7] Cleaning registry and cache...
set "CATALOG_GUID={3dbd0ece-b27b-4029-a1b7-a3a7c6f0ab21}"
reg delete "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\%CATALOG_GUID%" /f >nul 2>&1
rd /s /q "%LOCALAPPDATA%\Microsoft\Office\16.0\Wef" >nul 2>&1
rd /s /q "%LOCALAPPDATA%\Microsoft\Office\16.0\WebServiceCache" >nul 2>&1
echo       Done.

echo.
echo ============================================
echo   Uninstall complete!
echo   Restart Word to apply changes.
echo ============================================
echo.
pause
