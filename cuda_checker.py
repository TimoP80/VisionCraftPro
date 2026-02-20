"""
CUDA Checker for VisionCraft Pro
Check CUDA availability and GPU PyTorch installation
"""

import subprocess
import sys
import platform
import os
from typing import Dict, List, Optional

class CudaChecker:
    """Check CUDA availability and GPU PyTorch installation"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict:
        """Get basic system information"""
        return {
            "platform": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version
        }
    
    def check_cuda_availability(self) -> Dict:
        """Check CUDA availability and GPU PyTorch"""
        results = {
            "cuda_available": False,
            "gpu_torch_available": False,
            "cuda_version": None,
            "gpu_count": 0,
            "gpu_names": [],
            "pytorch_version": None,
            "recommendations": []
        }
        
        try:
            # Check PyTorch CUDA availability
            import torch
            results["pytorch_version"] = torch.__version__
            results["cuda_available"] = torch.cuda.is_available()
            
            if results["cuda_available"]:
                results["cuda_version"] = torch.version.cuda
                results["gpu_count"] = torch.cuda.device_count()
                results["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(results["gpu_count"])]
                results["gpu_torch_available"] = True
            else:
                # CUDA not available via PyTorch
                results["recommendations"].append("PyTorch CUDA not available")
                
                # Check if CUDA is installed on system
                cuda_version = self._check_system_cuda()
                if cuda_version:
                    results["cuda_version"] = cuda_version
                    results["recommendations"].append("CUDA detected but PyTorch GPU version not installed")
                else:
                    results["recommendations"].append("CUDA not detected on system")
            
        except ImportError:
            results["recommendations"].append("PyTorch not installed")
        
        return results
    
    def _check_system_cuda(self) -> Optional[str]:
        """Check if CUDA is installed on system"""
        try:
            if self.system_info["platform"] == "Windows":
                # Check nvidia-smi on Windows
                result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Parse CUDA version from nvidia-smi output
                    for line in result.stdout.split('\n'):
                        if "CUDA Version:" in line:
                            return line.split("CUDA Version:")[1].strip().split()[0]
            else:
                # Check nvcc on Linux/Mac
                result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Parse CUDA version
                    for line in result.stdout.split('\n'):
                        if "release" in line:
                            return line.split("release")[-1].strip().split(",")[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def install_gpu_pytorch(self) -> bool:
        """Attempt to install GPU PyTorch"""
        try:
            print("[CUDA] Installing GPU PyTorch...")
            
            # Determine the appropriate command based on system
            if self.system_info["platform"] == "Windows":
                cmd = [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu118"]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu118"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("[CUDA] GPU PyTorch installation completed successfully")
                return True
            else:
                print(f"[CUDA] Installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[CUDA] Installation timed out")
            return False
        except Exception as e:
            print(f"[CUDA] Installation error: {e}")
            return False
    
    def get_gpu_info(self) -> Dict:
        """Get detailed GPU information"""
        gpu_info = {
            "gpus": [],
            "total_memory_gb": 0,
            "driver_version": None,
            "cuda_version": None
        }
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["cuda_version"] = torch.version.cuda
                gpu_info["driver_version"] = "Unknown"  # Would need nvidia-ml-py for this
                
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    gpu_memory_gb = props.total_memory / (1024**3)
                    
                    gpu_info["gpus"].append({
                        "id": i,
                        "name": props.name,
                        "memory_gb": gpu_memory_gb,
                        "compute_capability": f"{props.major}.{props.minor}",
                        "multiprocessor_count": props.multi_processor_count
                    })
                    
                    gpu_info["total_memory_gb"] += gpu_memory_gb
        
        except ImportError:
            pass
        
        return gpu_info
    
    def check_compatibility(self) -> Dict:
        """Check system compatibility with AI models"""
        compatibility = {
            "compatible": False,
            "issues": [],
            "recommendations": [],
            "optimal_settings": {}
        }
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                total_memory = 0
                
                for i in range(gpu_count):
                    props = torch.cuda.get_device_properties(i)
                    total_memory += props.total_memory / (1024**3)
                
                # Check if we have enough VRAM
                if total_memory >= 8:
                    compatibility["compatible"] = True
                    compatibility["optimal_settings"] = {
                        "default_steps": 20,
                        "max_steps": 50,
                        "default_guidance": 7.5,
                        "max_resolution": (1024, 1024) if total_memory >= 12 else (512, 512)
                    }
                elif total_memory >= 4:
                    compatibility["compatible"] = True
                    compatibility["issues"].append("Limited VRAM - may need to use smaller images")
                    compatibility["recommendations"].append("Use 512x512 resolution for best performance")
                    compatibility["optimal_settings"] = {
                        "default_steps": 15,
                        "max_steps": 30,
                        "default_guidance": 7.0,
                        "max_resolution": (512, 512)
                    }
                else:
                    compatibility["compatible"] = False
                    compatibility["issues"].append("Insufficient VRAM for AI generation")
                    compatibility["recommendations"].append("Consider using CPU-only mode or upgrading GPU")
            else:
                compatibility["compatible"] = False
                compatibility["issues"].append("CUDA not available")
                compatibility["recommendations"].append("Install GPU PyTorch or use CPU-only mode")
                
        except ImportError:
            compatibility["compatible"] = False
            compatibility["issues"].append("PyTorch not installed")
            compatibility["recommendations"].append("Install PyTorch")
        
        return compatibility
    
    def print_system_info(self):
        """Print comprehensive system information"""
        print("[CUDA] System Information:")
        print(f"  Platform: {self.system_info['platform']}")
        print(f"  Machine: {self.system_info['machine']}")
        print(f"  Python: {self.system_info['python_version'].split()[0]}")
        
        # Check CUDA
        cuda_results = self.check_cuda_availability()
        print(f"\n[CUDA] Status:")
        print(f"  CUDA Available: {cuda_results['cuda_available']}")
        print(f"  GPU PyTorch: {cuda_results['gpu_torch_available']}")
        print(f"  CUDA Version: {cuda_results['cuda_version']}")
        print(f"  GPU Count: {cuda_results['gpu_count']}")
        
        if cuda_results['gpu_names']:
            for i, name in enumerate(cuda_results['gpu_names']):
                print(f"  GPU {i}: {name}")
        
        # GPU Info
        gpu_info = self.get_gpu_info()
        if gpu_info['gpus']:
            print(f"\n[GPU] Details:")
            for gpu in gpu_info['gpus']:
                print(f"  {gpu['name']}: {gpu['memory_gb']:.1f}GB VRAM")
        
        # Compatibility
        compat = self.check_compatibility()
        print(f"\n[COMPATIBILITY] Status: {'✅ Compatible' if compat['compatible'] else '❌ Not Compatible'}")
        
        if compat['issues']:
            print(f"  Issues:")
            for issue in compat['issues']:
                print(f"    - {issue}")
        
        if compat['recommendations']:
            print(f"  Recommendations:")
            for rec in compat['recommendations']:
                print(f"    - {rec}")

# Example usage
if __name__ == "__main__":
    checker = CudaChecker()
    checker.print_system_info()
