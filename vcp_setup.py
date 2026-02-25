#!/usr/bin/env python3
"""
VisionCraft Pro - Unified Setup Script
Handles environment creation, dependency installation, and directory initialization.
Compatible with Windows and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
import json

def print_banner():
    print("\n" + "="*60)
    print(" [VCP] VisionCraft Pro - Automatic Setup")
    print("="*60 + "\n")

def run_command(cmd, shell=True):
    """Run a command and return True if successful"""
    try:
        subprocess.run(cmd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_venv_path():
    """Return the platform-specific path to the virtual environment's Python"""
    if platform.system() == "Windows":
        return os.path.join(".venv", "Scripts", "python.exe")
    else:
        return os.path.join(".venv", "bin", "python")

def check_python_version():
    """Verify Python version is 3.9+"""
    major, minor = sys.version_info[:2]
    print(f"Checking Python version: {major}.{minor}")
    if (major == 3 and minor >= 9) or major > 3:
        print("[PASS] Python version acceptable.")
        return True
    else:
        print("[FAIL] VisionCraft Pro requires Python 3.9 or higher.")
        return False

def create_venv():
    """Create a virtual environment if it doesn't exist"""
    if os.path.exists(".venv"):
        print("[PASS] Virtual environment already exists.")
        return True
    
    print("[INIT] Creating virtual environment (.venv)...")
    if run_command(f"{sys.executable} -m venv .venv"):
        print("[PASS] Virtual environment created successfully.")
        return True
    else:
        print("[FAIL] Failed to create virtual environment.")
        return False

def install_dependencies():
    """Install required packages from requirements.txt"""
    venv_python = get_venv_path()
    
    # Check for NVIDIA GPU
    has_gpu = False
    try:
        # 1. Check if nvidia-smi is in PATH
        res = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if res.returncode == 0:
            has_gpu = True
        
        # 2. Check common installation paths on Windows if not in PATH
        if not has_gpu and platform.system() == "Windows":
            common_paths = [
                os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "nvidia-smi.exe"),
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "NVIDIA Corporation", "NVSMI", "nvidia-smi.exe"),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    has_gpu = True
                    break
    except:
        pass

    print(f"[INFO] Hardware detection: NVIDIA GPU {'found' if has_gpu else 'not found'}")

    # Installation strategy
    print("[DEPS] Installing dependencies (this may take a few minutes)...")
    
    # 1. Update pip
    run_command(f'"{venv_python}" -m pip install --upgrade pip')

    # 2. Install PyTorch (GPU optimized if found)
    if has_gpu:
        print("[DEPS] Installing GPU-optimized PyTorch (CUDA 12.1)...")
        run_command(f'"{venv_python}" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121')
    else:
        print("[WARN] Installing standard PyTorch (CPU only)...")
        run_command(f'"{venv_python}" -m pip install torch torchvision torchaudio')

    # 3. Install other requirements
    if os.path.exists("requirements.txt"):
        print("[DEPS] Installing requirements from requirements.txt...")
        if run_command(f'"{venv_python}" -m pip install -r requirements.txt'):
            print("[PASS] Requirements installed.")
        else:
            print("[FAIL] Some requirements failed to install.")
    
    # 4. Install PyWebView separately as it's critical for the desktop app
    print("[DEPS] Ensuring PyWebView is installed...")
    run_command(f'"{venv_python}" -m pip install pywebview')

def init_directories():
    """Create necessary directories and Fix permissions on Linux"""
    dirs = ["generated_images", "generated_images/images", "static"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"[FILE] Created directory: {d}")
        
        # On Linux, ensure the directory is writable
        if platform.system() != "Windows":
            try:
                # Grant read/write/execute permissions to current user
                os.chmod(d, 0o775)
                print(f"[FILE] Set permissions for: {d}")
            except Exception as e:
                print(f"[WARN] Could not set permissions for {d}: {e}")

    # Explicitly check/fix database file if it exists
    db_path = os.path.join("generated_images", "gallery.db")
    if os.path.exists(db_path) and platform.system() != "Windows":
        try:
            os.chmod(db_path, 0o664)
            print(f"[FILE] Set permissions for: {db_path}")
        except Exception as e:
            print(f"[WARN] Could not set permissions for {db_path}: {e}")

    print("[PASS] Directory initialization complete.")

def verify_installation():
    """Post-install verification"""
    print("\n[TEST] Verifying installation...")
    venv_python = get_venv_path()
    
    test_code = """
import torch
import webview
import fastapi
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
print('[PASS] Core dependencies successfully imported.')
"""
    
    try:
        subprocess.run([venv_python, "-c", test_code], check=True, text=True)
        print("[PASS] Verification successful!")
        return True
    except:
        print("[FAIL] Verification failed. Please check the errors above.")
        return False

def main():
    print_banner()
    
    if not check_python_version():
        sys.exit(1)
        
    init_directories()
    
    if not create_venv():
        sys.exit(1)
        
    install_dependencies()
    
    if verify_installation():
        print("\n" + "="*60)
        print(" [DONE] VisionCraft Pro Setup Complete!")
        print(f" You can now run the application using 'run.bat' (Windows) or './run.sh' (Linux).")
        print("="*60 + "\n")
    else:
        print("\n[WARN] Setup completed with warnings. Some features might not work as expected.")

if __name__ == "__main__":
    main()
