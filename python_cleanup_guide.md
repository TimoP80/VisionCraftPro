# Python Cleanup and Python 3.11 Installation Guide

## Overview
This guide will help you clean up all existing Python installations and install only Python 3.11 for optimal GTX 1070 performance with PyTorch CUDA.

## Why This Approach?
- **PyTorch CUDA builds** only support Python 3.10-3.12 (not 3.13/3.14)
- **Clean installation** avoids PATH conflicts
- **Single version** simplifies dependency management
- **GTX 1070 optimization** requires proper CUDA support

## Step 1: Uninstall All Python Versions

### Method 1: Windows Settings (Recommended)
1. Open **Windows Settings** → **Apps** → **Apps & features**
2. Search for "Python"
3. Uninstall all Python versions:
   - Python 3.13.x
   - Python 3.14.x
   - Python 3.12.x (if present)
   - Python 3.10.x (if present)
   - Python Launcher (py.exe)

### Method 2: Control Panel
1. Open **Control Panel** → **Programs and Features**
2. Find all Python installations
3. Uninstall each one

### Method 3: Python Install Manager
If you used pyenv, asdf, etc.:
```bash
pyenv uninstall --all  # Remove all versions
# Or uninstall specific versions
pyenv uninstall 3.13.9 3.14.3
```

## Step 2: Clean System Paths

After uninstalling, clean up PATH:
1. **Windows Settings** → **System** → **About** → **Advanced system settings**
2. Click **Environment Variables**
3. Under **System variables**, find **Path**
4. Remove any Python-related entries
5. Click **OK** to save

## Step 3: Install Python 3.11

### Download
1. Visit: https://www.python.org/downloads/release/python-3119/
2. Download: **Windows installer (64-bit)**

### Installation Steps
1. **Run installer as Administrator**
2. **IMPORTANT:** Check these options:
   - ✅ **Install for all users**
   - ✅ **Add Python 3.11 to PATH**
   - ✅ **Associate files with Python**
3. Click **Customize installation** (optional)
4. Ensure these features are selected:
   - ✅ **Documentation**
   - ✅ **pip**
   - ✅ **tcl/tk and IDLE**
   - ✅ **Python test suite**
   - ✅ **py launcher**
5. Click **Install**

## Step 4: Verify Installation

Open **new** Command Prompt and test:
```bash
python --version
# Should show: Python 3.11.x

pip --version
# Should show pip version

py --version
# Should show Python launcher version
```

## Step 5: Install PyTorch with CUDA

Run the automated script:
```bash
clean_python_install.bat
```

Or manually:
```bash
# Create virtual environment
python -m venv venv_py311

# Activate environment
venv_py311\Scripts\activate

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install diffusers transformers accelerate fastapi uvicorn python-multipart pillow numpy opencv-python bitsandbytes safetensors omegaconf gradio psutil

# Test CUDA
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## Step 6: Test GTX 1070

```bash
python -c "
import torch
print('PyTorch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('VRAM:', '{:.2f} GB'.format(torch.cuda.get_device_properties(0).total_memory / 1024**3))
else:
    print('❌ CUDA not available')
"
```

Expected output:
```
PyTorch: 2.1.0+cu121
CUDA available: True
GPU: NVIDIA GeForce GTX 1070
VRAM: 8.00 GB
```

## Step 7: Run the Image Generator

```bash
# Activate environment
venv_py311\Scripts\activate

# Run the app
python app.py
```

Or use the launcher:
```bash
start_py311.bat
```

## Troubleshooting

### "Python not found" Error
- Restart Command Prompt after installation
- Check PATH contains Python 3.11
- Try `py -3.11 --version`

### CUDA Not Available
- Update NVIDIA drivers
- Install CUDA toolkit 11.8+ (optional)
- Restart computer after driver installation

### Permission Errors
- Run Command Prompt as Administrator
- Install Python "for all users"

### Virtual Environment Issues
- Delete venv folder and recreate
- Ensure using correct Python version

## Final Verification

Run this test:
```bash
python check_system.py
```

Should show:
- ✅ Python 3.11.x
- ✅ PyTorch with CUDA support
- ✅ GTX 1070 detected
- ✅ 8GB VRAM available

## Benefits of Clean Installation

- **10-20x faster** image generation vs CPU
- **Stable dependencies** without version conflicts
- **Optimized GTX 1070 performance**
- **Real-time VRAM monitoring**
- **Automatic memory management**

After this setup, your GTX 1070 will generate 512x512 images in 2-5 seconds instead of 30-60 seconds on CPU!
