@echo off
chcp 65001 >nul 2>&1
title VN Grammar Assistant - Build
color 0B

echo.
echo ============================================
echo   VN Grammar Assistant - Build
echo   (c) 2026 by thanh007
echo ============================================
echo.

set "ROOT_DIR=%~dp0"
set "SERVER_DIR=%ROOT_DIR%server"
set "OUTPUT_DIR=%ROOT_DIR%dist\VNGrammar"

:: Activate venv
if exist "%SERVER_DIR%\venv\Scripts\activate.bat" (
    call "%SERVER_DIR%\venv\Scripts\activate.bat"
)

:: Install PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/3] Installing PyInstaller...
    pip install pyinstaller
) else (
    echo [1/3] PyInstaller ready.
)

:: ============================================================
:: STEP 2: Build .exe (with console for debugging)
:: ============================================================
echo [2/3] Building VNGrammar.exe ...
echo       This may take 2-5 minutes...
echo.

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

:: ============================================================
:: STEP 3: Package distribution folder
:: ============================================================
echo.
echo [3/3] Packaging distribution...

:: Remove old addin folder to avoid nesting
if exist "%OUTPUT_DIR%\addin" rd /s /q "%OUTPUT_DIR%\addin"

:: Copy addin using xcopy (creates target folder correctly)
xcopy /E /I /Y "%ROOT_DIR%addin" "%OUTPUT_DIR%\addin" >nul

:: Copy tools
if exist "%OUTPUT_DIR%\tools" rd /s /q "%OUTPUT_DIR%\tools"
if exist "%ROOT_DIR%tools" xcopy /E /I /Y "%ROOT_DIR%tools" "%OUTPUT_DIR%\tools" >nul

:: Copy scripts
copy /Y "%ROOT_DIR%install.bat" "%OUTPUT_DIR%\" >nul
copy /Y "%ROOT_DIR%uninstall.bat" "%OUTPUT_DIR%\" >nul

:: Cleanup build temp
rd /s /q "%ROOT_DIR%build_temp" >nul 2>&1

echo.
echo ============================================
echo   BUILD COMPLETE!
echo.
echo   Output: %OUTPUT_DIR%
echo.
echo   Contents:
echo     VNGrammar.exe  - Server (runs in background)
echo     addin\         - Word Add-in UI
echo     install.bat    - Setup (run once)
echo     uninstall.bat  - Remove
echo.
echo   Copy the VNGrammar folder to any PC,
echo   then run install.bat
echo ============================================
echo.
pause
