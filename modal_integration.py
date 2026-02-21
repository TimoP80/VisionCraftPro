"""
Modal Integration for VisionCraft Pro
Remote H100 GPU generation via Modal platform

IMPORTANT: This runs on Modal's cloud infrastructure, NOT on your local machine!
"""

import modal
import io
import base64
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline
import asyncio
from datetime import datetime
import os

# Modal app configuration
app = modal.App("visioncraft-modal")

# Modal image with GPU - this runs on Modal's infrastructure
@app.function(
    image=modal.Image.debian_slim().pip_install(
        "torch",
        "torchvision", 
        "diffusers",
        "transformers",
        "accelerate",
        "pillow",
        "numpy"
    ),
    gpu=modal.gpu.A100(),  # This runs on Modal's A100/H100 GPUs in the cloud
    timeout=300,
    secrets=[
        modal.Secret.from_name("huggingface-token"),
    ]
)
def generate_image(prompt: str, model_name: str = "runwayml/stable-diffusion-v1-5") -> bytes:
    """
    Generate image using Modal H100 GPU (REMOTE EXECUTION)
    
    This function runs entirely on Modal's cloud infrastructure,
    NOT on your local machine or local GPU.
    
    Args:
        prompt: Text prompt for image generation
        model_name: Model to use (default: runwayml/stable-diffusion-v1-5)
        
    Returns:
        PNG image bytes
    """
    print(f"[MODAL-REMOTE] Generating with {model_name}: {prompt[:100]}...")
    print(f"[MODAL-REMOTE] Running on Modal cloud GPU (NOT local GPU)")
    
    # Check if we're running on Modal infrastructure
    if not torch.cuda.is_available():
        print("[MODAL-REMOTE] ERROR: CUDA not available on Modal infrastructure")
        raise RuntimeError("CUDA not available on Modal infrastructure")
    
    print(f"[MODAL-REMOTE] Using GPU: {torch.cuda.get_device_name(0)}")
    print(f"[MODAL-REMOTE] CUDA Version: {torch.version.cuda}")
    
    # Load model on Modal's GPU
    pipe = StableDiffusionPipeline.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe = pipe.to("cuda")  # This is Modal's CUDA, not local
    
    print(f"[MODAL-REMOTE] Model loaded on Modal GPU")
    
    # Generate image on Modal's GPU
    with torch.autocast("cuda"):
        result = pipe(prompt, num_inference_steps=20, guidance_scale=7.5)
        image = result.images[0]
    
    print(f"[MODAL-REMOTE] Generated image: {image.size}")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    print(f"[MODAL-REMOTE] Returning {len(img_bytes.getvalue())} bytes")
    return img_bytes.getvalue()

# Alternative function for different models
@app.function(
    image=modal.Image.debian_slim().pip_install(
        "torch",
        "torchvision", 
        "diffusers",
        "transformers",
        "accelerate",
        "pillow",
        "numpy"
    ),
    gpu=modal.gpu.A100(),
    timeout=300,
)
def generate_image_sdxl(prompt: str, model_name: str = "stabilityai/stable-diffusion-xl-base-1.0") -> bytes:
    """
    Generate image using SDXL on Modal H100
    
    Args:
        prompt: Text prompt for image generation
        model_name: SDXL model to use
        
    Returns:
        PNG image bytes
    """
    print(f"[MODAL] SDXL generation with {model_name}: {prompt[:100]}...")
    
    # Load SDXL pipeline
    from diffusers import StableDiffusionXLPipeline
    
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        variant="fp16"
    )
    pipe = pipe.to("cuda")
    
    # Generate image (SDXL works best with 1024x1024)
    with torch.autocast("cuda"):
        result = pipe(prompt, num_inference_steps=30, guidance_scale=7.5, height=1024, width=1024)
        image = result.images[0]
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print(f"[MODAL] SDXL generated image: {image.size}")
    return img_bytes.getvalue()

if __name__ == "__main__":
    # Test locally (for development)
    import sys
    
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        model = sys.argv[2] if len(sys.argv) > 2 else "runwayml/stable-diffusion-v1-5"
        
        print(f"Testing Modal generation locally...")
        print(f"Prompt: {prompt}")
        print(f"Model: {model}")
        
        # This would normally be called via Modal API
        # result = generate_image.remote(prompt, model)
        # print(f"Generated {len(result)} bytes")
    else:
        print("Usage: python modal_integration.py <prompt> [model_name]")
        print("Example: python modal_integration.py 'a beautiful sunset' runwayml/stable-diffusion-v1-5")
