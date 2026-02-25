@echo off
TITLE VisionCraft Pro Server
echo [VCP] Starting VisionCraft Pro Server...

IF NOT EXIST .venv\Scripts\activate.bat (
    echo [WARN] Virtual environment not found. Running setup first...
    call setup.bat
)

echo [VCP] Activating environment...
call .venv\Scripts\activate.bat

echo [VCP] Launching FastAPI server...
python visioncraft_server.py

if %ERRORLEVEL% neq 0 (
    echo [FAIL] Server exited with error code %ERRORLEVEL%
    pause
)
