"""
Alternative launcher using Gradio for a more interactive interface
"""

import torch
import gc
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import gradio as gr
import numpy as np
import time
import psutil

class OptimizedImageGenerator:
    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        
    def load_model(self):
        """Load Stable Diffusion 1.5 with optimizations for 8GB VRAM"""
        if self.model_loaded:
            return "Model already loaded"
            
        print(f"Loading model on {self.device}...")
        
        model_id = "runwayml/stable-diffusion-v1-5"
        
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            safety_checker=None,
            requires_safety_checker=False,
            variant="fp16",
            use_safetensors=True
        )
        
        # Enable optimizations
        if hasattr(self.pipe, "enable_xformers_memory_efficient_attention"):
            try:
                self.pipe.enable_xformers_memory_efficient_attention()
                print("XFormers enabled")
            except:
                print("XFormers not available")
        
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_sequential_cpu_offload()
        self.pipe.enable_vae_slicing()
        
        self.pipe = self.pipe.to(self.device)
        self.model_loaded = True
        print("Model loaded successfully!")
        return "Model loaded successfully"
    
    def get_vram_usage(self):
        """Get current VRAM usage in GB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**3
        return 0.0
    
    def generate(self, prompt, negative_prompt, steps, guidance, width, height, seed, progress=gr.Progress()):
        """Generate image with progress tracking"""
        if not self.model_loaded:
            progress(0.1, desc="Loading model...")
            self.load_model()
        
        progress(0.2, desc="Preparing generation...")
        
        # Set seed
        if seed != -1:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
            
        # Clear cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        progress(0.3, desc="Generating image...")
        
        try:
            with torch.autocast(self.device):
                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    width=width,
                    height=height,
                    generator=generator
                )
            
            progress(0.9, desc="Finalizing...")
            
            image = result.images[0]
            
            # Clean up
            del result
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            progress(1.0, desc="Complete!")
            
            return image, f"VRAM Used: {self.get_vram_usage():.2f} GB"
            
        except Exception as e:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            return None, f"Error: {str(e)}"

# Initialize generator
generator = OptimizedImageGenerator()

def create_interface():
    """Create Gradio interface"""
    
    def get_system_info():
        vram_used = generator.get_vram_usage()
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        return f"""
        Device: {generator.device}
        VRAM Used: {vram_used:.2f} GB / {vram_total:.2f} GB
        CPU Usage: {cpu_usage:.1f}%
        Memory Usage: {memory_usage:.1f}%
        Model Status: {'Loaded' if generator.model_loaded else 'Not Loaded'}
        """
    
    with gr.Blocks(title="8GB VRAM Image Generator", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎨 8GB VRAM Image Generator")
        gr.Markdown("Generate images using Stable Diffusion optimized for 8GB VRAM GPUs")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Generation inputs
                prompt = gr.Textbox(
                    label="Prompt",
                    placeholder="A beautiful landscape with mountains and a lake...",
                    lines=3
                )
                
                negative_prompt = gr.Textbox(
                    label="Negative Prompt",
                    placeholder="blurry, low quality, distorted...",
                    lines=2
                )
                
                with gr.Row():
                    steps = gr.Slider(
                        label="Steps",
                        minimum=1,
                        maximum=50,
                        value=20,
                        step=1
                    )
                    
                    guidance = gr.Slider(
                        label="Guidance Scale",
                        minimum=1.0,
                        maximum=20.0,
                        value=7.5,
                        step=0.5
                    )
                
                with gr.Row():
                    width = gr.Dropdown(
                        label="Width",
                        choices=[512, 768],
                        value=512
                    )
                    
                    height = gr.Dropdown(
                        label="Height", 
                        choices=[512, 768],
                        value=512
                    )
                
                seed = gr.Number(
                    label="Seed (-1 for random)",
                    value=-1,
                    precision=0
                )
                
                generate_btn = gr.Button("Generate Image", variant="primary", size="lg")
                
            with gr.Column(scale=1):
                # System info
                system_info = gr.Textbox(
                    label="System Status",
                    value=get_system_info(),
                    lines=6,
                    interactive=False
                )
                
                load_model_btn = gr.Button("Load Model", variant="secondary")
        
        # Output
        with gr.Row():
            image_output = gr.Image(label="Generated Image", type="pil")
            info_output = gr.Textbox(label="Generation Info", interactive=False, lines=2)
        
        # Gallery
        gr.Markdown("## Recent Generations")
        gallery = gr.Gallery(label="Gallery", columns=3, height="auto")
        
        # Event handlers
        def generate_image(*args):
            image, info = generator.generate(*args)
            return image, info, get_system_info()
        
        generate_btn.click(
            generate_image,
            inputs=[prompt, negative_prompt, steps, guidance, width, height, seed],
            outputs=[image_output, info_output, system_info]
        )
        
        load_model_btn.click(
            generator.load_model,
            outputs=[system_info]
        )
        
        # Auto-refresh system info
        demo.load(
            get_system_info,
            outputs=[system_info],
            every=5  # Refresh every 5 seconds
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
