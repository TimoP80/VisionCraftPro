"""
VisionCraft Pro Server
Main FastAPI server with all endpoints
"""

import torch
import gc
import hmac
import time
import hashlib
import threading
import logging
from collections import defaultdict
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from transformers import CLIPTextModel, CLIPTokenizer
from PIL import Image
import numpy as np
import io
import base64
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import os
import json
import urllib.parse
import urllib.request
import uvicorn
import psutil

from modern_generators import ModernGeneratorManager
from video_generator_manager import VideoGeneratorManager
from image_gallery import ImageGallery
from prompt_enhancer import PromptEnhancer
from cuda_checker import CudaChecker
from local_model_manager import LocalModelManager

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[ENV] Loaded environment variables from .env file")
except ImportError:
    print("[ENV] python-dotenv not available, skipping .env file loading")
except Exception as e:
    print(f"[ENV] Error loading .env file: {e}")

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
    modal_model: Optional[str] = None  # Modal model selection
    modal_gpu: Optional[str] = None    # Modal GPU selection

class GenerationResponse(BaseModel):
    image: str
    generation_time: float
    vram_used: float

class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="Text prompt for video generation")
    model_id: str = Field(..., min_length=1, description="Video model ID to use")
    negative_prompt: str = Field(default="", max_length=1000, description="Negative prompt")
    duration: str = Field(default="5 seconds", description="Video duration")
    aspect_ratio: str = Field(default="16:9", description="Video aspect ratio")
    image_url: Optional[str] = Field(default=None, description="Image URL for image-to-video")
    
    @validator('prompt')
    def prompt_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('prompt cannot be empty or whitespace-only')
        return v.strip()
    
    @validator('duration')
    def validate_duration(cls, v):
        # Allow common durations
        allowed = ['3 seconds', '5 seconds', '6 seconds', '8 seconds', '10 seconds', 
                  '15 seconds', '20 seconds', '30 seconds', '1 minute', '2 minutes', '3 minutes']
        if v not in allowed:
            # Don't fail, just warn and use default
            return "5 seconds"
        return v
    
    @validator('aspect_ratio')
    def validate_aspect_ratio(cls, v):
        allowed = ['16:9', '9:16', '4:3', '1:1', '21:9']
        if v not in allowed:
            return "16:9"
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "A beautiful sunset over the ocean",
                "model_id": "runway-gen3-alpha",
                "negative_prompt": "blurry, low quality",
                "duration": "5 seconds",
                "aspect_ratio": "16:9"
            }
        }

class VideoGenerationResponse(BaseModel):
    """Response model for video generation"""
    success: bool
    video_url: str
    thumbnail_url: str
    generation_time: float
    model_used: str
    model_id: str
    provider: str
    message: Optional[str] = None

