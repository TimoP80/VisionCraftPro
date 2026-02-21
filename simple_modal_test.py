"""
Simple Modal test to verify function works
"""

import modal

# Create simple Modal app
app = modal.App("test-modal")

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
    timeout=300
)
def test_generate(prompt: str) -> str:
    """Simple test function"""
    return f"Modal received: {prompt}"

if __name__ == "__main__":
    print("Starting simple Modal test...")
    result = test_generate.remote("test prompt")
    print(f"Result: {result}")
