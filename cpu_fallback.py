"""
CPU-optimized version of the image generator
Falls back to CPU when GPU is not available
"""

import torch
import gc
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import numpy as np
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import psutil
import time
import warnings

class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    num_inference_steps: Optional[int] = 15  # Reduced for CPU
    guidance_scale: Optional[float] = 7.5
    width: Optional[int] = 512
    height: Optional[int] = 512
    seed: Optional[int] = -1

class GenerationResponse(BaseModel):
    image: str
    generation_time: float
    device_used: str
    memory_used: float

class CPUImageGenerator:
    """CPU-optimized image generator for when GPU is not available"""
    
    def __init__(self):
        self.pipe = None
        self.device = "cpu"  # Force CPU
        self.model_loaded = False
        
    def load_model(self):
        """Load model optimized for CPU"""
        if self.model_loaded:
            return
            
        print("Loading model for CPU generation...")
        print("⚠️  Note: CPU generation is much slower than GPU")
        print("💡 Consider installing GPU-supported PyTorch for better performance")
        
        model_id = "runwayml/stable-diffusion-v1-5"
        
        # Load with CPU optimizations
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,  # Use float32 for CPU
            safety_checker=None,
            requires_safety_checker=False,
            use_safetensors=True
        )
        
        # Use CPU-optimized scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        
        # Move to CPU
        self.pipe = self.pipe.to(self.device)
        
        # Enable CPU memory efficient attention
        if hasattr(self.pipe, "enable_attention_slicing"):
            self.pipe.enable_attention_slicing()
            print("✅ Attention slicing enabled for CPU")
        
        # Enable sequential CPU offload (helps with memory)
        self.pipe.enable_sequential_cpu_offload()
        
        self.model_loaded = True
        print("Model loaded successfully for CPU generation!")
        
    def get_memory_usage(self):
        """Get current memory usage in GB"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / 1024**3
    
    def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image with CPU optimizations"""
        if not self.model_loaded:
            self.load_model()
        
        start_time = time.time()
        
        # Set seed if provided
        if request.seed != -1:
            generator = torch.Generator(device=self.device).manual_seed(request.seed)
        else:
            generator = None
            
        # CPU-specific optimizations
        print(f"🖥️  Generating on CPU (this will take 30-60 seconds)...")
        print(f"📝 Prompt: {request.prompt[:50]}...")
        
        try:
            # Generate with CPU optimizations
            with torch.no_grad():
                result = self.pipe(
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    num_inference_steps=min(request.num_inference_steps, 15),  # Limit steps for CPU
                    guidance_scale=request.guidance_scale,
                    width=min(request.width, 512),  # Limit resolution for CPU
                    height=min(request.height, 512),
                    generator=generator
                )
            
            image = result.images[0]
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_str = base64.b64encode(buffer.getvalue()).decode()
            
            generation_time = time.time() - start_time
            memory_used = self.get_memory_usage()
            
            # Clean up
            del result
            gc.collect()
            
            print(f"✅ Generation completed in {generation_time:.1f} seconds")
            
            return GenerationResponse(
                image=image_str,
                generation_time=generation_time,
                device_used="CPU",
                memory_used=memory_used
            )
            
        except Exception as e:
            gc.collect()
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Initialize FastAPI app
app = FastAPI(title="CPU Image Generator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generator
generator = CPUImageGenerator()

@app.get("/")
async def root():
    return {
        "message": "CPU Image Generator (GPU not available)",
        "note": "Consider installing GPU-supported PyTorch for better performance",
        "status": "running"
    }

@app.get("/status")
async def get_status():
    """Get system status"""
    memory_info = psutil.virtual_memory()
    process = psutil.Process()
    
    status = {
        "device": generator.device,
        "model_loaded": generator.model_loaded,
        "memory_used": generator.get_memory_usage(),
        "system_memory_percent": memory_info.percent,
        "cpu_percent": psutil.cpu_percent(),
        "gpu_available": torch.cuda.is_available(),
        "note": "Running in CPU mode - much slower than GPU",
        "recommendations": [
            "Install GPU-supported PyTorch for 10-20x faster generation",
            "Use lower resolution (512x512) for faster CPU generation",
            "Use fewer steps (10-15) for faster CPU generation"
        ]
    }
    return status

@app.post("/generate", response_model=GenerationResponse)
async def generate_image(request: GenerationRequest):
    """Generate an image from text prompt"""
    return generator.generate_image(request)

@app.post("/load_model")
async def load_model():
    """Load the model"""
    generator.load_model()
    return {"message": "Model loaded successfully"}

if __name__ == "__main__":
    print("🖥️  Starting CPU Image Generator...")
    print("⚠️  Note: This is much slower than GPU generation")
    print("💡 Install GPU-supported PyTorch for better performance")
    uvicorn.run(app, host="0.0.0.0", port=8000)
