import torch
import sys

def check_system():
    print("=== System Check ===")
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"VRAM total: {vram_total:.2f} GB")
        
        # Check if 8GB VRAM is available
        if vram_total >= 7.5:
            print("✅ VRAM is sufficient for 8GB optimization")
        else:
            print("⚠️  VRAM may be limited, consider using smaller resolutions")
    else:
        print("❌ CUDA not available - will use CPU (much slower)")
    
    print("\n=== Dependencies Check ===")
    try:
        import diffusers
        print(f"✅ Diffusers: {diffusers.__version__}")
    except ImportError:
        print("❌ Diffusers not installed")
    
    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError:
        print("❌ Transformers not installed")
    
    try:
        import accelerate
        print(f"✅ Accelerate: {accelerate.__version__}")
    except ImportError:
        print("❌ Accelerate not installed")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed")
    
    try:
        import gradio
        print(f"✅ Gradio: {gradio.__version__}")
    except ImportError:
        print("❌ Gradio not installed")

if __name__ == "__main__":
    check_system()
