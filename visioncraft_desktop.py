#!/usr/bin/env python3
"""
VisionCraft Pro - Advanced Desktop Application
Professional AI Image Generator with Desktop Features
"""

import webview
import threading
import subprocess
import sys
import os
import time
import json
from pathlib import Path

class VisionCraftDesktop:
    def __init__(self):
        self.backend_process = None
        self.window = None
        self.config_file = "desktop_config.json"
        self.load_config()
    
    def load_config(self):
        """Load desktop configuration"""
        default_config = {
            "window_width": 1200,
            "window_height": 900,
            "window_x": None,
            "window_y": None,
            "always_on_top": False,
            "start_maximized": False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except:
            self.config = default_config
    
    def save_config(self):
        """Save desktop configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            
            # Start backend with output suppressed
            self.backend_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            print("✅ Backend started successfully")
            return True
        except Exception as e:
            print(f"❌ Backend failed to start: {e}")
            return False
    
    def create_window(self):
        """Create the main application window"""
        window_config = {
            'title': 'VisionCraft Pro - Professional AI Image Generator',
            'url': 'http://localhost:8000',
            'width': self.config.get("window_width", 1200),
            'height': self.config.get("window_height", 900),
            'resizable': True,
            'min_size': (800, 600),
            'frameless': False,
            'easy_drag': True,
            'on_top': self.config.get("always_on_top", False),
            'shadow': True,
            'text_select': False,
            'on_closed': self.on_closing
        }
        
        # Set window position if saved
        if self.config.get("window_x") and self.config.get("window_y"):
            window_config['x'] = self.config["window_x"]
            window_config['y'] = self.config["window_y"]
        
        # Create window (simplified without menu for compatibility)
        self.window = webview.create_window(**window_config)
        return self.window
    
    def run(self):
        """Run the desktop application"""
        print("🎨 VisionCraft Pro - Desktop Application")
        print("=" * 50)
        
        # Check dependencies
        if not os.path.exists("app.py"):
            print("❌ Error: app.py not found")
            input("Press Enter to exit...")
            return
        
        if not os.path.exists("static"):
            print("❌ Error: static folder not found")
            input("Press Enter to exit...")
            return
        
        # Start backend
        if not self.start_backend():
            input("Press Enter to exit...")
            return
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(4)
        
        # Create and run window
        try:
            window = self.create_window()
            print("🚀 Launching VisionCraft Pro Desktop...")
            webview.start()
        except Exception as e:
            print(f"❌ Error launching desktop app: {e}")
            if self.backend_process:
                self.backend_process.terminate()
            input("Press Enter to exit...")

def main():
    """Main entry point"""
    app = VisionCraftDesktop()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 VisionCraft Pro closed by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
