@echo off
echo Building VisionCraftPro Installer...
echo.

echo Compiling installer script...
makensis installer_simple.nsi

if %ERRORLEVEL% equ 0 (
    echo.
    echo SUCCESS: Installer built successfully!
    echo Installer file: VisionCraftPro_Setup_1.0.0.exe
) else (
    echo.
    echo ERROR: Failed to build installer.
)

pause
