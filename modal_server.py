"""
Modal server for VisionCraft - keeps app running without requiring arguments
"""

import modal
import time

# Create Modal app
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
        modal.Secret.from_name("huggingface-token"),
    ]
)
def generate_image(prompt: str, model_name: str = "runwayml/stable-diffusion-v1-5") -> bytes:
    """
    Generate image using Modal H100 GPU (REMOTE EXECUTION)
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
    
    # Load model on Modal's GPU
    from diffusers import StableDiffusionPipeline
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
    import io
    from PIL import Image
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    print(f"[MODAL-REMOTE] Returning {len(img_bytes.getvalue())} bytes")
    return img_bytes.getvalue()

# Server entrypoint - doesn't require function arguments
@app.function()
def server_status() -> str:
    """Keep server alive status check"""
    return "Modal server is running and ready for VisionCraft requests"

if __name__ == "__main__":
    print("[MODAL-SERVER] Starting Modal server...")
    print("[MODAL-SERVER] This keeps Modal app running for VisionCraft")
    
    # Start server mode - this keeps app running
    try:
        app.serve()
    except KeyboardInterrupt:
        print("\n[MODAL-SERVER] Stopping Modal server...")
    except Exception as e:
        print(f"[MODAL-SERVER] Error: {e}")