# Simple in-memory rate limiter for video endpoints
class SimpleRateLimiter:
    """Thread-safe rate limiter using sliding window algorithm"""
    def __init__(self):
        self.requests = defaultdict(list)  # client_id -> list of timestamps
        self._lock = threading.Lock()  # Thread safety for concurrent requests
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # Cleanup every 5 minutes
        self._request_count = 0  # Track requests since last cleanup
        self._cleanup_threshold = 100  # Cleanup every 100 requests
        
    def _cleanup_needed(self) -> bool:
        """Check if cleanup is needed based on time or request count"""
        now = time.time()
        return (now - self._last_cleanup >= self._cleanup_interval or 
                self._request_count >= self._cleanup_threshold)
    
    def _cleanup_stale_entries(self, force: bool = False):
        """Remove stale client entries to prevent memory leak
        
        Args:
            force: If True, run cleanup regardless of time interval (e.g., when triggered by request count)
        """
        now = time.time()
        # Only run cleanup periodically, not on every request
        # Unless force=True (triggered by request count threshold)
        if not force and now - self._last_cleanup < self._cleanup_interval:
            return
        
        # Remove clients with no requests in the last hour
        stale_clients = [
            client_id for client_id, timestamps in self.requests.items()
            if not timestamps or (now - max(timestamps)) > 3600
        ]
        for client_id in stale_clients:
            del self.requests[client_id]
        
        self._last_cleanup = now
        if stale_clients:
            print(f"[RATE_LIMITER] Cleaned up {len(stale_clients)} stale entries")
    
    def is_allowed(self, client_id: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """Check if request is allowed under rate limit (thread-safe)"""
        with self._lock:
            # Check if cleanup is needed
            cleanup_needed = self._cleanup_needed()
            now = time.time()
            time_cleanup_due = now - self._last_cleanup >= self._cleanup_interval
            
            # Run cleanup: force=True if triggered by request count, otherwise use time-based decision
            if cleanup_needed:
                force_cleanup = not time_cleanup_due  # Force if triggered by request count threshold
                self._cleanup_stale_entries(force=force_cleanup)
                self._request_count = 0
            else:
                self._request_count += 1
            
            # Remove requests outside the window
            self.requests[client_id] = [
                ts for ts in self.requests[client_id] 
                if now - ts < window_seconds
            ]
            if len(self.requests[client_id]) >= max_requests:
                return False
            self.requests[client_id].append(now)
            return True
    
    def get_remaining(self, client_id: str, max_requests: int = 10, window_seconds: int = 60) -> int:
        """Get remaining requests in current window (thread-safe)"""
        with self._lock:
            now = time.time()
            # Only filter timestamps - don't modify _request_count (read-only operation)
            self.requests[client_id] = [
                ts for ts in self.requests[client_id] 
                if now - ts < window_seconds
            ]
            return max(0, max_requests - len(self.requests[client_id]))

# Global rate limiter instance
video_rate_limiter = SimpleRateLimiter()

# Track IP warnings - only warn once at startup
_ip_warning_printed = False

def get_client_id(request) -> str:
    """Extract client identifier from request for rate limiting.
    
    NOTE: This uses IP-based identification as fallback when no API key is provided.
    This can cause shared rate limits in NAT environments, corporate proxies, or CDN.
    For better isolation, clients should include their API key in the X-API-Key header.
    
    Security recommendation: Always require API keys for rate-limited endpoints in production."""
    global _ip_warning_printed
    
    # Warn once at startup about IP-based rate limiting
    if not _ip_warning_printed:
        logging.getLogger(__name__).warning(
            "[RATE_LIMITER] Using IP-based client ID as fallback. "
            "This may cause shared rate limits in NAT environments. "
            "Recommend using X-API-Key header for better isolation."
        )
        _ip_warning_printed = True
    
    # Try to get API key as client ID, fall back to IP address
    if hasattr(request, 'headers'):
        # FastAPI Request
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Use full hashed API key for better collision resistance
            return hashlib.sha256(api_key.encode()).hexdigest()
        
        # Try to get client IP from X-Forwarded-For header (for reverse proxy setups)
        # Format: "X-Forwarded-For: client, proxy1, proxy2" - use first (leftmost) IP
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # Get the first (leftmost) IP which is the original client
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Fall back to direct client IP
            client_ip = request.client.host if request.client else "unknown"
        return client_ip
    return "unknown"

def get_public_ip():
    """Get the public IP address of the server"""
    services = [
        'https://api.ipify.org',
        'https://ifconfig.me/ip',
        'https://icanhazip.com',
        'https://ident.me'
    ]
    
    print("[SERVER] Detecting public IP address...")
    for service in services:
        try:
            with urllib.request.urlopen(service, timeout=5) as response:
                ip = response.read().decode('utf-8').strip()
                if ip:
                    return ip
        except Exception:
            continue
    return "Unknown"

class ImageGenerator:
    """Main image generation class with both local and modern generators"""
    
    def __init__(self):
        # Check CUDA and GPU PyTorch availability first
        print("[CUDA] Checking CUDA and GPU PyTorch availability...")
        self.cuda_checker = CudaChecker()
        cuda_results = self.cuda_checker.check_cuda_availability()
        
        if cuda_results['system_gpu_available'] and not cuda_results['gpu_torch_available']:
            print("[CUDA] NVIDIA GPU detected but GPU PyTorch not available")
            print("[CUDA] Attempting to install GPU PyTorch...")
            self.cuda_checker.install_gpu_pytorch()
            print("[CUDA] Please restart the application after GPU PyTorch installation")
        
        self.model_manager = LocalModelManager()
        self.modern_manager = ModernGeneratorManager()
        self.video_manager = VideoGeneratorManager()
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
        
        # Log Public IP
        public_ip = get_public_ip()
        print(f"[SERVER] Public IP: {public_ip}")
        print(f"[SERVER] Access URL: http://{public_ip}:8000")
        
    def load_model(self, model_key: str = "stable-diffusion-1.5"):
        """Load a specific model or modern generator"""
        print(f"[RELOAD] Loading model: {model_key}")
        
        # Check if this is a modern generator
        if model_key in self.modern_manager.available_generators:
            self.current_generator_type = "modern"
            self.current_model = model_key
            self.model_loaded = True
            return True
            
        # Check if this is a local model
        success = self.model_manager.load_model(model_key)
        if success:
            self.current_generator_type = "local"
            self.current_model = model_key
            self.model_loaded = True
            return True
            
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
                "public_ip": get_public_ip(),
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
                "public_ip": get_public_ip(),
                "optimal_settings": None
            }
    
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image using current model"""
        # Ensure the correct generator is selected for this request.
        # The UI attempts to call /load-model on selection changes, but we also enforce it here
        # so API clients (or failed /load-model calls) can't accidentally fall back to local generation.
        if request.model and request.model != self.current_model:
            self.load_model(request.model)

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
            if self.current_model == 'leonardo-api':
                if hasattr(request, 'aspect_ratio'):
                    kwargs['aspect_ratio'] = request.aspect_ratio
                if hasattr(request, 'preset_style'):
                    kwargs['preset_style'] = request.preset_style
                if hasattr(request, 'quality'):
                    kwargs['quality'] = request.quality
                if hasattr(request, 'leonardo_model') and request.leonardo_model:
                    kwargs['model'] = request.leonardo_model  # Pass specific Leonardo model

            # Add Modal specific parameters if available
            if self.current_model == 'modal':
                if hasattr(request, 'modal_model') and request.modal_model:
                    kwargs['model'] = request.modal_model  # Pass specific Modal model
                if hasattr(request, 'modal_gpu') and request.modal_gpu:
                    kwargs['gpu'] = request.modal_gpu      # Pass specific Modal GPU
            
            print(f"[SEARCH] Modern generator kwargs: {kwargs}")
            
            # Generate with modern API
            image = await self.modern_manager.generate_image(
                self.current_model,
                request.prompt,
                **kwargs
            )
        else:
            # Local generation
            print(f"[DEBUG] Using local generator: {self.current_model}")
            
            image = self.model_manager.generate(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                width=request.width,
                height=request.height
            )
            
        generation_time = time.time() - start_time
        vram_used = 0.0 # Could calculate if needed
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        print(f"[OK] Generation completed in {generation_time:.2f}s")
        
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

# Don't load a default model - let users choose
# generator.load_model("stable-diffusion-1.5")

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
    try:
        local_models = generator.model_manager.get_downloaded_models()
        modern_generators = generator.modern_manager.get_available_generators()
        return {
            "local_models": {m["id"]: m for m in local_models},
            "modern_generators": modern_generators
        }
    except Exception as e:
        print(f"[SERVER] Error in /models endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/local/download")
async def download_local_model(request: dict):
    """Download a model from Hugging Face for local use"""
    repo_id = request.get("repo_id")
    if not repo_id:
        raise HTTPException(status_code=400, detail="repo_id is required")
    
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    return generator.model_manager.download_model(repo_id, token=hf_token)

@app.get("/local/status/{model_id:path}")
async def get_local_model_status(model_id: str):
    """Get download status of a local model"""
    return {"status": generator.model_manager.get_status(model_id)}

@app.get("/local/models")
async def list_local_models():
    """List all downloaded local models"""
    return {"models": generator.model_manager.get_downloaded_models()}

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
        # Check if model actually exists in available models
        available_models = generator.model_manager.get_downloaded_models()
        available_model_ids = [m["id"] for m in available_models]
        
        print(f"[API] Available models: {available_model_ids}")
        print(f"[API] Requested model: {request.model_name}")
        
        if request.model_name not in available_model_ids:
            print(f"[API] Model {request.model_name} not found in available models")
            raise HTTPException(status_code=404, detail=f"Model {request.model_name} is not available locally. Please download it first.")
        
        success = generator.load_model(request.model_name)
        print(f"[API] load_model result: {success}")
        if success:
            return {"message": f"Model {request.model_name} loaded successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load model {request.model_name}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] load_model error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error while loading model: {str(e)}")

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
    try:
        image_b64 = generator.gallery.get_image_data(image_id)
        metadata = generator.gallery.get_image_by_id(image_id)

        if not image_b64 or not metadata:
            raise HTTPException(status_code=404, detail="Image not found")

        return {"image": image_b64, "metadata": metadata}
    except MemoryError:
        raise HTTPException(status_code=500, detail="Image too large to load")
    except Exception as e:
        print(f"[ERROR] Gallery image error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/gallery")
async def add_to_gallery(request: dict):
    """Add an image to the gallery"""
    try:
        image_data = request.get("image")
        prompt = request.get("prompt", "No prompt")
        model = request.get("model", "unknown")
        generation_time = request.get("generation_time", 0)
        vram_used = request.get("vram_used", 0)
        steps = request.get("steps", 20)
        guidance = request.get("guidance", 7.5)
        resolution = request.get("resolution", [512, 512])
        
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove data URL prefix if present
        if image_data.startswith("data:image/"):
            image_data = image_data.split(",", 1)[1]
        
        image_id = generator.gallery.add_image(
            image_data=image_data,
            prompt=prompt,
            model=model,
            generation_time=generation_time,
            vram_used=vram_used,
            steps=steps,
            guidance=guidance,
            resolution=resolution
        )
        
        return {
            "message": "Image added to gallery",
            "image_id": image_id
        }
    except Exception as e:
        print(f"[ERROR] Failed to add to gallery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/local/status/{repo_id}")
async def get_local_model_status(repo_id: str):
    """Get download status of a local model"""
    status = generator.model_manager.get_status(repo_id)
    progress = generator.model_manager.get_progress(repo_id)
    return {"status": status, "progress": progress}

@app.get("/local/progress-updates")
async def get_progress_updates():
    """Get all pending progress updates"""
    updates = generator.model_manager.get_progress_updates()
    print(f"[PROGRESS] Returning {len(updates)} updates: {updates}")
    return {"updates": updates}

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
    """Enhance prompt using AI-powered templates"""
    try:
        prompt = request.get("prompt", "")
        style = request.get("style", "cinematic")
        detail_level = request.get("detail_level", "medium")
        model = request.get("model", "auto")  # Get model parameter
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        print(f"[ENHANCE] Processing prompt: '{prompt}' with style: {style}, model: {model}")
        
        # Use prompt enhancer instance
        enhancer = PromptEnhancer()
        result = await enhancer.enhance_prompt(prompt, style, detail_level, model)
        
        print(f"[ENHANCE] Success: AI enhanced={result.get('ai_enhanced', False)}, model_used={result.get('model_used', 'N/A')}")
        
        return result
    except Exception as e:
        print(f"[ERROR] Prompt enhancement failed: {e}")
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

# Video generation endpoints
@app.get("/video-models")
async def get_video_models(http_request: Request = None):
    """Get all available video generation models"""
    # Require authentication for this endpoint
    check_video_api_auth(http_request)
    return {
        "video_models": generator.video_manager.get_available_models(),
        "categories": generator.video_manager.get_categories(),
        "badges": generator.video_manager.get_badges()
    }

def check_video_api_auth(request = None):
    """Check API key authentication for video endpoints.
    
    Security model:
    - If VIDEO_API_KEY is set on the server, clients MUST provide matching X-API-Key header
    - If VIDEO_API_KEY is NOT set, requests are DENIED by default for security
    - For development only: set VIDEO_DEV_MODE=true to allow unauthenticated requests (NOT for production!)
    
    To enable authentication:
    - Set VIDEO_API_KEY environment variable on the server (required for production)
    - Clients must include 'X-API-Key' header in their requests
    
    Example (server-side):
        # Linux/macOS:
        export VIDEO_API_KEY=your-secret-key
        
        # Windows (CMD):
        set VIDEO_API_KEY=your-secret-key
        
        # Windows (PowerShell):
        $env:VIDEO_API_KEY="your-secret-key"
        
        # For development only (NOT for production):
        set VIDEO_DEV_MODE=true
    """
    server_api_key = os.environ.get("VIDEO_API_KEY")
    
    # Check if we're in development mode (bypass auth) - NOT for production!
    dev_mode = os.environ.get("VIDEO_DEV_MODE", "false").lower() in ("true", "1", "yes")
    
    # Detect production mode - deny bypass in production
    is_production = (
        os.environ.get("NODE_ENV") == "production" or
        os.environ.get("FLASK_ENV") == "production" or
        os.environ.get("FASTAPI_ENV") == "production" or
        os.environ.get("PRODUCTION") == "true" or
        os.environ.get("PROD") == "true"
    )
    
    if is_production and not server_api_key:
        # Production without API key - deny all requests
        print("[SECURITY] Production mode detected without VIDEO_API_KEY. Denying all requests for security.")
        raise HTTPException(
            status_code=401, 
            detail="Production mode requires VIDEO_API_KEY to be set. Video API is disabled."
        )
    
    if dev_mode and is_production:
        # Cannot enable dev mode in production - deny for security
        print("[SECURITY] ERROR: VIDEO_DEV_MODE cannot be enabled in production. Denying request.")
        raise HTTPException(
            status_code=401, 
            detail="Development mode is not allowed in production. Please configure VIDEO_API_KEY."
        )
    
    if dev_mode:
        # Development bypass enabled - log warning
        print("[SECURITY] WARNING: VIDEO_DEV_MODE is enabled. Authentication is disabled. NOT FOR PRODUCTION!")
        return True
    
    if not server_api_key:
        # No API key configured - DENY by default for security
        # This prevents accidental exposure in production
        print("[SECURITY] VIDEO_API_KEY not configured. Denying unauthenticated requests.")
        raise HTTPException(
            status_code=401, 
            detail="Video API authentication not configured. Set VIDEO_API_KEY environment variable for production, or VIDEO_DEV_MODE=true for development only."
        )
    
    # Handle both dict and FastAPI Request objects
    auth_header = None
    if hasattr(request, 'headers'):
        # FastAPI Request object
        auth_header = request.headers.get("X-API-Key")
    elif isinstance(request, dict):
        # Plain dictionary
        auth_header = request.get("api_key") or request.get("X-API-Key")
    
    # Use constant-time comparison to prevent timing attacks
    if not auth_header or not hmac.compare_digest(str(auth_header), str(server_api_key)):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

@app.get("/video-models/{model_id}")
async def get_video_model(model_id: str, http_request: Request = None):
    """Get a specific video model by ID"""
    check_video_api_auth(http_request)
    model = generator.video_manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Video model not found: {model_id}")
    return model

@app.get("/video-categories")
async def get_video_categories(http_request: Request = None):
    """Get all video categories"""
    check_video_api_auth(http_request)
    return {
        "categories": generator.video_manager.get_categories()
    }

@app.get("/video-models/category/{category_id}")
async def get_video_models_by_category(category_id: str, http_request: Request = None):
    """Get video models by category"""
    check_video_api_auth(http_request)
    models = generator.video_manager.get_models_by_category(category_id)
    return {
        "category_id": category_id,
        "models": models
    }

@app.get("/video-providers")
async def get_video_providers(http_request: Request = None):
    """Get video provider status"""
    check_video_api_auth(http_request)
    return {
        "providers": generator.video_manager.get_provider_status(),
        "api_keys_set": generator.video_manager.get_configured_providers()
    }

@app.post("/set-video-api-key")
async def set_video_api_key(request: dict, http_request: Request = None):
    """Set API key for video provider"""
    try:
        # Check admin authentication - require server's VIDEO_API_KEY to be set
        server_admin_key = os.environ.get("VIDEO_API_KEY")
        if not server_admin_key:
            # Also check for dedicated admin key env var
            server_admin_key = os.environ.get("VIDEO_API_ADMIN_KEY")
        
        if server_admin_key:
            # Verify the request includes valid admin credentials
            auth_header = http_request.headers.get("X-API-Key") if http_request else None
            if not auth_header or not hmac.compare_digest(str(auth_header), str(server_admin_key)):
                raise HTTPException(status_code=403, detail="Admin authentication required to set API keys")
        else:
            # No admin key configured - log security warning but allow for development
            # In production, always set VIDEO_API_KEY or VIDEO_API_ADMIN_KEY
            print("[WARNING] /set-video-api-key called without server admin key configured. "
                  "Set VIDEO_API_KEY or VIDEO_API_ADMIN_KEY environment variable for production.")
        
        provider = request.get("provider")
        api_key = request.get("api_key")
        
        if not provider or not api_key:
            raise HTTPException(status_code=400, detail="provider and api_key required")
        
        generator.video_manager.set_api_key(provider, api_key)
        
        return {"message": f"API key set for {provider}"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-video")
async def generate_video(request: VideoGenerationRequest, http_request: Request = None):
    """Generate video using specified model"""
    try:
        # Check optional API key authentication
        # Pass the FastAPI Request object directly for header-based auth
        check_video_api_auth(http_request)
        
        # Apply rate limiting - 10 requests per minute per client
        client_id = get_client_id(http_request) if http_request else "unknown"
        
        # Validate rate limit config from environment variables
        try:
            rate_limit_max = int(os.environ.get("VIDEO_RATE_LIMIT", "10"))
            if rate_limit_max < 1:
                rate_limit_max = 10
        except ValueError:
            rate_limit_max = 10
        
        try:
            rate_limit_window = int(os.environ.get("VIDEO_RATE_LIMIT_WINDOW", "60"))
            if rate_limit_window < 1:
                rate_limit_window = 60
        except ValueError:
            rate_limit_window = 60
        
        if not video_rate_limiter.is_allowed(client_id, rate_limit_max, rate_limit_window):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {rate_limit_max} requests per {rate_limit_window} seconds."
            )
        
        remaining = video_rate_limiter.get_remaining(client_id, rate_limit_max, rate_limit_window)
        
        result = await generator.video_manager.generate_video(
            model_id=request.model_id,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            image_url=request.image_url
        )
        
        # Add rate limit info to response
        result_with_limits = {
            **result,
            "rate_limit_remaining": remaining,
            "rate_limit_max": rate_limit_max,
            "rate_limit_window": rate_limit_window
        }
        
        return result_with_limits
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video-models/search")
async def search_video_models(q: str = "", http_request: Request = None):
    """Search video models"""
    check_video_api_auth(http_request)
    if not q:
        return {"models": []}
    results = generator.video_manager.search_models(q)
    return {"models": results, "query": q}

# Leonardo.ai webhook endpoints
@app.post("/webhook/leonardo/{callback_id}")
async def leonardo_webhook(callback_id: str, data: dict):
    """Handle Leonardo.ai webhook callbacks"""
    try:
        result = generator.modern_manager.handle_leonardo_callback(callback_id, data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/upscale/status/{job_id}")
async def get_upscale_status(job_id: str):
    """Get status of an upscaling job"""
    # This would typically check a job store/database
    # For now, return a placeholder response
    return {
        "job_id": job_id,
        "status": "unknown",  # Would be processing/completed/failed
        "message": f"Status requested for job {job_id}"
    }

@app.post("/upscale")
async def upscale_image(request: dict):
    """Upscale an image using Leonardo.ai Universal Upscaler"""
    try:
        # Get image data (base64 or URL)
        image_data = request.get("image")
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Get upscaling parameters
        upscale_factor = request.get("upscale_factor", 2.0)
        prompt = request.get("prompt", "")
        negative_prompt = request.get("negative_prompt", "")
        num_inference_steps = request.get("num_inference_steps", 20)
        guidance_scale = request.get("guidance_scale", 7.5)
        seed = request.get("seed", -1)
        
        # Convert base64 to PIL Image
        import base64
        from io import BytesIO
        from PIL import Image
        
        print(f"[UPSCALE] Received image: {image_data[:50]}..., upscaling by {upscale_factor}x")
        
        if image_data.startswith("data:image/"):
            # Remove data URL prefix
            image_data = image_data.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Create a unique job ID for tracking
        import uuid
        job_id = str(uuid.uuid4())
        
        # Run upscaling and wait for completion
        print(f"[UPSCALE] Starting upscaling job {job_id}")
        upscaled_image = await generator.modern_manager.upscale_with_leonardo(
            image=image,
            upscale_factor=upscale_factor,
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        # Convert to base64 for response
        output_buffer = BytesIO()
        upscaled_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        upscaled_b64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        print(f"[UPSCALE] Job {job_id} completed successfully")
        
        return {
            "success": True,
            "upscaled_image": f"data:image/png;base64,{upscaled_b64}",
            "job_id": job_id,
            "upscaled_size": f"{upscaled_image.width}x{upscaled_image.height}"
        }
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Upscaling failed: {e}")
        traceback.print_exc()
        
        # Provide user-friendly error messages
        error_message = str(e)
        if "500 Server Error" in str(e) or "internal error" in str(e):
            raise HTTPException(status_code=503, detail="Leonardo.ai is experiencing server issues. Please try again in a few minutes or switch to a different upscaling method.")
        elif "401" in str(e) or "unauthorized" in str(e).lower():
            raise HTTPException(status_code=401, detail="Leonardo.ai API key is invalid or missing. Please check your API key configuration.")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            raise HTTPException(status_code=403, detail="Leonardo.ai API access forbidden. Please check your API key permissions.")
        elif "429" in str(e) or "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="Leonardo.ai rate limit exceeded. Please wait a moment and try again.")
        elif "timeout" in str(e).lower():
            raise HTTPException(status_code=408, detail="Leonardo.ai request timed out. The service may be slow. Please try again.")
        elif "API key" in error_message.lower():
            raise HTTPException(status_code=401, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=f"Upscaling failed: {error_message}")


# Import TodoManager for todo endpoints
from todo_manager import TodoManager

# Initialize TodoManager
todo_manager = TodoManager()


class TodoCreateRequest(BaseModel):
    """Request model for creating a todo"""
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    tags: Optional[List[str]] = []
    due_date: Optional[str] = None


class TodoUpdateRequest(BaseModel):
    """Request model for updating a todo"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None


