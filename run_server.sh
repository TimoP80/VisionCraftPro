#!/bin/bash
# VisionCraft Pro - Linux Server Launcher

echo -e "\033[1;34m🚀 Starting VisionCraft Pro Server...\033[0m"

# Ensure venv exists
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "\033[1;33m⚠️  Virtual environment not found. Running setup first...\033[0m"
    chmod +x setup.sh
    ./setup.sh
fi

# Activate virtual environment
source .venv/bin/activate

# Run the server
python3 visioncraft_server.py

if [ $? -ne 0 ]; then
    echo -e "\n\033[1;31m❌ VisionCraft Pro Server exited with an error.\033[0m"
fi
