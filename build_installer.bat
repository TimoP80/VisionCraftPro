@echo off
setlocal enabledelayedexpansion

title VisionCraft Pro - Installer Builder
color 0A
cls

echo.
echo ============================================================
echo   VisionCraft Pro - Windows Installer Builder v1.3.0
echo ============================================================
echo.

REM Check for NSIS
where makensis >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] NSIS not found in PATH
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo Make sure to add NSIS to your PATH environment variable.
    echo.
    echo Alternatively, run this script from the NSIS directory.
    echo.
    pause
    exit /b 1
)

echo [INFO] NSIS found. Building installer...
echo.

REM Check for LICENSE.txt
if not exist "LICENSE.txt" (
    echo [WARN] LICENSE.txt not found. Creating default license...
    (
        echo VisionCraft Pro License Agreement
        echo.
        echo Copyright (c) 2024 Timo Pitkänen
        echo.
        echo Permission is hereby granted, free of charge, to any person obtaining a copy
        echo of this software and associated documentation files (the "Software"), to deal
        echo in the Software without restriction, including without limitation the rights
        echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        echo copies of the Software, and to permit persons to whom the Software is
        echo furnished to do so, subject to the following conditions:
        echo.
        echo The above copyright notice and this permission notice shall be included in all
        echo copies or substantial portions of the Software.
        echo.
        echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        echo SOFTWARE.
    ) > LICENSE.txt
    echo [INFO] Created LICENSE.txt
)

REM Check for icon (optional)
if not exist "static\icon.ico" (
    echo [WARN] Application icon not found at static\icon.ico
    echo [INFO] Using default NSIS icon
)

REM Check for installer_config.json
if not exist "installer_config.json" (
    echo [WARN] installer_config.json not found. Using defaults...
    set "VERSION=1.3.0"
) else (
    REM Extract version from installer_config.json
    for /f "tokens=2 delims=:" %%a in ('findstr "version" installer_config.json') do (
        set "VERSION=%%a"
        set "VERSION=!VERSION:"=!"
        set "VERSION=!VERSION:,=!"
    )
    if "!VERSION!"=="" set "VERSION=1.3.0"
)
echo [INFO] Building version: !VERSION!

REM Check for installer.nsi
if not exist "installer.nsi" (
    echo [ERROR] installer.nsi not found!
    echo.
    pause
    exit /b 1
)

echo.
echo [BUILD] Compiling installer...
echo.

REM Run NSIS
makensis installer.nsi

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installer build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Build Successful!
echo ============================================================
echo.
echo Output: VisionCraftPro_Setup_!VERSION!.exe
echo.
echo Next steps:
echo 1. Test the installer on a clean Windows system
echo 2. Verify all features work correctly
echo 3. Distribute the installer to users
echo.
pause
