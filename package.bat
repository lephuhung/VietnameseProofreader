@echo off
chcp 65001 >nul 2>&1
title VN Grammar Assistant - Full Package
color 0E

echo.
echo ============================================
echo   VN Grammar Assistant - Full Package
echo   Build + Download Office.js + ZIP
echo   (c) 2026 by thanh007
echo ============================================
echo.

set "ROOT_DIR=%~dp0"
set "SERVER_DIR=%ROOT_DIR%server"
set "OUTPUT_DIR=%ROOT_DIR%dist\VNGrammar"
set "ZIP_FILE=%ROOT_DIR%dist\VNGrammar_Offline.zip"
set "VENV_PY=%SERVER_DIR%\venv\Scripts\python.exe"

:: ============================================================
:: PRE-CHECK
:: ============================================================
if not exist "%VENV_PY%" (
    echo [ERROR] Python venv not found at %VENV_PY%
    echo        Run: cd server ^&^& python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

:: ============================================================
:: STEP 1: Download Office.js files (needs internet - one time)
:: ============================================================
echo [1/4] Downloading Office.js for offline use...
"%VENV_PY%" "%ROOT_DIR%tools\download_officejs.py"
if errorlevel 1 (
    echo [WARN] Download failed. Checking if files already exist...
)

:: Verify Office.js files exist
set "OFFICEJS_OK=1"
if not exist "%ROOT_DIR%addin\lib\office.js" set "OFFICEJS_OK=0"
if not exist "%ROOT_DIR%addin\lib\word-win32-16.01.js" set "OFFICEJS_OK=0"
if not exist "%ROOT_DIR%addin\lib\en-us\office_strings.js" set "OFFICEJS_OK=0"
if "%OFFICEJS_OK%"=="0" (
    echo [ERROR] Office.js files missing! Internet required for first build.
    pause
    exit /b 1
)
echo       [OK] Office.js files ready.
echo.

:: ============================================================
:: STEP 2: Build .exe with PyInstaller
:: ============================================================
echo [2/4] Building VNGrammar.exe ...
echo       This may take 2-5 minutes...
echo.

:: Activate venv
call "%SERVER_DIR%\venv\Scripts\activate.bat"

:: Ensure PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo       Installing PyInstaller...
    pip install pyinstaller
)

cd /d "%SERVER_DIR%"

pyinstaller --noconfirm --clean ^
    --name VNGrammar ^
    --distpath "%ROOT_DIR%dist" ^
    --workpath "%ROOT_DIR%build_temp" ^
    --specpath "%ROOT_DIR%build_temp" ^
    --add-data "%SERVER_DIR%\engine;engine" ^
    --hidden-import uvicorn.logging ^
    --hidden-import uvicorn.loops ^
    --hidden-import uvicorn.loops.auto ^
    --hidden-import uvicorn.protocols ^
    --hidden-import uvicorn.protocols.http ^
    --hidden-import uvicorn.protocols.http.auto ^
    --hidden-import uvicorn.protocols.websockets ^
    --hidden-import uvicorn.protocols.websockets.auto ^
    --hidden-import uvicorn.lifespan ^
    --hidden-import uvicorn.lifespan.on ^
    --hidden-import uvicorn.lifespan.off ^
    --hidden-import pystray._win32 ^
    --hidden-import PIL._tkinter_finder ^
    --noconsole ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo       [OK] Build complete.
echo.

:: ============================================================
:: STEP 3: Assemble distribution folder
:: ============================================================
echo [3/4] Assembling distribution...

:: Copy addin (with Office.js files)
if exist "%OUTPUT_DIR%\addin" rd /s /q "%OUTPUT_DIR%\addin"
xcopy /E /I /Y "%ROOT_DIR%addin" "%OUTPUT_DIR%\addin" >nul
echo       [OK] addin\ copied

:: Copy tools (only needed scripts)
if exist "%OUTPUT_DIR%\tools" rd /s /q "%OUTPUT_DIR%\tools"
mkdir "%OUTPUT_DIR%\tools"
copy /Y "%ROOT_DIR%tools\create_shortcut.ps1"   "%OUTPUT_DIR%\tools\" >nul
copy /Y "%ROOT_DIR%tools\generate_cert.ps1"     "%OUTPUT_DIR%\tools\" >nul
copy /Y "%ROOT_DIR%tools\generate_cert_py.py"   "%OUTPUT_DIR%\tools\" >nul
copy /Y "%ROOT_DIR%tools\install_cert.ps1"      "%OUTPUT_DIR%\tools\" >nul
echo       [OK] tools\ copied

:: Copy installer scripts
copy /Y "%ROOT_DIR%install.bat"   "%OUTPUT_DIR%\" >nul
copy /Y "%ROOT_DIR%uninstall.bat" "%OUTPUT_DIR%\" >nul
echo       [OK] install.bat, uninstall.bat copied

:: Cleanup build temp
rd /s /q "%ROOT_DIR%build_temp" >nul 2>&1

echo.

:: ============================================================
:: STEP 4: Create ZIP archive
:: ============================================================
echo [4/4] Creating ZIP archive...

:: Remove old ZIP
if exist "%ZIP_FILE%" del /f "%ZIP_FILE%"

:: Use PowerShell to create ZIP
cd /d "%ROOT_DIR%dist"
powershell -NoProfile -Command "Compress-Archive -Path 'VNGrammar' -DestinationPath '%ZIP_FILE%' -Force"

if errorlevel 1 (
    echo [ERROR] ZIP creation failed!
    pause
    exit /b 1
)

:: Show result
for %%F in ("%ZIP_FILE%") do set "ZIP_SIZE=%%~zF"
echo       [OK] Created: %ZIP_FILE%
echo       Size: %ZIP_SIZE% bytes
echo.

echo ============================================
echo.
echo   PACKAGE COMPLETE!
echo.
echo   Output: %ZIP_FILE%
echo.
echo   To deploy on any offline PC:
echo   1. Copy VNGrammar_Offline.zip
echo   2. Extract to any folder
echo   3. Run install.bat (as Admin)
echo   4. Open Word ^> Insert ^> My Add-ins
echo      ^> Shared Folder ^> VN Grammar
echo.
echo   No internet, no Python, no Node.js needed!
echo.
echo ============================================
echo.
pause
