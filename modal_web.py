"""
Modal web endpoint for VisionCraft - accessible via HTTP
"""

import modal
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import Response

# Create Modal app
app = modal.App("visioncraft-modal")

# Create FastAPI web app
web_app = FastAPI()

_PIPELINE_CACHE = {}

# Modal image with GPU
image = modal.Image.debian_slim().pip_install(
    "torch",
    "torchvision", 
    "diffusers",
    "transformers",
    "accelerate",
    "pillow",
    "numpy",
    "fastapi",
    "uvicorn"
)

# Modal function for image generation
@app.function(
    image=image,
    gpu="A100-40GB",
    timeout=300,
    secrets=[
        modal.Secret.from_name("huggingface-token"),
    ]
)
def generate_image_internal(
    prompt: str,
    model_name: str = "runwayml/stable-diffusion-v1-5",
    width: int = 512,
    height: int = 512,
    num_inference_steps: int = 20,
    guidance_scale: float = 7.5,
) -> bytes:
    """
    Generate image using Modal H100 GPU (INTERNAL FUNCTION)
    """
    print(f"[MODAL-REMOTE] Generating with {model_name}: {prompt[:100]}...")
    print(f"[MODAL-REMOTE] Running on Modal cloud GPU (NOT local GPU)")
    
    # Check if we're running on Modal infrastructure
    import torch
    if not torch.cuda.is_available():
        print("[MODAL-REMOTE] ERROR: CUDA not available on Modal infrastructure")
        raise RuntimeError("CUDA not available on Modal infrastructure")
    
    print(f"[MODAL-REMOTE] Using GPU: {torch.cuda.get_device_name(0)}")
    print(f"[MODAL-REMOTE] CUDA Version: {torch.version.cuda}")
    
    # Basic validation: most diffusion models expect dimensions divisible by 8
    if width % 8 != 0 or height % 8 != 0:
        raise ValueError("width and height must be divisible by 8")

    # Load model on Modal's GPU
    # Avoid AutoPipelineForText2Image here: it eagerly imports many optional pipelines
    # and can crash if the environment is missing niche transformer tokenizers.
    from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
    import os
    pipe = _PIPELINE_CACHE.get(model_name)
    if pipe is None:
        hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
        print(f"[MODAL-REMOTE] HF token detected: {bool(hf_token)}")
        model_name_lower = (model_name or "").lower()
        is_sdxl = ("sdxl" in model_name_lower) or ("xl" in model_name_lower)

        if is_sdxl:
            pipe = StableDiffusionXLPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                **({"token": hf_token} if hf_token else {}),
            )
        else:
            pipe = StableDiffusionPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                safety_checker=None,
                requires_safety_checker=False,
                **({"token": hf_token} if hf_token else {}),
            )
        pipe = pipe.to("cuda")
        _PIPELINE_CACHE[model_name] = pipe

    # Ensure safety checker is disabled (avoids black/blank images on some prompts)
    if hasattr(pipe, "safety_checker"):
        pipe.safety_checker = None
    if hasattr(pipe, "requires_safety_checker"):
        pipe.requires_safety_checker = False
    if hasattr(pipe, "watermark"):
        pipe.watermark = None
    
    print(f"[MODAL-REMOTE] Model loaded on Modal GPU")
    
    # Generate image on Modal's GPU
    with torch.autocast("cuda"):
        result = pipe(
            prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        )
        image = result.images[0]
    
    print(f"[MODAL-REMOTE] Generated image: {image.size}")
    
    # Convert to bytes
    import io
    from PIL import Image
    import numpy as np

    try:
        arr = np.array(image)
        print(f"[MODAL-REMOTE] Image stats: shape={arr.shape} min={arr.min()} max={arr.max()}")
    except Exception as _e:
        pass

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    print(f"[MODAL-REMOTE] Returning {len(img_bytes.getvalue())} bytes")
    return img_bytes.getvalue()

# Web endpoint for image generation
@web_app.post("/generate")
async def generate_endpoint(
    prompt: str,
    model_name: str = "runwayml/stable-diffusion-v1-5",
    width: int = 512,
    height: int = 512,
    num_inference_steps: int = 20,
    guidance_scale: float = 7.5,
):
    """Web endpoint for image generation"""
    try:
        image_bytes = await generate_image_internal.remote.aio(
            prompt,
            model_name,
            width,
            height,
            num_inference_steps,
            guidance_scale,
        )
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@web_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "visioncraft-modal"}

# Deploy web app
@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app

if __name__ == "__main__":
    print("[MODAL-WEB] Starting Modal web server...")
    print("[MODAL-WEB] This will deploy a web endpoint for VisionCraft")
    
    # Deploy web app
    try:
        app.serve()
    except KeyboardInterrupt:
        print("\n[MODAL-WEB] Stopping Modal web server...")
    except Exception as e:
        print(f"[MODAL-WEB] Error: {e}")
