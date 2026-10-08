@echo off
title Clear Word Add-in Cache
echo.
echo ============================================
echo   Clear Word Add-in Cache
echo ============================================
echo.

:: Kill Word if running
echo [1/3] Closing Word...
taskkill /IM WINWORD.EXE /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Done.

:: Clear WEF cache
echo [2/3] Clearing Add-in cache...
if exist "%LOCALAPPDATA%\Microsoft\Office\16.0\Wef" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Office\16.0\Wef" >nul 2>&1
    echo       Cleared: Wef
)
if exist "%LOCALAPPDATA%\Microsoft\Office\OTele" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Office\OTele" >nul 2>&1
    echo       Cleared: OTele
)

:: Clear webview cache (icon + HTML cache)
for /d %%d in ("%LOCALAPPDATA%\Microsoft\Office\16.0\WebServiceCache\*") do (
    rd /s /q "%%d" >nul 2>&1
)
echo       Cleared: WebServiceCache

echo [3/3] Done!
echo.
echo       Now run install.bat and open Word.
echo.
pause
