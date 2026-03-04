@echo off
REM VisionCraft Pro Desktop Shortcut Creator
REM Creates a desktop shortcut for the VisionCraft GUI

echo Creating desktop shortcut for VisionCraft GUI...

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

REM Get desktop path
set "DESKTOP_DIR=%USERPROFILE%\Desktop"

REM Create VBScript for shortcut creation
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo sLinkFile = "%DESKTOP_DIR%\VisionCraft GUI.lnk" >> "%TEMP%\create_shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\create_shortcut.vbs"
echo oLink.TargetPath = "%CURRENT_DIR%\run_gui.bat" >> "%TEMP%\create_shortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Description = "VisionCraft Pro GUI Manager" >> "%TEMP%\create_shortcut.vbs"
echo oLink.IconLocation = "shell32.dll,13" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Save >> "%TEMP%\create_shortcut.vbs"

REM Run the VBScript
cscript /nologo "%TEMP%\create_shortcut.vbs"

REM Clean up
del "%TEMP%\create_shortcut.vbs"

echo Desktop shortcut created successfully!
echo.
echo You can now double-click "VisionCraft GUI.lnk" on your desktop
echo to start the VisionCraft GUI Manager.
echo.
pause
