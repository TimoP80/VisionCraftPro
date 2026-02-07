@echo off
echo Building VisionCraftPro Installer...
echo.

REM Check if NSIS is installed
makensis /VERSION >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH.
    echo Please install NSIS from https://nsis.sourceforge.io/Download
    echo.
    echo After installation, make sure to add NSIS to your PATH or run this from NSIS directory.
    pause
    exit /b 1
)

REM Create license file if it doesn't exist
if not exist "LICENSE.txt" (
    echo Creating LICENSE.txt file...
    echo VisionCraftPro License Agreement > LICENSE.txt
    echo. >> LICENSE.txt
    echo This software is provided as-is without any warranty. >> LICENSE.txt
    echo. >> LICENSE.txt
    echo By using this software, you agree to the terms and conditions. >> LICENSE.txt
    echo. >> LICENSE.txt
    echo For more information, visit: https://github.com/visioncraftpro >> LICENSE.txt
)

REM Check if icon exists, create placeholder if not
if not exist "static\icon.ico" (
    echo Creating placeholder icon...
    if not exist "static" mkdir static
    echo Placeholder icon file > static\icon.ico.txt
    echo WARNING: Please replace static\icon.ico with a proper icon file
)

REM Build the installer
echo Compiling installer script...
if exist "installer_simple.nsi" (
    echo Using simple installer script...
    makensis installer_simple.nsi
) else (
    echo Using main installer script...
    makensis installer.nsi
)

if %ERRORLEVEL% equ 0 (
    echo.
    echo SUCCESS: Installer built successfully!
    echo Installer file: VisionCraftPro_Setup_1.0.0.exe
    echo.
    echo You can now distribute this installer to users.
    echo.
    echo Note: Users will need Python 3.9+ and compatible GPU drivers installed.
) else (
    echo.
    echo ERROR: Failed to build installer.
    echo Please check the installer.nsi script for any errors.
)

pause
