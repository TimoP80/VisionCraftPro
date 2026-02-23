#!/bin/bash

# VisionCraft Pro - Linux Setup
set -e

echo -e "\n\033[1;32m╔══════════════════════════════════════════════════════════════╗"
echo -e "║                VisionCraft Pro - Setup Process               ║"
echo -e "╚══════════════════════════════════════════════════════════════╝\033[0m\n"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m❌ Python3 not found! Please install Python 3.9 or higher.\033[0m"
    exit 1
fi

# Check for venv module (common missing piece on Ubuntu/Debian)
if ! python3 -c "import venv" &> /dev/null; then
    echo -e "\033[1;31m❌ python3-venv is not installed.\033[0m"
    echo -e "Please run: \033[1;33msudo apt-get update && sudo apt-get install python3-venv\033[0m"
    exit 1
fi

echo -e "\033[1;34m🐍 Python detected. Starting setup script...\033[0m"
python3 vcp_setup.py

if [ $? -ne 0 ]; then
    echo -e "\n\033[1;31m❌ Setup failed. Please check the errors above.\033[0m"
    exit 1
fi

chmod +x run.sh

echo -e "\n\033[1;32m✅ Setup process finished.\033[0m"
echo -e "🚀 Use \033[1;33m./run.sh\033[0m to start the application.\n"
