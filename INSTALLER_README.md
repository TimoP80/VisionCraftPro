# VisionCraftPro Installer Guide

## Overview
This installer package provides a complete Windows installation solution for VisionCraftPro, an AI-powered image generation application.

## Files Created
- `installer.nsi` - NSIS installer script
- `build_installer.bat` - Build script to compile the installer
- `installer_config.json` - Configuration file for installer settings

## Prerequisites for Building
1. **NSIS (Nullsoft Scriptable Install System)** 3.0 or later
   - Download from: https://nsis.sourceforge.io/Download
   - Ensure NSIS is in your PATH or run build script from NSIS directory

2. **Icon file** (optional)
   - Place your application icon at `static/icon.ico`
   - If not present, a placeholder will be created

## Building the Installer
1. Run the build script:
   ```batch
   build_installer.bat
   ```

2. The script will:
   - Check for NSIS installation
   - Create LICENSE.txt if missing
   - Create placeholder icon if missing
   - Compile the installer script
   - Generate `VisionCraftPro_Setup_1.0.0.exe`

## Installer Features
- **Modern UI** with welcome page and license agreement
- **Component selection** (Core, Python check, shortcuts)
- **Registry integration** for Add/Remove Programs
- **Start Menu shortcuts** with documentation links
- **Desktop shortcut** option
- **Python version checking** (3.9+ required)
- **Complete uninstaller** with registry cleanup

## User Requirements
- Python 3.9 or higher
- NVIDIA GPU with 8GB+ VRAM (recommended)
- 16GB+ RAM (recommended)
- 10GB free disk space

## Installation Process
1. Run `VisionCraftPro_Setup_1.0.0.exe`
2. Accept license agreement
3. Select components to install
4. Choose installation directory (default: `C:\Program Files\VisionCraftPro`)
5. Complete installation

## Post-Installation
- Launch via Start Menu or Desktop shortcut
- Application will check Python compatibility on first run
- Generated images will be saved to `generated_images/` folder

## Troubleshooting
- **Python not found**: Install Python 3.9+ from python.org
- **Permission errors**: Run installer as Administrator
- **Missing dependencies**: Run `pip install -r requirements.txt` in install directory

## Customization
- Edit `installer.nsi` for UI changes
- Edit `installer_config.json` for configuration changes
- Update version numbers in both files for new releases
