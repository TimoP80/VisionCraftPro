"""
Modal Integration for VisionCraft Pro
Remote H100 GPU generation via Modal platform
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

# Modal image with GPU
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
    secrets=[
        modal.Secret.from_name("huggingface-token", optional=True),
    ]
)
def generate_image(prompt: str, model_name: str = "runwayml/stable-diffusion-v1-5") -> bytes:
    """
    Generate image using Modal H100 GPU
    
    Args:
        prompt: Text prompt for image generation
        model_name: Model to use (default: runwayml/stable-diffusion-v1-5)
        
    Returns:
        PNG image bytes
    """
    print(f"[MODAL] Generating with {model_name}: {prompt[:100]}...")
    
    # Load model
    pipe = StableDiffusionPipeline.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe = pipe.to("cuda")
    
    # Generate image
    with torch.autocast("cuda"):
        result = pipe(prompt, num_inference_steps=20, guidance_scale=7.5)
        image = result.images[0]
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print(f"[MODAL] Generated image: {image.size}")
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
