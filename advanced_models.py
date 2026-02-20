"""
Advanced Image Generation Models for GTX 1070
Experimental models with memory optimizations
"""

import torch
import gc
from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import warnings
from typing import Dict, Any, Optional
from gtx1070_optimizations import GTX1070Optimizer
from sdxl_models import SDXLOptimizedPipeline, SDXLTurboPipeline, SDXLModelManager, SDXLPromptPresets

class AdvancedModelManager:
    """Manages multiple AI models with GTX 1070 optimizations"""
    
    def __init__(self):
        self.models = {}
        self.current_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Define available models with GTX 1070 compatibility info
        self.available_models = {
            "stable-diffusion-1.5": {
                "name": "Stable Diffusion 1.5",
                "model_id": "runwayml/stable-diffusion-v1-5",
                "description": "Most stable, fastest, lowest VRAM usage",
                "vram_required": "4-6GB",
                "resolution": "512x512",
                "quality": "Good",
                "speed": "Fastest",
                "compatible": True,
                "experimental": False
            },
            "sdxl-base": {
                "name": "Stable Diffusion XL 1.0",
                "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "description": "High-quality 1024x1024 generation with advanced composition",
                "vram_required": "6-8GB",
                "resolution": "1024x1024",
                "quality": "Excellent",
                "speed": "Medium",
                "compatible": True,
                "experimental": False,
                "sdxl_optimized": True
            },
            "sdxl-turbo": {
                "name": "SDXL Turbo",
                "model_id": "stabilityai/sdxl-turbo",
                "description": "Ultra-fast generation (1-4 steps) with XL quality",
                "vram_required": "6-8GB",
                "resolution": "512x512 (fast) / 1024x1024 (quality)",
                "quality": "Good",
                "speed": "Fastest (1-4 steps)",
                "compatible": True,
                "experimental": False,
                "sdxl_optimized": True
            },
            "dreamshaper": {
                "name": "DreamShaper",
                "model_id": "Lykon/DreamShaper",
                "description": "Artistic and creative style, good for fantasy",
                "vram_required": "4-6GB", 
                "resolution": "512x512",
                "quality": "Very Good",
                "speed": "Fast",
                "compatible": True,
                "experimental": False
            },
            "realistic-vision": {
                "name": "Realistic Vision",
                "model_id": "runwayml/stable-diffusion-v1-5",
                "description": "Photorealistic images, portraits and scenes (using SD 1.5 base)",
                "vram_required": "4-6GB",
                "resolution": "512x512", 
                "quality": "Excellent",
                "speed": "Fast",
                "compatible": True,
                "experimental": False
            },
            "cyberpunk-anime": {
                "name": "Cyberpunk Anime",
                "model_id": "hakurei/waifu-diffusion",
                "description": "Anime and cyberpunk style, high quality",
                "vram_required": "4-6GB",
                "resolution": "512x512", 
                "quality": "Very Good",
                "speed": "Fast",
                "compatible": True,
                "experimental": False
            },
            "deliberate": {
                "name": "Deliberate",
                "model_id": "cagliostrolab/animagine-xl-3.0",
                "description": "High-quality anime and artistic style",
                "vram_required": "6-8GB",
                "resolution": "512x512",
                "quality": "Excellent",
                "speed": "Medium",
                "compatible": True,
                "experimental": True
            },
            "lcsd": {
                "name": "LCM SD",
                "model_id": "SimianLuo/LCM_Dreamshaper_v7",
                "description": "Latent Consistency Models, 2-8 step generation",
                "vram_required": "4-6GB",
                "resolution": "512x512",
                "quality": "Good",
                "speed": "Very Fast (2-8 steps)",
                "compatible": True,
                "experimental": True
            }
        }
    
    def get_model_info(self, model_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        return self.available_models.get(model_key)
    
    def get_compatible_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all models compatible with GTX 1070"""
        return {k: v for k, v in self.available_models.items() if v["compatible"]}
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all available models"""
        return self.available_models
    
    def load_model(self, model_key: str) -> bool:
        """Load a specific model with GTX 1070 optimizations"""
        if model_key not in self.available_models:
            print(f"❌ Model {model_key} not available")
            return False
        
        model_info = self.available_models[model_key]
        
        # Check VRAM requirements
        if not model_info["compatible"]:
            print(f"⚠️  Model {model_info['name']} may not be compatible with 8GB VRAM")
        
        print(f"🔄 Loading {model_info['name']}...")
        print(f"📝 {model_info['description']}")
        print(f"💾 VRAM required: {model_info['vram_required']}")
        
        try:
            # Clear existing model
            if self.current_model:
                self.unload_current_model()
            
            # Load new model
            if model_info.get("sdxl_optimized"):
                # Use the new SDXL optimized pipelines
                if "turbo" in model_key.lower():
                    pipe = SDXLTurboPipeline()
                else:
                    pipe = SDXLOptimizedPipeline(model_info["model_id"])
                
                # Load the model with optimizations
                success = pipe.load_model()
                if not success:
                    raise Exception("Failed to load SDXL model")
                
                # Store the pipeline directly (already optimized)
                self.models[model_key] = pipe
                self.current_model = model_key
                
                print(f"✅ {model_info['name']} loaded successfully!")
                return True
            elif "xl" in model_key.lower() or "sdxl" in model_key.lower():
                # Handle other SDXL models with legacy method
                pipe = self._load_sdxl_model(model_info["model_id"])
            else:
                # Handle SD 1.5 models
                pipe = self._load_sd15_model(model_info["model_id"])
            
            # Apply GTX 1070 optimizations
            pipe = GTX1070Optimizer.optimize_for_gtx1070(pipe)
            
            # Store the model
            self.models[model_key] = pipe
            self.current_model = model_key
            
            print(f"✅ {model_info['name']} loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load {model_info['name']}: {str(e)}")
            return False
    
    def _load_sd15_model(self, model_id: str) -> StableDiffusionPipeline:
        """Load Stable Diffusion 1.5 based model"""
        try:
            # Special handling for DreamShaper due to loading issues
            if "dreamshaper" in model_id.lower():
                print("🎨 Loading DreamShaper with special configuration...")
                try:
                    # Try loading the main DreamShaper variant that works
                    pipe = StableDiffusionPipeline.from_pretrained(
                        "Lykon/DreamShaper",
                        torch_dtype=torch.float16,
                        use_safetensors=True
                    )
                except Exception as e:
                    print(f"DreamShaper loading failed, trying fallback: {e}")
                    # Fallback to a working variant or alternative
                    try:
                        pipe = StableDiffusionPipeline.from_pretrained(
                            "runwayml/stable-diffusion-v1-5",  # Fallback to SD 1.5
                            torch_dtype=torch.float16,
                            variant="fp16",
                            use_safetensors=True
                        )
                        print("✅ Using Stable Diffusion 1.5 as fallback for DreamShaper")
                    except Exception as e2:
                        print(f"SD 1.5 fallback also failed: {e2}")
                        raise e2
            else:
                # Try loading with fp16 variant first
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    variant="fp16",
                    use_safetensors=True
                )
        except Exception as e:
            print(f"FP16 variant not available, trying standard loading: {e}")
            try:
                # Fallback to standard loading without variant
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True
                )
            except Exception as e2:
                print(f"Standard loading failed, trying without safetensors: {e2}")
                # Final fallback without safetensors (with security warning)
                try:
                    pipe = StableDiffusionPipeline.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16
                    )
                    print("⚠️  Loaded without safetensors - security warning acknowledged")
                except Exception as e3:
                    print(f"All loading methods failed: {e3}")
                    # Final fallback to SD 1.5
                    print("🔄 Falling back to Stable Diffusion 1.5...")
                    pipe = StableDiffusionPipeline.from_pretrained(
                        "runwayml/stable-diffusion-v1-5",
                        torch_dtype=torch.float16,
                        variant="fp16",
                        use_safetensors=True
                    )
        
        # Use DPM solver for better quality with fewer steps
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        
        return pipe
    
    def _load_sdxl_model(self, model_id: str) -> StableDiffusionXLPipeline:
        """Load Stable Diffusion XL based model"""
        try:
            # Special handling for SDXL Turbo
            if "turbo" in model_id.lower():
                print("🚀 Loading SDXL Turbo with special configuration...")
                pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    variant="fp16",
                    use_safetensors=True
                )
                # SDXL Turbo requires specific guidance scale and steps
                # It's designed for 1-step generation with guidance_scale=0.0
                pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
                print("✅ SDXL Turbo configured for 1-step generation")
            else:
                # Regular SDXL models
                pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    variant="fp16",
                    use_safetensors=True
                )
                # Use DPM solver for XL
                pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
                
        except Exception as e:
            print(f"FP16 variant not available, trying standard loading: {e}")
            try:
                # Fallback to standard loading without variant
                pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True
                )
                if "turbo" in model_id.lower():
                    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
                else:
                    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
            except Exception as e2:
                print(f"Standard loading failed, trying without safetensors: {e2}")
                # Final fallback without safetensors
                pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16
                )
                if "turbo" in model_id.lower():
                    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
                else:
                    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        
        return pipe
    
    def unload_current_model(self):
        """Unload the current model to free VRAM"""
        if self.current_model and self.current_model in self.models:
            print(f"🗑️  Unloading {self.available_models[self.current_model]['name']}...")
            del self.models[self.current_model]
            self.current_model = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("✅ Model unloaded, VRAM freed")
    
    def generate_image(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using current model"""
        if not self.current_model:
            raise ValueError("No model loaded. Please load a model first.")
        
        model = self.models[self.current_model]
        model_info = self.available_models[self.current_model]
        
        # Handle new SDXL optimized pipelines
        if model_info.get("sdxl_optimized"):
            print(f"🎨 Generating with {model_info['name']} (optimized)...")
            
            # Apply SDXL presets if requested
            preset_name = kwargs.get("sdxl_preset")
            if preset_name:
                preset_result = SDXLPromptPresets.apply_preset(prompt, preset_name)
                prompt = preset_result["prompt"]
                kwargs["negative_prompt"] = preset_result.get("negative_prompt", "")
                print(f"🎭 Applied SDXL preset: {preset_name}")
            
            # Generate with optimized pipeline
            result = model.generate(prompt, **kwargs)
            if result:
                return result
            else:
                raise Exception("SDXL generation failed")
        
        # Legacy model handling
        # Adjust parameters based on model type
        if "turbo" in self.current_model.lower():
            # SDXL Turbo uses 1-4 steps and 0.0 guidance for best results
            user_steps = kwargs.get("num_inference_steps", 1)
            # Use more steps for better quality (still very fast)
            optimal_steps = min(max(user_steps, 2), 4)  # Force 2-4 steps for better quality
            kwargs["num_inference_steps"] = optimal_steps
            kwargs["guidance_scale"] = 0.0  # Critical: SDXL Turbo requires 0.0 guidance
            print(f"🚀 Using SDXL Turbo settings: {optimal_steps} steps, 0.0 guidance")
            print("💡 Tip: SDXL Turbo works best with 2-4 steps for quality vs speed")
        elif "lcm" in self.current_model.lower():
            # LCM models use 2-8 steps
            kwargs["num_inference_steps"] = min(kwargs.get("num_inference_steps", 4), 8)
            kwargs["guidance_scale"] = min(kwargs.get("guidance_scale", 1.0), 2.0)  # Keep guidance low for LCM
        
        print(f"🎨 Generating with {model_info['name']}...")
        print(f"⚡ Steps: {kwargs.get('num_inference_steps', 25)}")
        print(f"🎯 Guidance: {kwargs.get('guidance_scale', 7.5)}")
        
        try:
            # Enhance prompt for better quality
            enhanced_prompt = self._enhance_prompt(prompt)
            print(f"📝 Enhanced prompt: {enhanced_prompt}")
            
            # Special debugging for SDXL models
            if "xl" in self.current_model.lower():
                print("🔍 SDXL Debug Info:")
                print(f"   Model type: {type(model)}")
                print(f"   Device: {model.device}")
                print(f"   Scheduler: {type(model.scheduler)}")
                print(f"   Prompt: {enhanced_prompt[:100]}...")
                print(f"   Steps: {kwargs.get('num_inference_steps', 25)}")
                print(f"   Guidance: {kwargs.get('guidance_scale', 7.5)}")
                print(f"   Width: {kwargs.get('width', 512)}")
                print(f"   Height: {kwargs.get('height', 512)}")
            
            # Generate image with enhanced prompt (don't pass prompt twice)
            if "xl" in self.current_model.lower():
                # Special handling for SDXL models - try without autocast first
                print("🔧 Using SDXL-specific generation...")
                try:
                    result = model(
                        prompt=enhanced_prompt,
                        negative_prompt=kwargs.get("negative_prompt", ""),
                        num_inference_steps=kwargs.get("num_inference_steps", 25),
                        guidance_scale=kwargs.get("guidance_scale", 7.5),
                        width=kwargs.get("width", 512),
                        height=kwargs.get("height", 512),
                        generator=kwargs.get("generator")
                    )
                except Exception as e:
                    print(f"⚠️  SDXL generation failed, trying with autocast: {e}")
                    # Fallback to autocast
                    with torch.autocast(self.device):
                        result = model(
                            prompt=enhanced_prompt,
                            negative_prompt=kwargs.get("negative_prompt", ""),
                            num_inference_steps=kwargs.get("num_inference_steps", 25),
                            guidance_scale=kwargs.get("guidance_scale", 7.5),
                            width=kwargs.get("width", 512),
                            height=kwargs.get("height", 512),
                            generator=kwargs.get("generator")
                        )
            else:
                # Standard generation for non-XL models
                with torch.autocast(self.device):
                    result = model(
                        prompt=enhanced_prompt,
                        negative_prompt=kwargs.get("negative_prompt", ""),
                        num_inference_steps=kwargs.get("num_inference_steps", 25),
                        guidance_scale=kwargs.get("guidance_scale", 7.5),
                        width=kwargs.get("width", 512),
                        height=kwargs.get("height", 512),
                        generator=kwargs.get("generator")
                    )
            
            # Debug the result
            print(f"🔍 Result Debug Info:")
            print(f"   Result type: {type(result)}")
            print(f"   Has images: {hasattr(result, 'images')}")
            if hasattr(result, 'images'):
                print(f"   Number of images: {len(result.images)}")
                if result.images:
                    img = result.images[0]
                    print(f"   Image type: {type(img)}")
                    print(f"   Image size: {img.size}")
                    print(f"   Image mode: {img.mode}")
                    
                    # Check if image is completely black
                    import numpy as np
                    img_array = np.array(img)
                    print(f"   Image array shape: {img_array.shape}")
                    print(f"   Min pixel value: {img_array.min()}")
                    print(f"   Max pixel value: {img_array.max()}")
                    print(f"   Mean pixel value: {img_array.mean()}")
                    
                    if img_array.mean() < 5:  # Very dark image
                        print("⚠️  WARNING: Image appears to be mostly black!")
            
            image = result.images[0]
            
            # Cleanup
            del result
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            return image
            
        except Exception as e:
            print(f"❌ Generation error: {str(e)}")
            # Cleanup on error
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            raise e
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt for better quality results"""
        # Check if current model is SDXL Turbo
        is_turbo = self.current_model and "turbo" in self.current_model.lower()
        
        if is_turbo:
            # SDXL Turbo works best with simpler, more direct prompts
            # Too many quality terms can actually make it blurrier
            quality_terms = ["high quality", "detailed", "sharp focus"]
            
            # Remove existing quality terms to avoid duplication
            cleaned = prompt.lower()
            for term in ["high quality", "detailed", "realistic", "photorealistic", "8k", "4k", "masterpiece"]:
                cleaned = cleaned.replace(term, "")
            
            # Add just a few key quality terms
            enhanced = f"{cleaned.strip()}, {', '.join(quality_terms)}"
            return enhanced
        else:
            # Standard enhancement for other models
            quality_terms = ["highly detailed", "sharp focus", "best quality", "photorealistic", "8k"]
            
            # Remove existing quality terms to avoid duplication
            cleaned = prompt.lower()
            for term in ["high quality", "detailed", "realistic", "photorealistic", "8k", "4k"]:
                cleaned = cleaned.replace(term, "")
            
            # Add quality terms
            enhanced = f"{cleaned.strip()}, {', '.join(quality_terms)}"
            return enhanced
    
    def get_optimal_settings(self, model_key: str = None) -> Dict[str, Any]:
        """Get optimal settings for a specific model or current model"""
        if model_key is None:
            model_key = self.current_model
        
        base_settings = {
            "default_steps": 25,  # Increased from 20 for better quality
            "max_steps": 50,      # Increased from 30
            "default_guidance": 7.5,
            "default_resolution": (512, 512)
        }
        
        if "turbo" in model_key.lower():
            return {
                **base_settings,
                "default_steps": 2,  # Changed from 1 to 2 for better quality
                "max_steps": 4,
                "default_guidance": 0.0  # No guidance for turbo
            }
        elif "lcm" in model_key.lower():
            return {
                **base_settings,
                "default_steps": 4,
                "max_steps": 8,
                "default_guidance": 1.0  # Lower guidance for LCM
            }
        elif "xl" in model_key.lower():
            return {
                **base_settings,
                "default_steps": 20,
                "max_steps": 40,
                "default_resolution": (1024, 1024)  # XL supports higher resolution
            }
        elif "realistic" in model_key.lower():
            return {
                **base_settings,
                "default_steps": 30,  # More steps for realism
                "max_steps": 50,
                "default_guidance": 8.0,  # Higher guidance for detail
                "default_resolution": (512, 512)
            }
        
        return base_settings
    
    def get_model_recommendations(self) -> Dict[str, str]:
        """Get recommendations for different use cases"""
        return {
            "beginners": "stable-diffusion-1.5 - Most stable and reliable",
            "speed": "sdxl-turbo - Fastest generation (1-4 steps with XL quality)",
            "quality": "sdxl-base - Best 1024x1024 high-quality generation",
            "photorealistic": "sdxl-base with photorealistic preset - Professional photography quality",
            "artistic": "dreamshaper - Great for creative and fantasy images",
            "anime": "deliberate - High-quality anime and artistic style",
            "balanced": "lcsd - Good quality with very fast generation"
        }
    
    def get_sdxl_presets(self) -> Dict[str, Dict[str, str]]:
        """Get available SDXL presets"""
        return SDXLPromptPresets.get_presets()
    
    def apply_sdxl_preset(self, prompt: str, preset_name: str) -> Dict[str, str]:
        """Apply SDXL preset to prompt"""
        return SDXLPromptPresets.apply_preset(prompt, preset_name)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information for current model"""
        if not self.current_model:
            return {"error": "No model loaded"}
        
        model = self.models[self.current_model]
        model_info = self.available_models[self.current_model]
        
        if model_info.get("sdxl_optimized"):
            return model.get_memory_info()
        else:
            # Legacy model memory info
            info = {
                "current_model": self.current_model,
                "device": self.device,
                "model_loaded": self.current_model in self.models
            }
            
            if torch.cuda.is_available():
                info.update({
                    "cuda_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
                    "cuda_reserved": f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB",
                    "cuda_max_allocated": f"{torch.cuda.max_memory_allocated() / 1024**3:.2f} GB"
                })
            
            return info
