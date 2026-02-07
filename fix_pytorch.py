"""
PyTorch GPU Installation Fix Script
This script helps diagnose and fix PyTorch CUDA issues
"""

import subprocess
import sys
import os

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_current_installation():
    """Check current PyTorch installation"""
    print("=== Current PyTorch Installation ===")
    
    success, output, error = run_command("python -c \"import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')\"")
    
    if success:
        print(output)
        if "CUDA available: False" in output:
            print("❌ PyTorch is CPU-only")
            return False
        else:
            print("✅ PyTorch has CUDA support")
            return True
    else:
        print(f"❌ Error checking PyTorch: {error}")
        return False

def install_gpu_pytorch():
    """Install GPU-supported PyTorch"""
    print("\n=== Installing GPU-Supported PyTorch ===")
    
    # Uninstall current PyTorch
    print("Removing current PyTorch...")
    success, _, error = run_command("pip uninstall torch torchvision -y")
    if not success:
        print(f"Warning: Could not uninstall PyTorch: {error}")
    
    # Install GPU version
    print("Installing PyTorch with CUDA 12.1 support...")
    cmd = "pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"
    success, output, error = run_command(cmd, capture_output=False)
    
    if success:
        print("✅ PyTorch GPU installation completed")
        return True
    else:
        print(f"❌ Installation failed: {error}")
        return False

def test_gpu_pytorch():
    """Test GPU PyTorch installation"""
    print("\n=== Testing GPU PyTorch ===")
    
    test_code = '''
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"VRAM total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("❌ CUDA not available")
'''
    
    success, output, error = run_command(f'python -c "{test_code}"')
    if success:
        print(output)
        return torch.cuda.is_available() if "CUDA available: True" in output else False
    else:
        print(f"❌ Test failed: {error}")
        return False

def main():
    print("🔧 PyTorch GPU Installation Fix Tool")
    print("=====================================")
    
    # Check current installation
    has_cuda = check_current_installation()
    
    if not has_cuda:
        print("\n❌ Current PyTorch installation is CPU-only")
        response = input("Do you want to install GPU-supported PyTorch? (y/n): ")
        
        if response.lower() == 'y':
            if install_gpu_pytorch():
                if test_gpu_pytorch():
                    print("\n✅ Success! PyTorch now has CUDA support")
                    print("You can now run: python app.py")
                else:
                    print("\n⚠️  Installation completed but CUDA test failed")
                    print("Please check your NVIDIA drivers and CUDA installation")
            else:
                print("\n❌ Installation failed")
                print("Please try manual installation:")
                print("pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        else:
            print("Installation cancelled. Keeping current CPU-only PyTorch.")
    else:
        print("\n✅ PyTorch already has CUDA support - no action needed")

if __name__ == "__main__":
    main()
