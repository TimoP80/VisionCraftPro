"""
CUDA and GPU PyTorch Verification and Installation
Checks for CUDA availability and installs GPU PyTorch if needed

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import torch
import subprocess
import sys
import os
from typing import Dict, Any

class CudaChecker:
    """Verifies CUDA installation and GPU PyTorch availability"""
    
    def __init__(self):
        self.cuda_available = False
        self.gpu_torch_available = False
        self.cuda_version = None
        self.gpu_count = 0
        self.gpu_name = None
        self.system_python = sys.executable
        
    def check_cuda_availability(self) -> Dict[str, Any]:
        """Comprehensive CUDA and GPU PyTorch check"""
        results = {
            "cuda_available": False,
            "gpu_torch_available": False,
            "cuda_version": None,
            "gpu_count": 0,
            "gpu_name": None,
            "torch_version": torch.__version__,
            "torch_cuda_version": None,
            "recommendations": []
        }
        
        # Check CUDA installation
        try:
            if torch.cuda.is_available():
                results["cuda_available"] = True
                results["gpu_count"] = torch.cuda.device_count()
                results["gpu_name"] = torch.cuda.get_device_name(0) if results["gpu_count"] > 0 else None
                results["cuda_version"] = torch.version.cuda
                results["torch_cuda_version"] = torch.version.cuda
                
                # Test if GPU PyTorch is actually working
                try:
                    # Try a simple GPU operation
                    device = torch.device("cuda")
                    x = torch.randn(3, 3).to(device)
                    results["gpu_torch_available"] = True
                    print(f"[CUDA] GPU PyTorch is working properly")
                    print(f"[CUDA] GPU: {results['gpu_name']}")
                    print(f"[CUDA] CUDA Version: {results['cuda_version']}")
                    print(f"[CUDA] GPU Count: {results['gpu_count']}")
                except Exception as e:
                    print(f"[CUDA] GPU PyTorch test failed: {e}")
                    results["recommendations"].append("GPU PyTorch is not working despite CUDA detection")
                    results["recommendations"].append("Install GPU-enabled PyTorch")
            else:
                print("[CUDA] CUDA is not available")
                results["recommendations"].append("Install CUDA toolkit from NVIDIA")
                results["recommendations"].append("Ensure NVIDIA GPU drivers are up to date")
                
        except Exception as e:
            print(f"[CUDA] Error checking CUDA: {e}")
            results["recommendations"].append("Error checking CUDA installation")
        
        return results
    
    def install_gpu_pytorch(self) -> bool:
        """Install GPU-enabled PyTorch"""
        try:
            print("[CUDA] Installing GPU-enabled PyTorch...")
            print("[CUDA] This will replace CPU-only PyTorch with GPU version")
            
            # Get CUDA version for compatibility
            cuda_version = None
            try:
                import nvidia
                # Try to get CUDA version from nvidia-ml-py if available
                import pynvml
                pynvml.nvmlInit()
                cuda_version = pynvml.nvmlSystemGetDriverVersion()
                print(f"[CUDA] NVIDIA Driver Version: {cuda_version}")
            except:
                pass
            
            # Determine appropriate PyTorch version
            if cuda_version and "12." in cuda_version:
                # Use CUDA 12.1 wheels
                install_cmd = [
                    self.system_python, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", 
                    "--index-url", "https://download.pytorch.org/whl/cu121"
                ]
            else:
                # Use CUDA 11.8 wheels (more compatible)
                install_cmd = [
                    self.system_python, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", 
                    "--index-url", "https://download.pytorch.org/whl/cu118"
                ]
            
            print(f"[CUDA] Running: {' '.join(install_cmd)}")
            
            # Run installation
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[CUDA] GPU PyTorch installation completed successfully")
                print("[CUDA] Please restart the application to use GPU PyTorch")
                return True
            else:
                print(f"[CUDA] Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[CUDA] Error installing GPU PyTorch: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that GPU PyTorch is working after installation"""
        try:
            # Reimport torch to get updated version
            import importlib
            importlib.reload(torch)
            
            if torch.cuda.is_available():
                # Test GPU operation
                device = torch.device("cuda")
                x = torch.randn(3, 3).to(device)
                y = x + 1
                print("[CUDA] GPU PyTorch verification successful")
                return True
            else:
                print("[CUDA] GPU PyTorch still not available after installation")
                return False
                
        except Exception as e:
            print(f"[CUDA] Verification failed: {e}")
            return False
    
    def get_recommendations(self) -> list:
        """Get recommendations based on current setup"""
        recommendations = []
        
        if not torch.cuda.is_available():
            recommendations.extend([
                "1. Install NVIDIA CUDA Toolkit (11.8 or 12.1 recommended)",
                "2. Update NVIDIA GPU drivers to latest version",
                "3. Restart your computer after CUDA installation",
                "4. Install GPU-enabled PyTorch using this tool"
            ])
        else:
            if not self.gpu_torch_available:
                recommendations.extend([
                    "1. Install GPU-enabled PyTorch (CPU-only version detected)",
                    "2. This will replace current PyTorch with GPU version",
                    "3. Restart application after installation"
                ])
            else:
                recommendations.append("GPU PyTorch is properly configured!")
        
        return recommendations

def check_and_fix_cuda():
    """Main function to check and fix CUDA issues"""
    print("=" * 60)
    print("VisionCraft Pro - CUDA and GPU PyTorch Checker")
    print("=" * 60)
    
    checker = CudaChecker()
    
    # Check current status
    results = checker.check_cuda_availability()
    
    print(f"\n[CUDA] Current Status:")
    print(f"  CUDA Available: {results['cuda_available']}")
    print(f"  GPU PyTorch Available: {results['gpu_torch_available']}")
    print(f"  PyTorch Version: {results['torch_version']}")
    
    if results['cuda_available']:
        print(f"  CUDA Version: {results['cuda_version']}")
        print(f"  GPU Count: {results['gpu_count']}")
        print(f"  GPU Name: {results['gpu_name']}")
    
    # Show recommendations
    if results['recommendations']:
        print(f"\n[CUDA] Issues Found:")
        for rec in results['recommendations']:
            print(f"  - {rec}")
    
    # Try to fix issues
    if results['cuda_available'] and not results['gpu_torch_available']:
        print(f"\n[CUDA] Attempting to install GPU PyTorch...")
        if checker.install_gpu_pytorch():
            print(f"\n[CUDA] Installation completed. Please restart the application.")
            return True
        else:
            print(f"\n[CUDA] Installation failed. Please install manually:")
            print(f"  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
            return False
    elif not results['cuda_available']:
        print(f"\n[CUDA] CUDA not available. Please install NVIDIA CUDA Toolkit first.")
        return False
    else:
        print(f"\n[CUDA] Everything is working correctly!")
        return True

if __name__ == "__main__":
    check_and_fix_cuda()
