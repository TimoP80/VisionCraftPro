"""
VisionCraft Pro Server
Main FastAPI server with all endpoints
"""

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
import os
import json
import urllib.parse
import urllib.request
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
    
    # Modal specific parameters
    modal_model: Optional[str] = "runwayml/stable-diffusion-v1-5"  # Modal model selection

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
        print(f"[SEARCH] Checking if '{model_key}' is in available generators...")
        
        # Check if this is a modern generator
        if model_key in self.modern_manager.available_generators:
            print(f"[SEARCH] Found '{model_key}' in modern generators!")
            self.current_generator_type = "modern"
            self.current_model = model_key
            self.model_loaded = True
            print(f"[OK] Modern generator selected: {self.modern_manager.available_generators[model_key]['name']}")
            print(f"[SEARCH] Generator type set to: {self.current_generator_type}")
            print(f"[SEARCH] Model key: {model_key}")
            return True
        else:
            print(f"[SEARCH] '{model_key}' NOT found in modern generators!")
            print(f"[SEARCH] Available keys: {list(self.modern_manager.available_generators.keys())}")
            # Don't try to load as local model if it's not a valid local model
            print(f"[ERROR] Unknown model: {model_key}")
            return False
    
    def get_status(self):
        """Get current system status"""
        if torch.cuda.is_available():
            vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            vram_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            vram_used = torch.cuda.memory_allocated(0) / (1024**3)
            vram_free = vram_total - vram_reserved
            vram_used_percent = (vram_used / vram_total) * 100
            
            return {
                "device": f"{torch.cuda.get_device_name(0)} (CUDA)",
                "vram_total": vram_total,
                "vram_free": vram_free,
                "vram_used": vram_used,
                "vram_reserved": vram_reserved,
                "vram_used_percent": vram_used_percent,
                "model_loaded": self.model_loaded,
                "current_model": self.current_model,
                "current_generator_type": self.current_generator_type,
                "gpu_name": torch.cuda.get_device_name(0),
                "cuda_version": torch.version.cuda,
                "torch_version": torch.__version__,
                "optimal_settings": self.model_manager.get_optimal_settings() if self.current_generator_type == "local" else None
            }
        else:
            return {
                "device": "CPU",
                "vram_total": 0,
                "vram_free": 0,
                "vram_used": 0,
                "vram_reserved": 0,
                "vram_used_percent": 0,
                "model_loaded": self.model_loaded,
                "current_model": self.current_model,
                "current_generator_type": self.current_generator_type,
                "gpu_name": "CPU",
                "cuda_version": "N/A",
                "torch_version": torch.__version__,
                "optimal_settings": None
            }
    
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image using current model"""
        if not self.model_loaded:
            raise HTTPException(status_code=400, detail="No model loaded")
        
        start_time = time.time()
        
        print(f"[DEBUG] Current generator type: {self.current_generator_type}")
        print(f"[DEBUG] Current model: {self.current_model}")
        print(f"[DEBUG] Request model: {request.model}")
        
        if self.current_generator_type == "modern":
            print(f"[DEBUG] Using modern generator: {self.current_model}")
            # Use modern generator
            kwargs = {
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
            
            # Add Modal specific parameters if available
            if hasattr(request, 'modal_model') and request.modal_model:
                kwargs['model'] = request.modal_model  # Pass specific Modal model
            
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
        else:
            print(f"[DEBUG] Using local generator: {self.current_model}")
            # Use local model
            if self.current_generator_type == "local":
                # Set seed for reproducibility
                if request.seed != -1:
                    torch.manual_seed(request.seed)
                    np.random.seed(request.seed)
                
                # Generate image
                image = self.model_manager.generate_image(
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    num_inference_steps=request.num_inference_steps,
                    guidance_scale=request.guidance_scale,
                    width=request.width,
                    height=request.height
                )
                
                generation_time = time.time() - start_time
                
                # Get VRAM usage
                if torch.cuda.is_available():
                    vram_used = torch.cuda.memory_allocated(0) / (1024**3)
                else:
                    vram_used = 0.0
                
                # Convert to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
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
            else:
                raise HTTPException(status_code=400, detail="No valid generator loaded")

# Initialize FastAPI app
app = FastAPI(title="VisionCraft Pro API", version="1.1.6")

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

# Initialize generator
generator = ImageGenerator()

# Load default model
generator.load_model("stable-diffusion-1.5")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return FileResponse("static/index.html")

@app.get("/status")
async def get_status():
    """Get system status"""
    return generator.get_status()

@app.get("/models")
async def get_models():
    """Get available models"""
    local_models = generator.model_manager.get_available_models()
    modern_generators = generator.modern_manager.get_available_generators()
    return {
        "local_models": local_models,
        "modern_generators": modern_generators
    }

@app.post("/generate")
async def generate_image(request: GenerationRequest):
    """Generate image"""
    try:
        return await generator.generate_image(request)
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class LoadModelRequest(BaseModel):
    model_name: str

@app.post("/load-model")
async def load_model(request: LoadModelRequest):
    """Load a specific model"""
    print(f"[API] /load-model called with model_name: {request.model_name}")
    try:
        success = generator.load_model(request.model_name)
        print(f"[API] load_model result: {success}")
        if success:
            return {"message": f"Model {request.model_name} loaded successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load model {request.model_name}")
    except Exception as e:
        print(f"[API] load_model error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gallery")
async def get_gallery():
    """Get image gallery"""
    images = generator.gallery.get_images()
    stats = generator.gallery.get_stats()
    return {
        "images": images,
        "stats": stats
    }

@app.get("/gallery/search")
async def search_gallery(q: str = ""):
    """Search gallery images by prompt text"""
    images = generator.gallery.search_images(query=q, limit=50)
    return {"images": images}

@app.get("/gallery/{image_id}")
async def get_gallery_image(image_id: str):
    """Get a single gallery image as base64 plus metadata"""
    image_b64 = generator.gallery.get_image_data(image_id)
    metadata = generator.gallery.get_image_by_id(image_id)

    if not image_b64 or not metadata:
        raise HTTPException(status_code=404, detail="Image not found")

    return {"image": image_b64, "metadata": metadata}

@app.delete("/gallery/{image_id}")
async def delete_gallery_image(image_id: str):
    """Delete a single gallery image"""
    ok = generator.gallery.delete_image(image_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "deleted"}

@app.delete("/gallery")
async def clear_gallery():
    """Clear the entire gallery"""
    generator.gallery.clear_gallery()
    return {"message": "cleared"}

@app.get("/hf/models")
async def hf_search_models(q: str = "", limit: int = 20):
    """Search Hugging Face for Stable Diffusion / diffusers-compatible text-to-image models"""
    try:
        limit = max(1, min(int(limit), 50))
    except Exception:
        limit = 20

    params = {
        "search": q or "stable diffusion",
        "limit": str(limit),
        "pipeline_tag": "text-to-image",
        "library": "diffusers",
        "sort": "downloads",
        "direction": "-1",
    }
    url = "https://huggingface.co/api/models?" + urllib.parse.urlencode(params)

    headers = {
        "Accept": "application/json",
        "User-Agent": "VisionCraftPro/1.0",
    }
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)

    results = []
    for item in data or []:
        model_id = item.get("modelId") or item.get("id")
        if not model_id:
            continue
        results.append(
            {
                "id": model_id,
                "likes": item.get("likes", 0),
                "downloads": item.get("downloads", 0),
                "pipeline_tag": item.get("pipeline_tag"),
                "library_name": item.get("library_name"),
                "tags": item.get("tags", []),
                "private": item.get("private", False),
                "gated": item.get("gated", False),
            }
        )

    return {"models": results}

@app.get("/debug-state")
async def debug_state():
    """Debug endpoint to check current server state"""
    return {
        "current_generator_type": generator.current_generator_type,
        "current_model": generator.current_model,
        "model_loaded": generator.model_loaded,
        "available_modern_generators": list(generator.modern_manager.available_generators.keys()),
        "available_local_models": list(generator.model_manager.get_available_models().keys())
    }

@app.post("/enhance-prompt")
async def enhance_prompt(request: dict):
    """Enhance prompt using AI"""
    try:
        prompt = request.get("prompt", "")
        style = request.get("style", "cinematic")
        detail_level = request.get("detail_level", "medium")
        
        # Use prompt enhancer
        enhancer = PromptEnhancer()
        enhanced = enhancer.enhance_prompt(prompt, style, detail_level)
        
        return {
            "original_prompt": prompt,
            "enhanced_prompt": enhanced["prompt"],
            "style": style,
            "detail_level": detail_level,
            "all_enhancements": enhanced["all_enhancements"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/modern-generators")
async def get_modern_generators():
    """Get modern generators info"""
    return {
        "available_generators": generator.modern_manager.available_generators,
        "api_keys_set": list(generator.modern_manager.api_keys.keys())
    }

@app.post("/set-api-key")
async def set_api_key(request: dict):
    """Set API key for modern generator"""
    try:
        generator_name = request.get("generator_name")
        api_key = request.get("api_key")
        
        if not generator_name or not api_key:
            raise HTTPException(status_code=400, detail="generator_name and api_key required")
        
        generator.modern_manager.set_api_key(generator_name, api_key)
        
        return {"message": f"API key set for {generator_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Leonardo.ai webhook endpoints
@app.post("/webhook/leonardo/{callback_id}")
async def leonardo_webhook(callback_id: str, data: dict):
    """Handle Leonardo.ai webhook callbacks"""
    try:
        result = generator.modern_manager.handle_leonardo_callback(callback_id, data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import logging
    
    # Suppress connection reset errors (harmless)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    
    print("[ART] Starting VisionCraft Pro Server...")
    print("[WEB] Open http://localhost:8000 in your browser")
    print("[IMAGE] Gallery persistence enabled - images are saved!")
    print("[SPARKLE] Enhanced UI with gradients and animations")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
