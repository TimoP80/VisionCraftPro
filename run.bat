echo [INFO] Starting VisionCraft Pro...

if not exist ".venv\Scripts\activate.bat" (
    echo [WARN] Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the app
python minimal_desktop.py

if errorlevel 1 (
    echo.
    echo [FAIL] VisionCraft Pro exited with an error.
    echo.
    pause
)
