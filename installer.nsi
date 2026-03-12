; VisionCraft Pro - NSIS Installer Script
; Version: 1.3.0
; Author: Timo Pitkänen (tpitkane@gmail.com)

;--------------------------------
; Includes
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "x64.nsh"

;--------------------------------
; General Configuration
Name "VisionCraft Pro"
OutFile "VisionCraftPro_Setup_1.3.0.exe"
InstallDir "$PROGRAMFILES\VisionCraftPro"
InstallDirRegKey HKLM "Software\VisionCraftPro" "InstallDir"
RequestExecutionLevel admin

;--------------------------------
; Version Information
VIProductVersion "1.3.0.0"
VIAddVersionKey "ProductName" "VisionCraft Pro"
VIAddVersionKey "CompanyName" "Timo Pitkänen"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2024 Timo Pitkänen"
VIAddVersionKey "FileDescription" "VisionCraft Pro Installer"
VIAddVersionKey "FileVersion" "1.3.0"
VIAddVersionKey "ProductVersion" "1.3.0"

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

; Section: Core Application (Required)
Section "VisionCraft Pro Core" SEC_CORE
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    ; Copy all application files
    File /r "*.py"
    File /r "*.bat"
    File /r "*.sh"
    File /r "*.json"
    File /r "*.txt"
    File /r "*.md"
    File /r "static"
    File /r "data"
    
    ; Create directory structure
    CreateDirectory "$INSTDIR\generated_images"
    CreateDirectory "$INSTDIR\generated_images\images"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\VisionCraftPro" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\VisionCraftPro" "Version" "1.3.0"
    
    ; Write uninstall information
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "DisplayName" "VisionCraft Pro"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "DisplayIcon" "$INSTDIR\run.bat"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "Publisher" "Timo Pitkänen"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "DisplayVersion" "1.3.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "URLInfoAbout" "https://github.com"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "NoRepair" 1
    
    ; Get installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro" "EstimatedSize" "$0"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Section: Python Check
Section "Python Installation Check" SEC_PYTHON
    ; Check for Python in HKLM registry first
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore" "InstallPath"
    StrCmp $0 "" 0 python_found_hklm
    
    ; Check for Python in HKCU registry
    ReadRegStr $0 HKCU "SOFTWARE\Python\PythonCore" "InstallPath"
    StrCmp $0 "" 0 python_found_hkcu
    
    ; Python not found in either location
    MessageBox MB_YESNO|MB_ICONQUESTION "Python 3.9 or higher was not detected. VisionCraft Pro requires Python to run.$\n$\nWould you like to continue anyway?" IDNO skip_python
    Abort "Python 3.9+ is required. Please install Python from python.org"
    skip_python:
    Goto python_check_done
    
    python_found_hklm:
    ; Check Python version from HKLM
    ReadRegStr $1 HKLM "SOFTWARE\Python\PythonCore\3.12" "InstallPath"
    StrCmp $1 "" 0 python_ver_ok
    ReadRegStr $1 HKLM "SOFTWARE\Python\PythonCore\3.11" "InstallPath"
    StrCmp $1 "" 0 python_ver_ok
    ReadRegStr $1 HKLM "SOFTWARE\Python\PythonCore\3.10" "InstallPath"
    StrCmp $1 "" 0 python_ver_ok
    ReadRegStr $1 HKLM "SOFTWARE\Python\PythonCore\3.9" "InstallPath"
    StrCmp $1 "" python_version_check_hklm python_ver_ok
    
    python_version_check_hklm:
    MessageBox MB_YESNO|MB_ICONQUESTION "Python 3.9 or higher was not detected. VisionCraft Pro requires Python 3.9+ to run.$\n$\nWould you like to continue anyway?" IDNO skip_python
    Abort "Python 3.9+ is required. Please install Python from python.org"
    Goto skip_python
    
    python_found_hkcu:
    ; Check Python version from HKCU
    ReadRegStr $1 HKCU "SOFTWARE\Python\PythonCore\3.12" "InstallPath"
    StrCmp $1 "" 0 python_ver_ok
    ReadRegStr $1 HKCU "SOFTWARE\Python\PythonCore\3.11" "InstallPath"
    StrCmp $1 "" 0 python_ver_ok
    ReadRegStr $1 HKCU "SOFTWARE\Python\PythonCore\3.10" "InstallPath"
    StrCmp $1 "" 0 python_ver_ok
    ReadRegStr $1 HKCU "SOFTWARE\Python\PythonCore\3.9" "InstallPath"
    StrCmp $1 "" python_version_check_hkcu python_ver_ok
    
    python_version_check_hkcu:
    MessageBox MB_YESNO|MB_ICONQUESTION "Python 3.9 or higher was not detected. VisionCraft Pro requires Python 3.9+ to run.$\n$\nWould you like to continue anyway?" IDNO skip_python
    Abort "Python 3.9+ is required. Please install Python from python.org"
    Goto skip_python
    
    python_ver_ok:
    MessageBox MB_OK "Python 3.9+ detected! After installation, run 'setup.bat' to install required dependencies."
    
    python_check_done:
