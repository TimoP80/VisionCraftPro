import torch
import gc
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from transformers import CLIPTextModel, CLIPTokenizer
from PIL import Image
import numpy as np
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import psutil
import threading
import time
import asyncio
import io
import base64
from gtx1070_optimizations import GTX1070Optimizer
from advanced_models import AdvancedModelManager
from image_gallery import ImageGallery
from prompt_enhancer import PromptEnhancer
from modern_generators import ModernGeneratorManager
from cuda_checker import CudaChecker

class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    num_inference_steps: Optional[int] = 20
    guidance_scale: Optional[float] = 7.5
    width: Optional[int] = 512
    height: Optional[int] = 512
    seed: Optional[int] = -1
    model: Optional[str] = "stable-diffusion-1.5"  # New field for model selection
    
    # Leonardo.ai specific parameters
    leonardo_model: Optional[str] = None  # Specific model within Leonardo.ai
    aspect_ratio: Optional[str] = None
    preset_style: Optional[str] = None
    quality: Optional[str] = None

class GenerationResponse(BaseModel):
    image: str
    generation_time: float
    vram_used: float

class ImageGenerator:
    """Main image generation class with both local and modern generators"""
    
    def __init__(self):
        # Check CUDA and GPU PyTorch availability first
        print("[CUDA] Checking CUDA and GPU PyTorch availability...")
        self.cuda_checker = CudaChecker()
        cuda_results = self.cuda_checker.check_cuda_availability()
        
        if cuda_results['cuda_available'] and not cuda_results['gpu_torch_available']:
            print("[CUDA] CUDA detected but GPU PyTorch not available")
            print("[CUDA] Attempting to install GPU PyTorch...")
            self.cuda_checker.install_gpu_pytorch()
            print("[CUDA] Please restart the application after GPU PyTorch installation")
        
        self.model_manager = AdvancedModelManager()
        self.modern_manager = ModernGeneratorManager()
        self.gallery = ImageGallery()
        self.model_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.current_generator_type = "local"  # "local" or "modern"
        self.current_model = None
        
        # Print CUDA status
        if torch.cuda.is_available():
            print(f"[CUDA] Using GPU: {torch.cuda.get_device_name(0)}")
            print(f"[CUDA] CUDA Version: {torch.version.cuda}")
        else:
            print("[CUDA] Using CPU (CUDA not available or GPU PyTorch not installed)")
        
    def load_model(self, model_key: str = "stable-diffusion-1.5"):
        """Load a specific model or modern generator"""
        print(f"[RELOAD] Loading model: {model_key}")
        print(f"[SEARCH] Available modern generators: {list(self.modern_manager.available_generators.keys())}")
        
        # Check if this is a modern generator
        if model_key in self.modern_manager.available_generators:
            self.current_generator_type = "modern"
            self.current_model = model_key
            self.model_loaded = True
            print(f"[OK] Modern generator selected: {self.modern_manager.available_generators[model_key]['name']}")
            print(f"[SEARCH] Generator type set to: {self.current_generator_type}")
            return True
        else:
            # Load local model
            print(f"[RELOAD] Attempting to load local model: {model_key}")
            self.current_generator_type = "local"
            if self.model_manager.load_model(model_key):
                self.model_loaded = True
                self.current_model = model_key
                print(f"[OK] Local model selected: {model_key}")
                print(f"[SEARCH] Generator type set to: {self.current_generator_type}")
                return True
            else:
                print(f"[ERROR] Failed to load local model: {model_key}")
        return False
        
    def get_vram_usage(self):
        """Get current VRAM usage in GB"""
        if torch.cuda.is_available():
            # Get comprehensive VRAM usage that matches Task Manager
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            
            # Use reserved memory as it's closer to what Task Manager shows
            # Task Manager shows total VRAM usage including reserved memory
            return reserved
        return 0.0
    
    def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image using local or modern generator"""
        start_time = time.time()
        
        print(f"[ART] Starting generation with {self.current_model}")
        print(f"[SEARCH] Current generator type: {self.current_generator_type}")
        print(f"[SEARCH] Request model: {request.model}")
        
        if self.current_generator_type == "modern":
            print(f"[RELOAD] Using modern generator...")
            # Use modern generator
            return self._generate_with_modern(request, start_time)
        else:
            print(f"[RELOAD] Using local generator...")
            # Use local model
            return self._generate_with_local(request, start_time)
    
    async def _generate_with_modern_async(self, request: GenerationRequest, start_time: float) -> GenerationResponse:
        """Generate image using modern API generator (async version)"""
        try:
            print(f"[ART] Starting modern generation with {self.current_model}")
            print(f"[NOTE] Prompt: {request.prompt[:100]}...")
            print(f"[SEARCH] Request model: {request.model}")
            print(f"[SEARCH] Request leonardo_model: {getattr(request, 'leonardo_model', 'None')}")
            
            # Prepare kwargs for modern generator
            kwargs = {
                'negative_prompt': request.negative_prompt,
                'width': request.width,
                'height': request.height,
                'num_inference_steps': request.num_inference_steps,
                'guidance_scale': request.guidance_scale
            }
            
            # Add Leonardo.ai specific parameters if available
            if hasattr(request, 'aspect_ratio'):
                kwargs['aspect_ratio'] = request.aspect_ratio
            if hasattr(request, 'preset_style'):
                kwargs['preset_style'] = request.preset_style
            if hasattr(request, 'quality'):
                kwargs['quality'] = request.quality
            if hasattr(request, 'leonardo_model') and request.leonardo_model:
                kwargs['model'] = request.leonardo_model  # Pass specific Leonardo model
            
            print(f"[SEARCH] Modern generator kwargs: {kwargs}")
            
            # Generate with modern API
            image = await self.modern_manager.generate_image(
                self.current_model,
                request.prompt,
                **kwargs
            )
            
            generation_time = time.time() - start_time
            vram_used = 0.0  # API generators don't use local VRAM
            
            # Convert to base64 first
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            print(f"[OK] Modern generation completed in {generation_time:.2f}s")
            
            # Save to gallery
            image_id = self.gallery.add_image(
                image_data=img_str,
                prompt=request.prompt,
                model=self.current_model,
                generation_time=generation_time,
                vram_used=vram_used,
                steps=request.num_inference_steps,
                guidance=request.guidance_scale,
                resolution=(request.width, request.height)
            )
            
            return GenerationResponse(
                image=img_str,
                generation_time=generation_time,
                vram_used=vram_used
            )
            
        except Exception as e:
            print(f"[ERROR] Modern generation failed: {str(e)}")
            print(f"[SEARCH] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Modern generation failed: {str(e)}")
    
    def _generate_with_modern(self, request: GenerationRequest, start_time: float) -> GenerationResponse:
        """Generate image using modern API generator"""
        try:
            # Generate with modern API
            image = asyncio.run(self.modern_manager.generate_image(
                self.current_model,
                request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale
            ))
            
            generation_time = time.time() - start_time
            vram_used = 0.0  # API generators don't use local VRAM
            
            # Save to gallery
            image_id = self.gallery.add_image(
                image=image,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                model=self.current_model,
                steps=request.num_inference_steps,
                guidance=request.guidance_scale,
                width=request.width,
                height=request.height,
                generation_time=generation_time,
                vram_used=vram_used
            )
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return GenerationResponse(
                image=img_str,
                generation_time=generation_time,
                vram_used=vram_used
            )
            
        except Exception as e:
            print(f" Modern generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Modern generation failed: {str(e)}")
    
    def _generate_with_local(self, request: GenerationRequest, start_time: float) -> GenerationResponse:
        """Generate image using local model"""
        # Load model if needed or switch model
        if not self.model_loaded or self.model_manager.current_model != request.model:
            if not self.load_model(request.model):
                raise HTTPException(status_code=400, detail=f"Failed to load model: {request.model}")
        
        try:
            # Generate image
            image = self.model_manager.generate_image(
                request.prompt,
                negative_prompt=request.negative_prompt,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                width=request.width,
                height=request.height,
                seed=request.seed if request.seed != -1 else None
            )
            
            generation_time = time.time() - start_time
            vram_used = self.get_vram_usage()
            
            # Convert to base64 first
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Save to gallery
            image_id = self.gallery.add_image(
                image_data=img_str,
                prompt=request.prompt,
                model=self.model_manager.current_model,
                generation_time=generation_time,
                vram_used=vram_used,
                steps=request.num_inference_steps,
                guidance=request.guidance_scale,
                resolution=(request.width, request.height)
            )
            
            # Aggressive cleanup for GTX 1070
            GTX1070Optimizer.cleanup_memory()
            
            return GenerationResponse(
                image=img_str,
                generation_time=generation_time,
                vram_used=vram_used
            )
            
        except Exception as e:
            # Clean up on error
            GTX1070Optimizer.cleanup_memory()
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Initialize FastAPI app
app = FastAPI(title="VisionCraft Pro", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML file at root
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api")
async def api_root():
    return {"message": "VisionCraft Pro API", "status": "running"}

@app.get("/api/cuda-status")
async def get_cuda_status():
    """Get CUDA and GPU PyTorch status"""
    if not hasattr(generator, 'cuda_checker'):
        return {"error": "CUDA checker not initialized"}
    
    cuda_results = generator.cuda_checker.check_cuda_availability()
    return cuda_results

@app.post("/install-gpu-torch")
async def install_gpu_torch():
    """Install GPU-enabled PyTorch"""
    if not hasattr(generator, 'cuda_checker'):
        return {"error": "CUDA checker not initialized"}
    
    success = generator.cuda_checker.install_gpu_pytorch()
    return {"success": success, "message": "GPU PyTorch installation completed. Please restart the application."}

@app.post("/refresh-generators")
async def refresh_generators():
    """Refresh modern generators list"""
    try:
        generator.modern_manager._setup_leonardo_ai()
        return {"success": True, "message": "Generators refreshed successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Initialize image generator
generator = ImageGenerator()

@app.get("/status")
async def get_status():
    """Get system status including VRAM usage"""
    if generator is None:
        return {"error": "Generator not initialized"}
    
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
    else:
        allocated = reserved = total = 0
    
    status = {
        "device": generator.device,
        "model_loaded": generator.model_loaded,
        "vram_allocated": allocated,  # Memory actually used by tensors
        "vram_reserved": reserved,    # Memory reserved by PyTorch (closer to Task Manager)
        "vram_total": total,
        "vram_used_percent": (reserved / total * 100) if total > 0 else 0,
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
    }
    return status

@app.post("/generate")
async def generate_image(request: GenerationRequest):
    """Generate image from text prompt"""
    start_time = time.time()
    
    if generator.current_generator_type == "modern":
        # Use modern generator
        return await generator._generate_with_modern_async(request, start_time)
    else:
        # Use local model
        return generator._generate_with_local(request, start_time)

@app.post("/enhance-prompt")
async def enhance_prompt(request: dict):
    """Advanced AI-powered prompt enhancement"""
    prompt = request.get("prompt", "")
    style = request.get("style", "photorealistic")
    detail_level = request.get("detail_level", "medium")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    # Use the advanced prompt enhancer
    enhanced_prompt = PromptEnhancer.enhance_prompt(prompt, style, detail_level)
    
    # Also create multiple options for comparison
    all_enhancements = PromptEnhancer.create_multiple_enhancements(prompt)
    
    return {
        "original_prompt": prompt,
        "enhanced_prompt": enhanced_prompt,
        "style": style,
        "detail_level": detail_level,
        "all_enhancements": all_enhancements,
        "available_styles": PromptEnhancer.get_enhancement_options()
    }

@app.get("/enhance-styles")
async def get_enhance_styles():
    """Get available prompt enhancement styles"""
    return {
        "styles": PromptEnhancer.get_enhancement_options(),
        "detail_levels": {
            "low": "Minimal enhancement - adds basic quality terms",
            "medium": "Balanced enhancement - adds style and quality elements",
            "high": "Maximum enhancement - adds all professional details"
        }
    }

@app.get("/models")
async def get_available_models():
    """Get list of available models including modern generators"""
    local_models = generator.model_manager.get_compatible_models()
    modern_models = generator.modern_manager.get_available_generators()
    
    return {
        "local_models": local_models,
        "modern_generators": modern_models,
        "current_model": generator.current_model,
        "current_generator_type": generator.current_generator_type,
        "recommendations": {
            "local": generator.model_manager.get_model_recommendations(),
            "modern": generator.modern_manager.get_generator_recommendations()
        }
    }

@app.post("/set-api-key")
async def set_api_key(request: dict):
    """Set API key for a modern generator"""
    generator_name = request.get("generator_name")
    api_key = request.get("api_key")
    
    if not generator_name or not api_key:
        raise HTTPException(status_code=400, detail="Generator name and API key required")
    
    if generator_name not in generator.modern_manager.available_generators:
        raise HTTPException(status_code=404, detail="Generator not found")
    
    generator.modern_manager.set_api_key(generator_name, api_key)
    
    return {"message": f"API key set for {generator.modern_manager.available_generators[generator_name]['name']}"}

@app.get("/modern-generators")
async def get_modern_generators():
    """Get information about available modern generators"""
    return {
        "generators": generator.modern_manager.get_available_generators(),
        "api_keys_set": list(generator.modern_manager.api_keys.keys()),
        "recommendations": generator.modern_manager.get_generator_recommendations(),
        "webhook_endpoints": generator.modern_manager.get_webhook_endpoints(),
        "leonardo_options": generator.modern_manager.get_leonardo_options()
    }

@app.post("/webhook/leonardo/{callback_id}")
async def leonardo_webhook(callback_id: str, webhook_data: dict):
    """Handle Leonardo.ai webhook callbacks"""
    try:
        generator.modern_manager.handle_leonardo_callback(callback_id, webhook_data)
        return {"status": "success", "callback_id": callback_id}
    except Exception as e:
        print(f"[ERROR] Leonardo webhook error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/webhook-status")
async def get_webhook_status():
    """Get current webhook status and pending callbacks"""
    pending_count = 0
    if hasattr(generator.modern_manager, 'pending_callbacks'):
        pending_count = len(generator.modern_manager.pending_callbacks)
    
    return {
        "pending_callbacks": pending_count,
        "webhook_url": "http://localhost:8000/webhook/leonardo/{callback_id}",
        "status": "active" if pending_count > 0 else "idle"
    }

@app.get("/gallery")
async def get_gallery():
    """Get recent images from gallery"""
    return {
        "images": generator.gallery.get_recent_images(limit=50),
        "stats": generator.gallery.get_stats()
    }

@app.get("/gallery/{image_id}")
async def get_gallery_image(image_id: str):
    """Get specific image from gallery"""
    image_data = generator.gallery.get_image_data(image_id)
    if image_data:
        metadata = generator.gallery.get_image_by_id(image_id)
        return {
            "image": image_data,
            "metadata": metadata
        }
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.delete("/gallery/{image_id}")
async def delete_gallery_image(image_id: str):
    """Delete image from gallery"""
    success = generator.gallery.delete_image(image_id)
    if success:
        return {"message": "Image deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.get("/gallery/search")
async def search_gallery(q: str = "", model: str = "", limit: int = 20):
    """Search gallery images"""
    return {
        "images": generator.gallery.search_images(query=q, model=model, limit=limit)
    }

@app.post("/load_model/{model_name}")
async def load_model_endpoint(model_name: str):
    """Load a specific model"""
    success = generator.load_model(model_name)
    if success:
        return {"message": f"Model {model_name} loaded successfully", "current_model": generator.model_manager.current_model}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to load model: {model_name}")

@app.post("/load_model")
async def load_model():
    """Load the model (legacy endpoint)"""
    generator.load_model()
    return {"message": "Model loaded successfully"}

if __name__ == "__main__":
    import logging
    
    # Suppress connection reset errors (harmless)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    
    print("[ART] Starting VisionCraft Pro...")
    print("[WEB] Open http://localhost:8000 in your browser")
    print("[IMAGE] Gallery persistence enabled - images are saved!")
    print("[SPARKLE] Enhanced UI with gradients and animations")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
