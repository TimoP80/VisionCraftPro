#!/usr/bin/env python3
"""
VisionCraft Pro - Desktop Application
Professional AI Image Generator Desktop Version
"""

import webview
import threading
import subprocess
import sys
import os
import time
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    try:
        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start the backend server
        print("🎨 Starting VisionCraft Pro Backend...")
        subprocess.run([sys.executable, "app.py"], check=True)
    except Exception as e:
        print(f"❌ Backend failed to start: {e}")
        input("Press Enter to exit...")

def create_desktop_app():
    """Create and launch the desktop application"""
    
    # Configuration
    window_config = {
        'title': 'VisionCraft Pro - Professional AI Image Generator',
        'url': 'http://localhost:8000',
        'width': 1200,
        'height': 900,
        'resizable': True,
        'min_size': (800, 600),
        'frameless': False,
        'easy_drag': True,
        'on_top': False,
        'shadow': True,
        'vibrancy': False,
        'text_select': False,
        'edge': 'default'
    }
    
    # Create window
    window = webview.create_window(**window_config)
    
    # Start backend in separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start the webview
    print("🚀 Launching VisionCraft Pro Desktop...")
    webview.start(window)

def main():
    """Main entry point"""
    print("🎨 VisionCraft Pro - Desktop Application")
    print("=" * 50)
    
    # Check if backend file exists
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found in current directory")
        input("Press Enter to exit...")
        return
    
    # Check if static folder exists
    if not os.path.exists("static"):
        print("❌ Error: static folder not found")
        input("Press Enter to exit...")
        return
    
    try:
        create_desktop_app()
    except KeyboardInterrupt:
        print("\n👋 VisionCraft Pro closed by user")
    except Exception as e:
        print(f"❌ Error launching desktop app: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
