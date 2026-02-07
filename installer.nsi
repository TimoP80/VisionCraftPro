; VisionCraftPro Installer Script
; Requires NSIS 3.0 or later

!define APPNAME "VisionCraftPro"
!define VERSION "1.0.0"
!define PUBLISHER "VisionCraftPro Team"
!define URL "https://github.com/visioncraftpro"
!define EXECUTABLE "Launch_VisionCraft_Pro.bat"

; Include Modern UI
!include "MUI2.nsh"
!include "AccessControl.nsh"

; General settings
Name "${APPNAME}"
OutFile "${APPNAME}_Setup_${VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "InstallPath"
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Core Application" SecCore
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    ; Main application files
    File /r "*.py"
    File /r "static"
    File /r "generated_images"
    File "requirements.txt"
    File "package.json"
    File "package-lock.json"
    File "tailwind.config.js"
    File "postcss.config.js"
    File "${EXECUTABLE}"
    File "README.md"
    File "USER_GUIDE.md"
    File "API_DOCUMENTATION.md"
    File "CHANGELOG.md"
    
    ; Create directories
    CreateDirectory "$INSTDIR\generated_images"
    CreateDirectory "$INSTDIR\logs"
    
    ; Write installation files
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\${APPNAME}" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\${APPNAME}" "Version" "${VERSION}"
    WriteRegStr HKLM "Software\${APPNAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\${APPNAME}" "URL" "${URL}"
    
    ; Add uninstall information to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\${EXECUTABLE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${URL}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${EXECUTABLE}" "" "$INSTDIR\${EXECUTABLE}" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\User Guide.lnk" "$INSTDIR\USER_GUIDE.md" "" "$INSTDIR\USER_GUIDE.md" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXECUTABLE}" "" "$INSTDIR\${EXECUTABLE}" 0
    
    ; Set permissions for generated_images directory
    AccessControl::GrantOnFile "$INSTDIR\generated_images" "(BU)" "FullAccess"
SectionEnd

Section "Python Environment Check" SecPython
    SectionIn RO
    
    ; Check for Python installation
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
    ${If} $0 == ""
        ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
        ${If} $0 == ""
            ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.9\InstallPath" ""
            ${If} $0 == ""
                MessageBox MB_OK|MB_ICONEXCLAMATION "Python 3.9+ is required but was not found. Please install Python from python.org before running ${APPNAME}."
            ${EndIf}
        ${EndIf}
    ${EndIf}
    
    ; Create Python check script
    FileOpen $1 "$INSTDIR\check_python.py" w
    FileWrite $1 "import sys$\r$\n"
    FileWrite $1 "if sys.version_info >= (3, 9):$\r$\n"
    FileWrite $1 "    print('Python version OK:', sys.version)$\r$\n"
    FileWrite $1 "else:$\r$\n"
    FileWrite $1 "    print('Python version too old:', sys.version)$\r$\n"
    FileWrite $1 "    sys.exit(1)$\r$\n"
    FileClose $1
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXECUTABLE}" "" "$INSTDIR\${EXECUTABLE}" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${EXECUTABLE}" "" "$INSTDIR\${EXECUTABLE}" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\User Guide.lnk" "$INSTDIR\USER_GUIDE.md" "" "$INSTDIR\USER_GUIDE.md" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\API Documentation.lnk" "$INSTDIR\API_DOCUMENTATION.md" "" "$INSTDIR\API_DOCUMENTATION.md" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Install the core VisionCraftPro application files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} "Check for compatible Python installation."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a desktop shortcut for VisionCraftPro."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create Start Menu shortcuts for VisionCraftPro."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove files and directories
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APPNAME}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "Software\${APPNAME}"
    
    ; Remove self
    Delete "$INSTDIR\Uninstall.exe"
SectionEnd
