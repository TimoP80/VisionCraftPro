"""
GTX 1070 Specific Optimizations for 8GB VRAM
This module contains additional optimizations specifically tuned for GTX 1070 GPUs
"""

import torch
import gc
from diffusers import StableDiffusionPipeline
import warnings

class GTX1070Optimizer:
    """GTX 1070 specific optimizations for maximum VRAM efficiency"""
    
    @staticmethod
    def optimize_for_gtx1070(pipe) -> StableDiffusionPipeline:
        """
        Apply GTX 1070 specific optimizations to the pipeline
        """
        
        # Check if this is an SDXL pipeline
        is_sdxl = "StableDiffusionXLPipeline" in str(type(pipe))
        
        if is_sdxl:
            print("🔧 Applying SDXL-compatible optimizations...")
            # More conservative optimizations for SDXL
            try:
                pipe.enable_xformers_memory_efficient_attention()
                print("✅ XFormers enabled for SDXL")
            except Exception:
                print("⚠️  XFormers not available, using default attention")
            
            # SDXL VAE optimizations
            try:
                pipe.enable_vae_slicing()
                print("✅ VAE slicing enabled for SDXL")
            except Exception:
                print("⚠️  VAE slicing not available for SDXL")
            
            # SDXL CPU offloading (more conservative)
            try:
                pipe.enable_sequential_cpu_offload()
                print("✅ Sequential CPU offload enabled for SDXL")
            except Exception as e:
                print(f"⚠️  CPU offload failed for SDXL: {e}")
        else:
            print("🔧 Applying standard SD 1.5 optimizations...")
            # Full optimizations for SD 1.5
            # 1. Force FP16 precision for GTX 1070
            pipe = pipe.to(torch.float16)
            
            # 2. Enable all available memory optimizations
            try:
                pipe.enable_xformers_memory_efficient_attention()
                print("✅ XFormers enabled")
            except Exception:
                print("⚠️  XFormers not available, using default attention (still works fine)")
            
            # 3. Enable VAE slicing (critical for 8GB cards)
            pipe.enable_vae_slicing()
            print("✅ VAE slicing enabled")
            
            # 4. Enable VAE tiling for very large images
            pipe.enable_vae_tiling()
            print("✅ VAE tiling enabled")
            
            # 5. Use CPU offloading strategy optimized for GTX 1070
            pipe.enable_sequential_cpu_offload()
            print("✅ Sequential CPU offload enabled")
            
            # Note: Don't enable model_cpu_offload as it conflicts with sequential_cpu_offload
            
            # 6. Set memory efficient attention slice size
            if hasattr(pipe.unet, 'config'):
                pipe.unet.config.attention_slice_dim = 1
            
            # 7. Reduce UNet memory usage
            if hasattr(pipe.unet, 'set_attention_slice'):
                pipe.unet.set_attention_slice("auto")
        
        return pipe
    
    @staticmethod
    def get_optimal_settings_for_gtx1070():
        """
        Returns optimal generation settings for GTX 1070
        """
        return {
            "default_steps": 20,  # Balanced quality/speed
            "max_steps": 30,       # Don't exceed for VRAM safety
            "default_resolution": (512, 512),  # Most efficient
            "max_resolution": (768, 768),      # Use with caution
            "default_guidance": 7.5,
            "batch_size": 1,       # Never use batching on 8GB
            "recommended_scheduler": "DPMSolverMultistepScheduler"
        }
    
    @staticmethod
    def monitor_vram_usage():
        """
        Monitor VRAM usage and provide warnings
        """
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            # Show both allocated and reserved for better understanding
            print(f"VRAM Usage: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved, {total:.2f}GB total")
            
            # Use reserved memory for warnings (closer to Task Manager)
            if reserved > 7.0:
                warnings.warn("VRAM usage is very high! Consider reducing resolution or steps.")
            elif reserved > 6.0:
                print("⚠️  VRAM usage is moderate, monitor closely")
            else:
                print("✅ VRAM usage is within safe limits")
    
    @staticmethod
    def cleanup_memory():
        """
        Aggressive memory cleanup for GTX 1070
        """
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    
    @staticmethod
    def get_gtx1070_tips():
        """
        Return GTX 1070 specific usage tips
        """
        return """
🎮 GTX 1070 Optimization Tips:
        
✅ RECOMMENDED SETTINGS:
- Resolution: 512x512 (most efficient)
- Steps: 15-25 (balanced quality/speed)
- Guidance: 7.0-8.0 (good results)
- Batch Size: 1 (never increase)

⚠️  USE WITH CAUTION:
- 768x768 resolution (may hit VRAM limit)
- 30+ steps (diminishing returns, high VRAM)
- Multiple generations simultaneously

🚀 PERFORMANCE TIPS:
- Close other GPU applications
- Use 20 steps for most images
- Start with 512x512, upscale if needed
- Monitor VRAM usage in the web interface

💾 MEMORY MANAGEMENT:
- App automatically cleans memory after each generation
- VRAM usage displayed in real-time
- Model loads on first generation (slower, then fast)
"""
    
    @staticmethod
    def validate_gtx1070_compatibility():
        """
        Check if the system is GTX 1070 compatible
        """
        if not torch.cuda.is_available():
            return False, "CUDA not available"
        
        gpu_name = torch.cuda.get_device_name(0).lower()
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        is_gtx1070 = "gtx 1070" in gpu_name
        has_8gb = vram_gb >= 7.5
        
        if is_gtx1070 and has_8gb:
            return True, "GTX 1070 with 8GB VRAM detected - Perfect!"
        elif has_8gb:
            return True, f"8GB+ GPU detected ({torch.cuda.get_device_name(0)}) - Should work well"
        else:
            return False, f"GPU has only {vram_gb:.1f}GB VRAM - May be insufficient"