SectionEnd

; Section: Start Menu Shortcuts
Section "Start Menu Shortcuts" SEC_STARTMENU
    CreateDirectory "$SMPROGRAMS\VisionCraft Pro"
    CreateShortCut "$SMPROGRAMS\VisionCraft Pro\VisionCraft Pro.lnk" "$INSTDIR\run.bat"
    CreateShortCut "$SMPROGRAMS\VisionCraft Pro\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$SMPROGRAMS\VisionCraft Pro\Setup.lnk" "$INSTDIR\setup.bat"
SectionEnd

; Section: Desktop Shortcut
Section "Desktop Shortcut" SEC_DESKTOP
    CreateShortCut "$DESKTOP\VisionCraft Pro.lnk" "$INSTDIR\run.bat"
SectionEnd

; Section: Run Setup
Section "Run Setup After Installation" SEC_SETUP
    ; Create a batch file to run setup
    FileOpen $0 "$INSTDIR\post_install.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 "title VisionCraft Pro - Post-Install Setup$\r$\n"
    FileWrite $0 "echo.$\r$\n"
    FileWrite $0 "echo Running VisionCraft Pro setup...$\r$\n"
    FileWrite $0 "echo.$\r$\n"
    FileWrite $0 "call setup.bat$\r$\n"
    FileWrite $0 "pause$\r$\n"
    FileClose $0
    
    ; Ask user if they want to run setup
    MessageBox MB_YESNO|MB_ICONINFORMATION "Would you like to run the setup process now to install Python dependencies?" IDNO skip_run_setup
        ExecWait 'cmd /c "$INSTDIR\post_install.bat"'
        skip_run_setup:
SectionEnd

;--------------------------------
; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CORE} "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_PYTHON} "Verify Python 3.9+ is installed"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} "Create Start Menu shortcuts"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} "Create Desktop shortcut"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_SETUP} "Run setup to install Python dependencies"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\*.py"
    Delete "$INSTDIR\*.bat"
    Delete "$INSTDIR\*.sh"
    Delete "$INSTDIR\*.json"
    Delete "$INSTDIR\*.txt"
    Delete "$INSTDIR\*.md"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$INSTDIR\post_install.bat"
    
    ; Remove directories
    RMDir /r "$INSTDIR\static"
    RMDir /r "$INSTDIR\data"
    RMDir /r "$INSTDIR\generated_images"
    
    ; Remove shortcuts
    Delete "$DESKTOP\VisionCraft Pro.lnk"
    RMDir /r "$SMPROGRAMS\VisionCraft Pro"
    
    ; Remove installation directory
    RMDir "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\VisionCraftPro"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VisionCraftPro"
SectionEnd

;--------------------------------
; Functions
Function .onInit
    ; Check for 64-bit Windows
    ${If} ${RunningX64}
        SetRegView 64
    ${Else}
        MessageBox MB_OK|MB_ICONSTOP "VisionCraft Pro requires a 64-bit version of Windows."
        Abort
    ${EndIf}
FunctionEnd
