@echo off
title VisionCraft Pro - Professional AI Image Generator
color 0A
cls

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                VisionCraft Pro - Desktop Application           ║
echo ║              Professional AI Image Generator                  ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🎨 Starting VisionCraft Pro Desktop...
echo.

REM Get the directory where this batch file is located
set APP_DIR=%~dp0
cd /d "%APP_DIR%"

echo 📁 Installation directory: %APP_DIR%
echo.

REM Check if virtual environment exists
if not exist "%APP_DIR%venv_gtx1070\Scripts\activate.bat" (
    echo ❌ Virtual environment not found at: %APP_DIR%venv_gtx1070\Scripts\activate.bat
    echo.
    echo 🔧 Attempting to use system Python...
    echo.
    
    REM Check if Python is available system-wide
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python not found! Please install Python 3.9+ from python.org
        echo.
        pause
        exit /b 1
    )
    
    REM Check if required packages are installed
    echo 📦 Checking required packages...
    python -c "import fastapi, uvicorn, torch, diffusers" 2>nul
    if errorlevel 1 (
        echo 📦 Installing required packages...
        python -m pip install -r requirements.txt
        if errorlevel 1 (
            echo ❌ Failed to install required packages
            pause
            exit /b 1
        )
    )
    
    REM Check if PyTorch has CUDA support
    echo 🎯 Checking PyTorch CUDA support...
    python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>nul
    if errorlevel 1 (
        echo ❌ Failed to check PyTorch CUDA support
    ) else (
        echo ✅ PyTorch CUDA check completed
    )
    
    REM If CUDA is not available, offer to install GPU PyTorch
    python -c "import torch; cuda_available = torch.cuda.is_available(); print('CUDA_AVAILABLE:', cuda_available)" 2>temp_cuda_check.txt
    findstr /C:"CUDA_AVAILABLE: True" temp_cuda_check.txt >nul
    if errorlevel 1 (
        echo ⚠️  PyTorch CPU-only version detected
        echo 💡 Installing GPU-enabled PyTorch for better performance...
        echo.
        echo This will install PyTorch with CUDA support for your NVIDIA GPU
        echo.
        set /p install_gpu="Install GPU PyTorch? (y/n): "
        if /i "%install_gpu%"=="y" (
            echo 🔄 Uninstalling CPU PyTorch...
            python -m pip uninstall torch torchvision torchaudio -y
            echo 📦 Installing GPU PyTorch with CUDA...
            python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
            if errorlevel 1 (
                echo ❌ Failed to install GPU PyTorch
                echo 💡 You can install manually: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
            ) else (
                echo ✅ GPU PyTorch installed successfully
                echo 🔄 Verifying installation...
                python -c "import torch; print('New CUDA available:', torch.cuda.is_available())"
            )
        ) else (
            echo ⚠️  Continuing with CPU PyTorch (slower performance)
        )
    ) else (
        echo ✅ GPU PyTorch is already available
    )
    del temp_cuda_check.txt 2>nul
    
    echo ✅ Using system Python environment
    goto launch_app
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call "%APP_DIR%venv_gtx1070\Scripts\activate.bat"

:launch_app
REM Check if PyWebView is installed
python -c "import webview" 2>nul
if errorlevel 1 (
    echo 📦 Installing PyWebView...
    python -m pip install pywebview
    if errorlevel 1 (
        echo ❌ Failed to install PyWebView
        pause
        exit /b 1
    )
)

REM Ensure generated_images directories exist and are writable
echo 📁 Setting up image directories...
if not exist "%APP_DIR%generated_images" mkdir "%APP_DIR%generated_images"
if not exist "%APP_DIR%generated_images\images" mkdir "%APP_DIR%generated_images\images"

REM Test write permissions
echo test > "%APP_DIR%generated_images\test_write.tmp" 2>nul
if errorlevel 1 (
    echo ⚠️  Warning: Cannot write to generated_images directory
    echo 💡 Try running as administrator or check folder permissions
    echo.
) else (
    del "%APP_DIR%generated_images\test_write.tmp" 2>nul
    echo ✅ Image directories are ready
)

REM Launch the desktop app
echo 🚀 Launching desktop application...
echo.
python "%APP_DIR%minimal_desktop.py"

REM If the app crashes, show error
if errorlevel 1 (
    echo.
    echo ❌ VisionCraft Pro encountered an error
    echo Check the console output above for details.
    echo.
    pause
)
