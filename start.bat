@echo off
echo 🚀 Starting VisionCraft Pro Server...
echo.

REM Check if keys.txt exists
if not exist "keys.txt" (
    echo ❌ keys.txt not found!
    echo Please create keys.txt with your HF_TOKEN
    echo.
    pause
    exit /b 1
)

REM Check if HF_TOKEN is configured
findstr /C:"YOUR_HF_TOKEN_HERE" keys.txt >nul
if %errorlevel%==0 (
    echo ⚠️  HF_TOKEN is not configured!
    echo Please edit keys.txt and replace YOUR_HF_TOKEN_HERE with your actual Hugging Face token
    echo Get your token from: https://huggingface.co/settings/tokens
    echo.
    pause
    exit /b 1
)

echo ✅ Configuration looks good!
echo 🌐 Starting server...
echo.

REM Start the server
python start_server.py

pause
