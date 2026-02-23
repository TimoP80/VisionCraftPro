#!/bin/bash

# VisionCraft Pro - Linux Launcher

echo -e "\033[1;34m🚀 Starting VisionCraft Pro...\033[0m"

if [ ! -f ".venv/bin/activate" ]; then
    echo -e "\033[1;33m⚠️  Virtual environment not found. Running setup first...\033[0m"
    chmod +x setup.sh
    ./setup.sh
fi

# Activate virtual environment
source .venv/bin/activate

# Run the app
python3 minimal_desktop.py

if [ $? -ne 0 ]; then
    echo -e "\n\033[1;31m❌ VisionCraft Pro exited with an error.\033[0m"
fi