@app.get("/todos")
async def get_todos(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get all todos with optional filtering and sorting"""
    try:
        todos = todo_manager.get_all_todos(
            status=status,
            priority=priority,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return {
            "todos": [todo.to_dict() for todo in todos],
            "count": len(todos)
        }
    except Exception as e:
        print(f"[ERROR] Failed to get todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/todos/stats")
async def get_todo_stats():
    """Get todo statistics"""
    try:
        stats = todo_manager.get_stats()
        return stats
    except Exception as e:
        print(f"[ERROR] Failed to get todo stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/todos/search")
async def search_todos(q: str = ""):
    """Search todos by query string"""
    try:
        if not q:
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
        todos = todo_manager.search_todos(q)
        return {
            "todos": [todo.to_dict() for todo in todos],
            "count": len(todos)
        }
    except Exception as e:
        print(f"[ERROR] Failed to search todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/todos/{todo_id}")
async def get_todo(todo_id: str):
    """Get a specific todo by ID"""
    try:
        todo = todo_manager.get_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/todos")
async def create_todo(request: TodoCreateRequest):
    """Create a new todo"""
    try:
        todo = todo_manager.create_todo(
            title=request.title,
            description=request.description or "",
            status=request.status or "pending",
            priority=request.priority or "medium",
            tags=request.tags or [],
            due_date=request.due_date
        )
        return todo.to_dict()
    except Exception as e:
        print(f"[ERROR] Failed to create todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: str, request: TodoUpdateRequest):
    """Update an existing todo"""
    try:
        todo = todo_manager.update_todo(
            todo_id=todo_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            tags=request.tags,
            due_date=request.due_date
        )
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str):
    """Delete a todo"""
    try:
        success = todo_manager.delete_todo(todo_id)
        if not success:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"message": "Todo deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to delete todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: str):
    """Mark a todo as completed"""
    try:
        todo = todo_manager.complete_todo(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to complete todo: {e}")
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
    
    try:
        print("[DEBUG] Starting uvicorn server...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        print("[ERROR] Server startup failed - check dependencies and configuration")
