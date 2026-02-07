#!/usr/bin/env python3
"""
VisionCraft Pro - Simple Desktop Application
Professional AI Image Generator Desktop Version
"""

import webview
import threading
import subprocess
import sys
import os
import time
import requests

def start_backend():
    """Start the FastAPI backend server"""
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print("Starting backend server...")
        
        # Start backend and capture output in real-time
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start a thread to read output
        def read_output():
            for line in iter(backend_process.stdout.readline, ''):
                if line.strip():
                    print(f"Backend: {line.strip()}")
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        # Wait a moment and check if process is still running
        time.sleep(3)
        if backend_process.poll() is None:
            print("Backend process is running")
            return backend_process
        else:
            # Backend exited immediately, show error
            output, _ = backend_process.communicate()
            print(f"Backend failed to start:")
            print(output)
            return None
            
    except Exception as e:
        print(f"Backend failed to start: {e}")
        return None

def test_backend_connection():
    """Test if backend is responding"""
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            print("Backend is responding")
            return True
    except requests.exceptions.ConnectionError:
        print("Backend not ready yet...")
    except requests.exceptions.Timeout:
        print("Backend timeout...")
    except Exception as e:
        print(f"Connection test failed: {e}")
    return False

def wait_for_backend(max_wait=30):
    """Wait for backend to be ready"""
    print("Waiting for backend to be ready...")
    for i in range(max_wait):
        if test_backend_connection():
            return True
        time.sleep(1)
        if i % 5 == 0:
            print(f"Still waiting... ({i}/{max_wait}s)")
    
    print("Backend failed to start within timeout")
    return False

def main():
    """Main entry point"""
    print("VisionCraft Pro - Desktop Application")
    print("=" * 50)
    
    # Check dependencies
    if not os.path.exists("app.py"):
        print("Error: app.py not found")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists("static"):
        print("Error: static folder not found")
        input("Press Enter to exit...")
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        input("Press Enter to exit...")
        return
    
    # Wait for backend to be ready
    if not wait_for_backend(30):
        print("Backend failed to start properly")
        if backend_process:
            backend_process.terminate()
        input("Press Enter to exit...")
        return
    
    try:
        # Create window
        window = webview.create_window(
            title='VisionCraft Pro - Professional AI Image Generator',
            url='http://localhost:8000',
            width=1200,
            height=900,
            resizable=True,
            min_size=(800, 600),
            shadow=True
        )
        
        print("Launching VisionCraft Pro Desktop...")
        
        # Start the webview
        webview.start()
        
    except Exception as e:
        print(f"Error launching desktop app: {e}")
    finally:
        # Clean up backend process
        if backend_process:
            backend_process.terminate()
            print("Backend stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nVisionCraft Pro closed by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")
