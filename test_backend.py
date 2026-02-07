#!/usr/bin/env python3
"""
Test backend startup to identify issues
"""

import subprocess
import sys
import os
import time

def test_backend_directly():
    """Test running backend directly"""
    print("🔧 Testing backend startup directly...")
    
    try:
        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run backend and capture output
        process = subprocess.run(
            [sys.executable, "app.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("📝 STDOUT:")
        print(process.stdout)
        
        print("📝 STDERR:")
        print(process.stderr)
        
        print(f"📊 Return code: {process.returncode}")
        
        return process.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Backend startup timed out (this might be good - means it's running)")
        return True
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

if __name__ == "__main__":
    test_backend_directly()
