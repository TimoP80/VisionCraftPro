@echo off
echo Building VisionCraftPro Installer...
echo.

echo Compiling minimal installer script (without virtual environment)...
"C:\Program Files (x86)\NSIS\makensis.exe" installer_minimal.nsi

if %ERRORLEVEL% equ 0 (
    echo.
    echo SUCCESS: Installer built successfully!
    echo Installer file: VisionCraftPro_Setup_1.0.0.exe
    echo.
    echo NOTE: This installer uses system Python and will install dependencies on first run.
) else (
    echo.
    echo ERROR: Failed to build installer.
)

pause
