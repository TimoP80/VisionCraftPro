"""
Stable Diffusion XL (SDXL) Integration for VisionCraft Pro
Optimized for 8GB VRAM cards with memory-efficient loading

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
from diffusers.utils import logging
import gc
import os
from typing import Optional, Dict, Any
import json

# Suppress excessive logging
logging.set_verbosity_error()

class SDXLOptimizedPipeline:
    """Memory-optimized SDXL pipeline for 8GB VRAM"""
    
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.is_loaded = False
        
    def load_model(self, force_cpu: bool = False) -> bool:
        """Load SDXL model with memory optimizations"""
        try:
            print(f"[SDXL] Loading model: {self.model_id}")
            print(f"[SDXL] Device: {self.device}")
            print(f"[SDXL] Memory optimization enabled")
            
            device = "cpu" if force_cpu else self.device
            
            # Load with memory optimizations
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self.torch_dtype if device == "cuda" else torch.float32,
                variant="fp16" if device == "cuda" else "default",
                use_safetensors=True,
                add_watermarker=False,
                # Memory optimizations
                low_cpu_mem_usage=True,
                device_map="auto" if device == "cuda" else None
            )
            
            if device == "cuda":
                # Enable memory efficient attention
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_xformers_memory_efficient_attention()
                
                # Enable VAE slicing to reduce memory usage
                self.pipeline.enable_vae_slicing()
                self.pipeline.enable_vae_tiling()
            
            self.pipeline = self.pipeline.to(device)
            self.is_loaded = True
            
            # Clear cache
            if device == "cuda":
                torch.cuda.empty_cache()
            
            print(f"[SDXL] Model loaded successfully on {device}")
            return True
            
        except Exception as e:
            print(f"[SDXL] Error loading model: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> Optional[torch.Tensor]:
        """Generate image with SDXL"""
        if not self.is_loaded:
            print("[SDXL] Model not loaded")
            return None
            
        try:
            # Default SDXL parameters optimized for 8GB VRAM
            default_params = {
                "num_inference_steps": kwargs.get("num_inference_steps", 20),  # Reduced for speed
                "height": kwargs.get("height", 1024),
                "width": kwargs.get("width", 1024),
                "guidance_scale": kwargs.get("guidance_scale", 7.5),
                "negative_prompt": kwargs.get("negative_prompt", ""),
                "num_images_per_prompt": kwargs.get("num_images_per_prompt", 1),
                "generator": kwargs.get("generator", None),
                "latents": kwargs.get("latents", None),
                "prompt_embeds": kwargs.get("prompt_embeds", None),
                "negative_prompt_embeds": kwargs.get("negative_prompt_embeds", None),
                "pooled_prompt_embeds": kwargs.get("pooled_prompt_embeds", None),
                "negative_pooled_prompt_embeds": kwargs.get("negative_pooled_prompt_embeds", None),
            }
            
            print(f"[SDXL] Generating with {default_params['num_inference_steps']} steps")
            print(f"[SDXL] Size: {default_params['width']}x{default_params['height']}")
            
            with torch.inference_mode():
                result = self.pipeline(prompt, **default_params)
                
            # Clear cache after generation
            if self.device == "cuda":
                torch.cuda.empty_cache()
                
            return result.images[0]
            
        except Exception as e:
            print(f"[SDXL] Generation error: {e}")
            return None
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
            self.is_loaded = False
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            gc.collect()
            print("[SDXL] Model unloaded")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        info = {
            "device": self.device,
            "model_loaded": self.is_loaded,
            "torch_dtype": str(self.torch_dtype)
        }
        
        if self.device == "cuda":
            info.update({
                "cuda_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
                "cuda_reserved": f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB",
                "cuda_max_allocated": f"{torch.cuda.max_memory_allocated() / 1024**3:.2f} GB"
            })
        
        return info

class SDXLTurboPipeline:
    """SDXL Turbo pipeline for fast generation"""
    
    def __init__(self):
        self.model_id = "stabilityai/sdxl-turbo"
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.is_loaded = False
    
    def load_model(self) -> bool:
        """Load SDXL Turbo model"""
        try:
            print(f"[SDXL-Turbo] Loading model: {self.model_id}")
            
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self.torch_dtype,
                variant="fp16" if self.device == "cuda" else "default",
                use_safetensors=True,
                add_watermarker=False,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_xformers_memory_efficient_attention()
            
            self.pipeline = self.pipeline.to(self.device)
            self.is_loaded = True
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            print(f"[SDXL-Turbo] Model loaded successfully")
            return True
            
        except Exception as e:
            print(f"[SDXL-Turbo] Error loading model: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> Optional[torch.Tensor]:
        """Generate image with SDXL Turbo (1-4 steps)"""
        if not self.is_loaded:
            print("[SDXL-Turbo] Model not loaded")
            return None
            
        try:
            # Turbo uses very few steps
            params = {
                "num_inference_steps": kwargs.get("num_inference_steps", 1),  # Turbo default
                "guidance_scale": kwargs.get("guidance_scale", 0.0),  # Turbo default
                "height": kwargs.get("height", 512),  # Smaller for speed
                "width": kwargs.get("width", 512),
                "negative_prompt": kwargs.get("negative_prompt", ""),
            }
            
            print(f"[SDXL-Turbo] Generating with {params['num_inference_steps']} steps")
            
            with torch.inference_mode():
                result = self.pipeline(prompt, **params)
                
            if self.device == "cuda":
                torch.cuda.empty_cache()
                
            return result.images[0]
            
        except Exception as e:
            print(f"[SDXL-Turbo] Generation error: {e}")
            return None
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
            self.is_loaded = False
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            gc.collect()
            print("[SDXL-Turbo] Model unloaded")

class SDXLPromptPresets:
    """SDXL-specific prompt engineering presets"""
    
    PRESETS = {
        "photorealistic": {
            "prefix": "photorealistic, professional photography, 8k, ultra detailed, sharp focus",
            "suffix": "cinematic lighting, high resolution, award-winning photography",
            "negative": "cartoon, anime, painting, illustration, 3d render, blurry, low quality"
        },
        "artistic": {
            "prefix": "digital art, masterpiece, intricate details, artistic composition",
            "suffix": "vibrant colors, creative, expressive, fine art",
            "negative": "photorealistic, realistic, photo, blurry, low quality"
        },
        "cinematic": {
            "prefix": "cinematic shot, film still, dramatic lighting, movie scene",
            "suffix": "epic, atmospheric, professional cinematography, high budget",
            "negative": "cartoon, anime, amateur, snapshot, phone camera"
        },
        "fantasy": {
            "prefix": "fantasy art, magical, ethereal, dreamlike, otherworldly",
            "suffix": "enchanted, mystical, divine, celestial, magical atmosphere",
            "negative": "modern, realistic, contemporary, mundane, ordinary"
        },
        "sci_fi": {
            "prefix": "sci-fi, futuristic, cyberpunk, high-tech, advanced technology",
            "suffix": "neon lights, holographic, digital art, concept art",
            "negative": "historical, vintage, retro, low-tech, primitive"
        },
        "portrait": {
            "prefix": "portrait photography, professional headshot, detailed face",
            "suffix": "natural lighting, sharp focus, eyes in focus, high resolution",
            "negative": "cartoon, anime, distorted face, blurry eyes, low quality"
        }
    }
    
    @classmethod
    def apply_preset(cls, prompt: str, preset_name: str) -> Dict[str, str]:
        """Apply a preset to a prompt"""
        if preset_name not in cls.PRESETS:
            return {"prompt": prompt, "negative_prompt": ""}
        
        preset = cls.PRESETS[preset_name]
        enhanced_prompt = f"{preset['prefix']}, {prompt}, {preset['suffix']}"
        
        return {
            "prompt": enhanced_prompt,
            "negative_prompt": preset["negative"]
        }
    
    @classmethod
    def get_presets(cls) -> Dict[str, Dict[str, str]]:
        """Get all available presets"""
        return cls.PRESETS.copy()

# Model management
class SDXLModelManager:
    """Manage SDXL model downloads and caching"""
    
    def __init__(self, cache_dir: str = "models/sdxl"):
        self.cache_dir = cache_dir
        self.models = {
            "sdxl_base": SDXLOptimizedPipeline("stabilityai/stable-diffusion-xl-base-1.0"),
            "sdxl_turbo": SDXLTurboPipeline(),
        }
        self.current_model = None
        
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def load_model(self, model_name: str) -> bool:
        """Load a specific model"""
        if model_name not in self.models:
            print(f"[Model Manager] Unknown model: {model_name}")
            return False
        
        # Unload current model if different
        if self.current_model and self.current_model != model_name:
            self.unload_current_model()
        
        self.ensure_cache_dir()
        
        success = self.models[model_name].load_model()
        if success:
            self.current_model = model_name
            print(f"[Model Manager] Loaded model: {model_name}")
        
        return success
    
    def unload_current_model(self):
        """Unload the currently loaded model"""
        if self.current_model:
            self.models[self.current_model].unload_model()
            self.current_model = None
    
    def generate(self, prompt: str, model_name: str = None, **kwargs):
        """Generate with specified model"""
        if model_name is None:
            model_name = self.current_model
        
        if not model_name or model_name not in self.models:
            print("[Model Manager] No model specified or loaded")
            return None
        
        return self.models[model_name].generate(prompt, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        info = {
            "current_model": self.current_model,
            "available_models": list(self.models.keys()),
            "model_status": {}
        }
        
        for name, model in self.models.items():
            info["model_status"][name] = {
                "loaded": model.is_loaded,
                "device": model.device,
                "memory_info": model.get_memory_info()
            }
        
        return info

# Convenience functions
def create_sdxl_pipeline(model_type: str = "base") -> SDXLOptimizedPipeline:
    """Create an SDXL pipeline"""
    if model_type == "turbo":
        return SDXLTurboPipeline()
    else:
        return SDXLOptimizedPipeline()

def get_sdxl_presets() -> Dict[str, Dict[str, str]]:
    """Get SDXL prompt presets"""
    return SDXLPromptPresets.get_presets()

def apply_sdxl_preset(prompt: str, preset_name: str) -> Dict[str, str]:
    """Apply SDXL preset to prompt"""
    return SDXLPromptPresets.apply_preset(prompt, preset_name)
