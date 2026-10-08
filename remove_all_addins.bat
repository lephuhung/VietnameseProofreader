@echo off
title Remove ALL Word Add-ins
color 0C
echo.
echo ============================================
echo   Remove ALL Word Add-ins (Clean Slate)
echo ============================================
echo.
echo   WARNING: This will remove ALL sideloaded
echo   add-ins from Word. Press Ctrl+C to cancel.
echo.
pause

:: 1. Close Word
echo.
echo [1/6] Closing Word...
taskkill /IM WINWORD.EXE /F >nul 2>&1
timeout /t 3 /nobreak >nul
echo       Done.

:: 2. Remove ALL Trusted Catalogs from registry
echo [2/6] Removing Trusted Add-in Catalogs...
reg delete "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs" /f >nul 2>&1
echo       Done.

:: 3. Remove WEF (Web Extensions Framework) cache
echo [3/6] Clearing WEF cache...
if exist "%LOCALAPPDATA%\Microsoft\Office\16.0\Wef" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Office\16.0\Wef" >nul 2>&1
    echo       Cleared: Wef
)

:: 4. Remove WebServiceCache
echo [4/6] Clearing web cache...
if exist "%LOCALAPPDATA%\Microsoft\Office\16.0\WebServiceCache" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Office\16.0\WebServiceCache" >nul 2>&1
    echo       Cleared: WebServiceCache
)

:: 5. Remove OTele
echo [5/6] Clearing telemetry cache...
if exist "%LOCALAPPDATA%\Microsoft\Office\OTele" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Office\OTele" >nul 2>&1
    echo       Cleared: OTele
)

:: 6. Remove ALL sideloaded manifest folders
echo [6/6] Removing manifest folders...
if exist "%LOCALAPPDATA%\VNGrammarManifests" (
    rd /s /q "%LOCALAPPDATA%\VNGrammarManifests" >nul 2>&1
    echo       Cleared: VNGrammarManifests
)

:: Remove startup shortcut
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\VNGrammar.lnk" >nul 2>&1

:: Kill VNGrammar if running
taskkill /IM VNGrammar.exe /F >nul 2>&1

echo.
echo ============================================
echo   ALL add-ins removed!
echo.
echo   Word is now clean - no sideloaded add-ins.
echo   Open Word to verify: Insert tab should
echo   show no custom add-ins.
echo ============================================
echo.
pause
