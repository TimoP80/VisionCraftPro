#!/usr/bin/env python3
"""
VisionCraft Pro - Robust Desktop Application
Professional AI Image Generator Desktop Version
"""

import webview
import subprocess
import sys
import os
import time
import threading

def start_backend_with_output():
    """Start backend and show all output"""
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print("🔧 Starting backend server...")
        
        # Start backend normally (showing output)
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'  # Ensure real-time output
        
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Function to read and print output
        def print_output():
            while True:
                line = backend_process.stdout.readline()
                if not line:
                    break
                if line.strip():
                    print(f"📝 Backend: {line.strip()}")
        
        # Start output reader thread
        output_thread = threading.Thread(target=print_output, daemon=True)
        output_thread.start()
        
        return backend_process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def wait_for_user_or_timeout(backend_process, timeout=60):
    """Wait for user to press Enter or timeout"""
    print(f"\n⏳ Waiting {timeout} seconds for backend to start...")
    print("📝 Press Enter now to open the desktop window (if backend is ready)")
    print("📝 Or wait for automatic detection...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check if backend is still running
        if backend_process.poll() is not None:
            print("❌ Backend process stopped unexpectedly")
            return False
        
        # Try to check if server is responding
        try:
            import requests
            response = requests.get("http://localhost:8000/status", timeout=1)
            if response.status_code == 200:
                print("✅ Backend is responding!")
                return True
        except:
            pass
        
        # Check for user input (non-blocking)
        try:
            import msvcrt
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':  # Enter key
                    print("🚀 User requested to open window...")
                    return True
        except:
            # Fallback for non-Windows or if msvcrt not available
            pass
        
        time.sleep(1)
        
        # Show progress
        elapsed = int(time.time() - start_time)
        if elapsed % 5 == 0 and elapsed > 0:
            print(f"⏳ Still waiting... ({elapsed}/{timeout}s)")
    
    print("⏰ Timeout reached, trying anyway...")
    return True

def main():
    """Main entry point"""
    print("🎨 VisionCraft Pro - Robust Desktop Application")
    print("=" * 60)
    
    # Check files
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists("static"):
        print("❌ Error: static folder not found")
        input("Press Enter to exit...")
        return
    
    # Start backend
    backend_process = start_backend_with_output()
    if not backend_process:
        input("Press Enter to exit...")
        return
    
    try:
        # Wait for backend or user input
        if wait_for_user_or_timeout(backend_process, 60):
            print("🚀 Opening desktop window...")
            
            # Create and show window
            window = webview.create_window(
                title='VisionCraft Pro - Professional AI Image Generator',
                url='http://localhost:8000',
                width=1200,
                height=900,
                resizable=True,
                min_size=(800, 600),
                shadow=True
            )
            
            webview.start()
        else:
            print("❌ Backend failed to start properly")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if backend_process:
            backend_process.terminate()
            print("👋 Backend stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 VisionCraft Pro closed by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")
