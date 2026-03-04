@echo off
REM VisionCraft Pro GUI Runner
REM This script runs the VisionCraft GUI Manager

echo ========================================
echo  VisionCraft Pro GUI Manager
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found.
    echo Please run install_gui.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Run the GUI
echo Starting VisionCraft GUI...
echo.
echo Close this window to stop the GUI.
echo.
visioncraft-gui

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo GUI exited with error code %errorlevel%
    echo Press any key to exit...
    pause >nul
)
