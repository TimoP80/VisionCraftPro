"""
Manual installation script for Python 3.11 + PyTorch CUDA
Run this with Python 3.11 directly
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and show progress"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error code {e.returncode}")
        return False

def main():
    print("🚀 Manual PyTorch CUDA Installation for GTX 1070")
    print("="*60)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"Python version: {python_version}")
    
    if python_version != "3.11":
        print("❌ This script requires Python 3.11")
        print("Please run this script with Python 3.11:")
        print("python3.11 manual_install.py")
        return
    
    print("✅ Python 3.11 detected")
    
    # Create virtual environment
    if not os.path.exists("venv_py311"):
        print("\n📦 Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv_py311", "Virtual environment creation"):
            return
    
    # Activate and install packages
    venv_python = os.path.join("venv_py311", "Scripts", "python.exe" if os.name == "nt" else "bin/python")
    
    print(f"\n🔧 Using virtual environment Python: {venv_python}")
    
    # Install PyTorch with CUDA
    if not run_command(f'"{venv_python}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121', "PyTorch with CUDA"):
        return
    
    # Install other dependencies
    packages = [
        "diffusers",
        "transformers", 
        "accelerate",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pillow",
        "numpy",
        "opencv-python",
        "bitsandbytes",
        "safetensors",
        "omegaconf",
        "gradio",
        "psutil"
    ]
    
    for package in packages:
        if not run_command(f'"{venv_python}" -m pip install {package}', f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    # Test CUDA
    print("\n🧪 Testing CUDA support...")
    test_code = '''
import torch
print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:", "{:.2f} GB".format(torch.cuda.get_device_properties(0).total_memory / 1024**3))
else:
    print("❌ CUDA not available")
'''
    
    try:
        result = subprocess.run([venv_python, "-c", test_code], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 Installation complete!")
    print("\nTo run the app:")
    print("1. Activate virtual environment:")
    if os.name == "nt":
        print("   venv_py311\\Scripts\\activate")
    else:
        print("   source venv_py311/bin/activate")
    print("2. Run the app:")
    print("   python app.py")
    print("="*60)

if __name__ == "__main__":
    main()
