"""
Comprehensive CUDA Diagnostic Tool
Helps identify and resolve CUDA installation issues

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import subprocess
import sys
import os
import platform
from typing import Dict, List, Any

class CudaDiagnostic:
    """Comprehensive CUDA diagnostic and repair tool"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.issues = []
        self.recommendations = []
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Gather basic system information"""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_executable": sys.executable
        }
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run comprehensive CUDA diagnostic"""
        print("=" * 70)
        print("VisionCraft Pro - Comprehensive CUDA Diagnostic")
        print("=" * 70)
        
        results = {
            "system_info": self.system_info,
            "nvidia_driver": self._check_nvidia_driver(),
            "cuda_installation": self._check_cuda_installation(),
            "pytorch_cuda": self._check_pytorch_cuda(),
            "gpu_info": self._get_gpu_info(),
            "environment_variables": self._check_environment_variables(),
            "path_check": self._check_system_path(),
            "issues": [],
            "recommendations": []
        }
        
        # Analyze results and generate recommendations
        self._analyze_results(results)
        
        # Print results
        self._print_diagnostic_results(results)
        
        return results
    
    def _check_nvidia_driver(self) -> Dict[str, Any]:
        """Check NVIDIA driver installation"""
        print("\n🔍 Checking NVIDIA Driver...")
        
        result = {
            "installed": False,
            "version": None,
            "error": None
        }
        
        try:
            # Try nvidia-smi command
            if self.system_info["platform"] == "Windows":
                # Windows
                cmd = ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader,nounits"]
            else:
                # Linux/Mac
                cmd = ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader,nounits"]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if process.returncode == 0:
                driver_version = process.stdout.strip()
                result["installed"] = True
                result["version"] = driver_version
                print(f"✅ NVIDIA Driver installed: {driver_version}")
            else:
                result["error"] = process.stderr
                print(f"❌ NVIDIA Driver not found or not working")
                self.issues.append("NVIDIA driver not installed or not working")
                
        except subprocess.TimeoutExpired:
            result["error"] = "Command timed out"
            print(f"❌ nvidia-smi command timed out")
            self.issues.append("nvidia-smi command not responding")
        except FileNotFoundError:
            result["error"] = "nvidia-smi not found"
            print(f"❌ nvidia-smi not found in PATH")
            self.issues.append("nvidia-smi not found in system PATH")
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error checking NVIDIA driver: {e}")
            self.issues.append(f"Error checking NVIDIA driver: {e}")
        
        return result
    
    def _check_cuda_installation(self) -> Dict[str, Any]:
        """Check CUDA toolkit installation"""
        print("\n🔍 Checking CUDA Toolkit...")
        
        result = {
            "installed": False,
            "version": None,
            "path": None,
            "error": None
        }
        
        try:
            # Try nvcc command
            if self.system_info["platform"] == "Windows":
                cmd = ["nvcc", "--version"]
            else:
                cmd = ["nvcc", "--version"]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if process.returncode == 0:
                # Parse version from output
                output = process.stdout
                for line in output.split('\n'):
                    if 'release' in line.lower() or 'version' in line.lower():
                        # Extract version number
                        import re
                        version_match = re.search(r'(\d+\.\d+)', line)
                        if version_match:
                            result["version"] = version_match.group(1)
                            break
                
                result["installed"] = True
                print(f"✅ CUDA Toolkit installed: {result['version']}")
            else:
                result["error"] = process.stderr
                print(f"❌ CUDA Toolkit not found")
                self.issues.append("CUDA Toolkit not installed")
                
        except subprocess.TimeoutExpired:
            result["error"] = "Command timed out"
            print(f"❌ nvcc command timed out")
            self.issues.append("nvcc command not responding")
        except FileNotFoundError:
            result["error"] = "nvcc not found"
            print(f"❌ nvcc not found in PATH")
            self.issues.append("nvcc not found in system PATH")
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error checking CUDA: {e}")
            self.issues.append(f"Error checking CUDA: {e}")
        
        return result
    
    def _check_pytorch_cuda(self) -> Dict[str, Any]:
        """Check PyTorch CUDA support"""
        print("\n🔍 Checking PyTorch CUDA Support...")
        
        result = {
            "torch_version": None,
            "cuda_available": False,
            "cuda_version": None,
            "gpu_count": 0,
            "gpu_names": [],
            "error": None
        }
        
        try:
            import torch
            result["torch_version"] = torch.__version__
            
            if torch.cuda.is_available():
                result["cuda_available"] = True
                result["cuda_version"] = torch.version.cuda
                result["gpu_count"] = torch.cuda.device_count()
                
                # Get GPU names
                for i in range(result["gpu_count"]):
                    gpu_name = torch.cuda.get_device_name(i)
                    result["gpu_names"].append(gpu_name)
                
                print(f"✅ PyTorch CUDA support available")
                print(f"   PyTorch Version: {result['torch_version']}")
                print(f"   CUDA Version: {result['cuda_version']}")
                print(f"   GPU Count: {result['gpu_count']}")
                for i, name in enumerate(result["gpu_names"]):
                    print(f"   GPU {i}: {name}")
                
                # Test GPU operation
                try:
                    device = torch.device("cuda")
                    x = torch.randn(3, 3).to(device)
                    y = x + 1
                    print(f"✅ GPU operation test passed")
                except Exception as e:
                    print(f"❌ GPU operation test failed: {e}")
                    self.issues.append(f"GPU operation test failed: {e}")
                    result["error"] = f"GPU operation test failed: {e}"
            else:
                print(f"❌ PyTorch CUDA not available")
                print(f"   PyTorch Version: {result['torch_version']}")
                self.issues.append("PyTorch CUDA not available")
                
        except ImportError:
            result["error"] = "PyTorch not installed"
            print(f"❌ PyTorch not installed")
            self.issues.append("PyTorch not installed")
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error checking PyTorch: {e}")
            self.issues.append(f"Error checking PyTorch: {e}")
        
        return result
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get detailed GPU information"""
        print("\n🔍 Getting GPU Information...")
        
        result = {
            "gpus": [],
            "error": None
        }
        
        try:
            if self.system_info["platform"] == "Windows":
                cmd = ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"]
            else:
                cmd = ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        parts = line.split(', ')
                        if len(parts) >= 6:
                            gpu_info = {
                                "id": i,
                                "name": parts[0].strip(),
                                "memory_total_mb": int(parts[1].strip()),
                                "memory_used_mb": int(parts[2].strip()),
                                "memory_free_mb": int(parts[3].strip()),
                                "utilization_percent": int(parts[4].strip()),
                                "temperature_c": int(parts[5].strip())
                            }
                            result["gpus"].append(gpu_info)
                
                for gpu in result["gpus"]:
                    print(f"✅ GPU {gpu['id']}: {gpu['name']}")
                    print(f"   Memory: {gpu['memory_used_mb']}MB / {gpu['memory_total_mb']}MB ({gpu['memory_free_mb']}MB free)")
                    print(f"   Utilization: {gpu['utilization_percent']}%")
                    print(f"   Temperature: {gpu['temperature_c']}°C")
            else:
                result["error"] = process.stderr
                print(f"❌ Could not get GPU info")
                
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error getting GPU info: {e}")
        
        return result
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """Check CUDA-related environment variables"""
        print("\n🔍 Checking Environment Variables...")
        
        result = {
            "cuda_path": os.environ.get("CUDA_PATH", None),
            "cuda_home": os.environ.get("CUDA_HOME", None),
            "cuda_root": os.environ.get("CUDA_ROOT", None),
            "path_contains_cuda": False
        }
        
        # Check if PATH contains CUDA
        path_env = os.environ.get("PATH", "")
        cuda_paths = ["cuda", "CUDA"]
        result["path_contains_cuda"] = any(cuda_path in path_env for cuda_path in cuda_paths)
        
        print(f"   CUDA_PATH: {result['cuda_path'] or 'Not set'}")
        print(f"   CUDA_HOME: {result['cuda_home'] or 'Not set'}")
        print(f"   CUDA_ROOT: {result['cuda_root'] or 'Not set'}")
        print(f"   PATH contains CUDA: {'Yes' if result['path_contains_cuda'] else 'No'}")
        
        return result
    
    def _check_system_path(self) -> Dict[str, Any]:
        """Check system PATH for CUDA and NVIDIA tools"""
        print("\n🔍 Checking System PATH...")
        
        result = {
            "path_entries": [],
            "cuda_found": False,
            "nvidia_found": False
        }
        
        path_env = os.environ.get("PATH", "")
        path_entries = path_env.split(os.pathsep)
        
        for entry in path_entries:
            entry_clean = entry.strip()
            if entry_clean:
                result["path_entries"].append(entry_clean)
                
                if "cuda" in entry_clean.lower():
                    result["cuda_found"] = True
                    print(f"   Found CUDA path: {entry_clean}")
                
                if "nvidia" in entry_clean.lower():
                    result["nvidia_found"] = True
                    print(f"   Found NVIDIA path: {entry_clean}")
        
        if not result["cuda_found"] and not result["nvidia_found"]:
            print(f"   No CUDA or NVIDIA paths found in PATH")
            self.issues.append("No CUDA or NVIDIA paths in system PATH")
        
        return result
    
    def _analyze_results(self, results: Dict[str, Any]):
        """Analyze diagnostic results and generate recommendations"""
        print("\n🔍 Analyzing Results...")
        
        # Check NVIDIA driver
        if not results["nvidia_driver"]["installed"]:
            self.recommendations.extend([
                "1. Install NVIDIA GPU drivers from https://www.nvidia.com/drivers",
                "2. Download the latest driver for your GPU model",
                "3. Restart your computer after installation",
                "4. Verify installation with 'nvidia-smi' command"
            ])
        
        # Check CUDA toolkit
        elif not results["cuda_installation"]["installed"]:
            self.recommendations.extend([
                "1. Install CUDA Toolkit from https://developer.nvidia.com/cuda-downloads",
                "2. Choose CUDA 11.8 or 12.1 (recommended for PyTorch)",
                "3. Follow installation instructions carefully",
                "4. Add CUDA to system PATH during installation"
            ])
        
        # Check PyTorch
        if not results["pytorch_cuda"]["cuda_available"]:
            if results["pytorch_cuda"]["torch_version"]:
                self.recommendations.extend([
                    "1. Current PyTorch is CPU-only version",
                    "2. Install GPU PyTorch with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
                    "3. Or use CUDA 11.8: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
                    "4. Restart your Python application after installation"
                ])
            else:
                self.recommendations.extend([
                    "1. Install PyTorch first: pip install torch torchvision torchaudio",
                    "2. Then install GPU version as shown above"
                ])
        
        # Check environment variables
        if not results["environment_variables"]["cuda_path"] and results["cuda_installation"]["installed"]:
            self.recommendations.append("Set CUDA_PATH environment variable to CUDA installation directory")
        
        if not results["path_check"]["cuda_found"] and results["cuda_installation"]["installed"]:
            self.recommendations.append("Add CUDA bin directory to system PATH")
    
    def _print_diagnostic_results(self, results: Dict[str, Any]):
        """Print comprehensive diagnostic results"""
        print("\n" + "=" * 70)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        # System Info
        print(f"\n📋 System Information:")
        print(f"   OS: {results['system_info']['platform']} {results['system_info']['platform_release']}")
        print(f"   Architecture: {results['system_info']['architecture']}")
        print(f"   Python: {results['system_info']['python_version']}")
        
        # Issues Found
        if self.issues:
            print(f"\n❌ Issues Found ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ No issues found!")
        
        # Recommendations
        if self.recommendations:
            print(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Final Status
        print(f"\n🎯 CUDA Status: {'✅ READY' if not self.issues else '❌ NEEDS ATTENTION'}")
        
        if not self.issues:
            print(f"\n🎉 Everything looks good! CUDA should be working properly.")
        else:
            print(f"\n🔧 Follow the recommendations above to fix CUDA issues.")
            print(f"   After fixing issues, restart VisionCraft Pro to use GPU acceleration.")

def run_diagnostic():
    """Run the complete CUDA diagnostic"""
    diagnostic = CudaDiagnostic()
    return diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    run_diagnostic()
