@echo off
REM VisionCraft Pro GUI Installer
REM This script installs the VisionCraft GUI Manager

echo ========================================
echo  VisionCraft Pro GUI Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required.
    echo Current version:
    python --version
    pause
    exit /b 1
)

echo Python version OK.
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

echo.
echo Installing VisionCraft GUI...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install VisionCraft GUI.
    pause
    exit /b 1
)

echo.
echo Installing additional dependencies...
echo Note: tkinter is included with Python - no installation needed
if errorlevel 1 (
    echo WARNING: tkinter may not be available via pip (it's usually included with Python).
    echo This is normal if you're seeing this message.
)

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo You can now run VisionCraft GUI with:
echo   run_gui.bat
echo.
echo Or manually with:
echo   venv\Scripts\activate && visioncraft-gui
echo.
pause
