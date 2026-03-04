#!/usr/bin/env python3
"""
Install AI packages for prompt enhancement
"""

import subprocess
import sys

def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully installed {package_name}")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def main():
    print("🚀 Installing AI packages for prompt enhancement...")
    print()
    
    packages = [
        "google-generativeai>=0.3.0",
        "openai>=1.0.0", 
        "anthropic>=0.7.0"
    ]
    
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print(f"📊 Installation Summary: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("🎉 All AI packages installed successfully!")
        print("🔄 Restart the server with: python app.py")
        print("🤖 Then test AI enhancement in the web interface!")
    else:
        print("⚠️  Some packages failed to install.")
        print("💡 Try installing manually:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()
