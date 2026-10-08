@echo off
title VN Grammar Assistant - Installer
color 0A

:: ============================================================
:: Check admin rights (needed for network share + cert trust)
:: ============================================================
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ============================================
echo   VN Grammar Assistant - Installer
echo   Copyright 2026 by thanh007
echo   No internet required
echo ============================================
echo.

set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%VNGrammar.exe"
set "MANIFEST=%APP_DIR%addin\manifest.xml"
set "TOOLS_DIR=%APP_DIR%tools"
set "MANIFEST_DIR=%LOCALAPPDATA%\VNGrammarManifests"

if not exist "%EXE_PATH%" (
    echo [ERROR] VNGrammar.exe not found!
    pause
    exit /b 1
)

:: ============================================================
:: STEP 1: Close Word + old server
:: ============================================================
echo [1/5] Closing Word and old server...
taskkill /IM WINWORD.EXE /F >nul 2>&1
taskkill /IM VNGrammar.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul
echo       Done.
echo.

:: ============================================================
:: STEP 2: Loopback exemption + auto-start
:: ============================================================
echo [2/5] Setting up loopback exemption...
CheckNetIsolation LoopbackExempt -a -n="microsoft.win32webviewhost_cw5n1h2txyewy" >nul 2>&1
echo       [OK] Loopback exemption added.
echo.

echo [3/5] Setting up auto-start...
powershell -NoProfile -ExecutionPolicy Bypass -File "%TOOLS_DIR%\create_shortcut.ps1" "%EXE_PATH%" "%APP_DIR%"
echo       [OK] Auto-start enabled.
echo.

:: ============================================================
:: STEP 4: Create manifest share folder
:: ============================================================
echo [4/5] Setting up manifest catalog...
if not exist "%MANIFEST_DIR%" mkdir "%MANIFEST_DIR%"
copy /Y "%MANIFEST%" "%MANIFEST_DIR%\manifest.xml" >nul
echo       Manifest copied.

:: Remove old share if exists
net share VNGrammarCatalog /delete >nul 2>&1

:: Create network share
net share VNGrammarCatalog="%MANIFEST_DIR%" /grant:everyone,READ >nul 2>&1
if errorlevel 1 (
    echo       [WARN] Could not create network share.
    echo       You may need to add the catalog manually.
) else (
    echo       [OK] Network share created.
)
echo.

:: ============================================================
:: STEP 5: Register Trusted Catalog (UNC path)
:: ============================================================
echo [4/5] Registering add-in catalog...
set "CATALOG_GUID={3dbd0ece-b27b-4029-a1b7-a3a7c6f0ab21}"
for /f %%H in ('hostname') do set "HOSTNAME=%%H"
set "UNC_PATH=\\%HOSTNAME%\VNGrammarCatalog"

reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\%CATALOG_GUID%" /v Id /t REG_SZ /d "%CATALOG_GUID%" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\%CATALOG_GUID%" /v Url /t REG_SZ /d "%UNC_PATH%" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\%CATALOG_GUID%" /v Flags /t REG_DWORD /d 1 /f >nul 2>&1
echo       [OK] Catalog: %UNC_PATH%
echo.

:: ============================================================
:: STEP 6: Start server
:: ============================================================
echo [5/5] Starting VN Grammar server...
start "" "%EXE_PATH%"
echo       Waiting for server...
timeout /t 5 /nobreak >nul
echo       [OK] Server started.
echo.

echo ============================================
echo.
echo   INSTALLATION COMPLETE!
echo.
echo   FINAL STEP - do this ONCE in Word:
echo   1. Open Word
echo   2. Insert tab - My Add-ins
echo   3. Click "SHARED FOLDER" tab
echo   4. Select "VN Grammar" - click Add
echo   5. Done! The button appears on Home tab.
echo.
echo   VNGrammar starts automatically with
echo   Windows. No further action needed.
echo.
echo   To uninstall: run uninstall.bat
echo.
echo ============================================
echo.
pause
