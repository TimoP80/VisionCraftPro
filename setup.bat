@echo off
title VisionCraft Pro - Setup
color 0A
cls

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                VisionCraft Pro - Setup Process               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.9 or higher from python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Python detected. Starting setup script...
python vcp_setup.py

if errorlevel 1 (
    echo.
    echo [FAIL] Setup failed. Please check the errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo [PASS] Setup process finished.
echo [INFO] Use 'run.bat' to start the application.
echo.
pause
