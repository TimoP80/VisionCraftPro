"""
Detect and work with Python install managers (pyenv, asdf, etc.)
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def detect_python_manager():
    """Detect which Python install manager is being used"""
    print("🔍 Detecting Python Install Manager...")
    print("="*50)
    
    # Check pyenv
    stdout, stderr, code = run_command("pyenv --version")
    if code == 0:
        print(f"✅ Found pyenv: {stdout}")
        
        # List installed versions
        stdout, stderr, code = run_command("pyenv versions")
        print(f"Installed versions:\n{stdout}")
        
        # Check for 3.11
        if "3.11" in stdout:
            print("✅ Python 3.11 found in pyenv")
            return "pyenv", True
        else:
            print("❌ Python 3.11 not found in pyenv")
            return "pyenv", False
    
    # Check asdf
    stdout, stderr, code = run_command("asdf --version")
    if code == 0:
        print(f"✅ Found asdf: {stdout}")
        
        stdout, stderr, code = run_command("asdf list python")
        print(f"Installed Python versions:\n{stdout}")
        
        if "3.11" in stdout:
            print("✅ Python 3.11 found in asdf")
            return "asdf", True
        else:
            print("❌ Python 3.11 not found in asdf")
            return "asdf", False
    
    # Check for other managers
    managers = ["rye", "hatch", "pixi"]
    for manager in managers:
        stdout, stderr, code = run_command(f"{manager} --version")
        if code == 0:
            print(f"✅ Found {manager}: {stdout}")
            return manager, None
    
    print("❌ No Python install manager detected")
    return None, None

def install_python_311(manager):
    """Install Python 3.11 using the detected manager"""
    print(f"\n📦 Installing Python 3.11 using {manager}...")
    
    if manager == "pyenv":
        # Install Python 3.11.9
        print("Installing Python 3.11.9...")
        stdout, stderr, code = run_command("pyenv install 3.11.9")
        if code == 0:
            print("✅ Python 3.11.9 installed successfully")
            # Set as local version
            run_command("pyenv local 3.11.9")
            return True
        else:
            print(f"❌ Installation failed: {stderr}")
            return False
    
    elif manager == "asdf":
        print("Installing Python 3.11.9...")
        stdout, stderr, code = run_command("asdf install python 3.11.9")
        if code == 0:
            print("✅ Python 3.11.9 installed successfully")
            run_command("asdf local python 3.11.9")
            return True
        else:
            print(f"❌ Installation failed: {stderr}")
            return False
    
    return False

def setup_pytorch():
    """Setup PyTorch with CUDA"""
    print("\n🚀 Setting up PyTorch with CUDA...")
    
    # Check current Python version
    print(f"Current Python: {sys.version}")
    
    # Create virtual environment
    if not os.path.exists("venv_py311"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv_py311"], check=True)
    
    # Activate and install packages
    if os.name == "nt":
        venv_python = "venv_py311\\Scripts\\python"
        activate_cmd = "venv_py311\\Scripts\\activate"
    else:
        venv_python = "venv_py311/bin/python"
        activate_cmd = "source venv_py311/bin/activate"
    
    print(f"Using virtual environment: {venv_python}")
    
    # Install PyTorch
    print("Installing PyTorch with CUDA...")
    subprocess.run([venv_python, "-m", "pip", "install", "torch", "torchvision", 
                   "--index-url", "https://download.pytorch.org/whl/cu121"], check=True)
    
    # Install other dependencies
    packages = ["diffusers", "transformers", "accelerate", "fastapi", "uvicorn",
                "python-multipart", "pillow", "numpy", "opencv-python", 
                "bitsandbytes", "safetensors", "omegaconf", "gradio", "psutil"]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([venv_python, "-m", "pip", "install", package], check=True)
    
    # Test CUDA
    print("\n🧪 Testing CUDA support...")
    test_code = '''
import torch
print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:", "{:.2f} GB".format(torch.cuda.get_device_properties(0).total_memory / 1024**3))
else:
    print("❌ CUDA not available")
'''
    
    result = subprocess.run([venv_python, "-c", test_code], capture_output=True, text=True)
    print(result.stdout)
    
    return torch.cuda.is_available() if "CUDA available: True" in result.stdout else False

def main():
    print("🐍 Python Install Manager Setup for GTX 1070")
    print("="*60)
    
    # Detect manager
    manager, has_311 = detect_python_manager()
    
    if manager and has_311:
        print(f"\n✅ {manager} with Python 3.11 detected!")
        print("Setting up PyTorch...")
        if setup_pytorch():
            print("\n🎉 Success! Your GTX 1070 is ready!")
            print(f"\nTo run the app:")
            if os.name == "nt":
                print("venv_py311\\Scripts\\activate")
            else:
                print("source venv_py311/bin/activate")
            print("python app.py")
        else:
            print("\n❌ CUDA setup failed")
    
    elif manager and not has_311:
        print(f"\n📦 {manager} detected but Python 3.11 not installed")
        if install_python_311(manager):
            print("✅ Python 3.11 installed, setting up PyTorch...")
            if setup_pytorch():
                print("\n🎉 Success! Your GTX 1070 is ready!")
            else:
                print("\n❌ PyTorch setup failed")
        else:
            print("\n❌ Python 3.11 installation failed")
    
    else:
        print("\n❌ No Python install manager detected")
        print("Please install pyenv, asdf, or Python 3.11 manually")
        print("https://www.python.org/downloads/release/python-3119/")

if __name__ == "__main__":
    main()
