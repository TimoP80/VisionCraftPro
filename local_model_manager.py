"""
Local Model Manager for VisionCraft Pro
Handles on-demand downloading of Hugging Face models and local generation (GPU/CPU).
"""

import torch
import gc
import os
import json
import time
from diffusers import (
    StableDiffusionPipeline, 
    StableDiffusionXLPipeline, 
    DiffusionPipeline,
    DPMSolverMultistepScheduler
)
from huggingface_hub import snapshot_download, model_info
from PIL import Image
from typing import Dict, Any, Optional, List
import threading

class LocalModelManager:
    """Manages local AI models with on-demand downloading and CPU/GPU support"""
    
    def __init__(self, models_dir: str = "models/local"):
        self.models_dir = models_dir
        self.models = {}
        self.current_model_id = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.download_status = {} # model_id -> status string
        
        # Ensure models directory exists
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            
        print(f"[LOCAL-MANAGER] Initialized on {self.device}")
        if self.device == "cpu":
            print("[LOCAL-MANAGER] ⚠️ Running in CPU mode. Generation will be slower.")

    def get_downloaded_models(self) -> List[Dict[str, Any]]:
        """List all models currently downloaded in the local directory"""
        downloaded = []
        if not os.path.exists(self.models_dir):
            return downloaded
            
        # Each subdirectory in models/local is expected to be a model (or part of a repo id path)
        # For simplicity, we'll look for directories that look like they contain a model
        for root, dirs, files in os.walk(self.models_dir):
            if "model_index.json" in files:
                # This is likely a diffusers model directory
                relative_path = os.path.relpath(root, self.models_dir)
                # Convert backslashes to forward slashes for repo-id style
                model_id = relative_path.replace("\\", "/")
                
                # Try to get some meta-info if available
                downloaded.append({
                    "id": model_id,
                    "path": root,
                    "name": model_id.split("/")[-1],
                    "is_local": True
                })
        return downloaded

    def download_model(self, repo_id: str, token: Optional[str] = None):
        """Download a model from Hugging Face in a background thread"""
        if repo_id in self.download_status and self.download_status[repo_id] == "downloading":
            return {"status": "already downloading", "repo_id": repo_id}

        def _download_task():
            try:
                self.download_status[repo_id] = "downloading"
                print(f"[LOCAL-MANAGER] Starting download of {repo_id}...")
                
                # snapshot_download handles the local directory structure automatically
                # but we'll put it under our models_dir
                local_path = os.path.join(self.models_dir, repo_id.replace("/", os.sep))
                
                snapshot_download(
                    repo_id=repo_id,
                    local_dir=local_path,
                    token=token,
                    ignore_patterns=["*.msgpack", "*.ckpt", "*.h5"] # Save space
                )
                
                self.download_status[repo_id] = "completed"
                print(f"[LOCAL-MANAGER] Successfully downloaded {repo_id}")
            except Exception as e:
                self.download_status[repo_id] = f"failed: {str(e)}"
                print(f"[LOCAL-MANAGER] Failed to download {repo_id}: {e}")

        thread = threading.Thread(target=_download_task)
        thread.daemon = True
        thread.start()
        
        return {"status": "started", "repo_id": repo_id}

    def get_status(self, repo_id: str) -> str:
        """Get the download status of a model"""
        return self.download_status.get(repo_id, "unknown")

    def load_model(self, model_id: str) -> bool:
        """Load a locally available model"""
        # Search for model_id in downloaded models
        local_models = self.get_downloaded_models()
        target_model = next((m for m in local_models if m["id"] == model_id), None)
        
        if not target_model:
            print(f"[LOCAL-MANAGER] ❌ Model {model_id} not found locally.")
            return False
            
        print(f"[LOCAL-MANAGER] 🔄 Loading {model_id} from {target_model['path']}...")
        
        try:
            # Unload current
            self.unload_model()
            
            # Determine pipeline type
            # We'll use DiffusionPipeline and let it auto-detect, but apply our optimizations
            load_kwargs = {
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "use_safetensors": True,
                "local_files_only": True
            }
            
            pipe = DiffusionPipeline.from_pretrained(target_model['path'], **load_kwargs)
            pipe = pipe.to(self.device)
            
            # Apply optimizations
            if self.device == "cuda":
                if hasattr(pipe, "enable_xformers_memory_efficient_attention"):
                    try:
                        pipe.enable_xformers_memory_efficient_attention()
                    except:
                        pass
                pipe.enable_attention_slicing()
                pipe.enable_model_cpu_offload() # Very good for memory
            else:
                # CPU Optimizations
                pipe.enable_attention_slicing()
                if hasattr(pipe, "enable_sequential_cpu_offload"):
                    pipe.enable_sequential_cpu_offload()
            
            self.models[model_id] = pipe
            self.current_model_id = model_id
            print(f"[LOCAL-MANAGER] ✅ Model {model_id} loaded successfully.")
            return True
        except Exception as e:
            print(f"[LOCAL-MANAGER] ❌ Error loading model: {e}")
            return False

    def unload_model(self):
        """Free up memory by unloading the current model"""
        if self.current_model_id and self.current_model_id in self.models:
            print(f"[LOCAL-MANAGER] 🗑️ Unloading {self.current_model_id}...")
            del self.models[self.current_model_id]
            self.current_model_id = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def generate(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using the currently loaded local model"""
        if not self.current_model_id:
            raise Exception("No local model loaded.")
            
        pipe = self.models[self.current_model_id]
        
        # Adjust steps for CPU if needed
        steps = kwargs.get("num_inference_steps", 20)
        if self.device == "cpu":
            steps = min(steps, 15) # Cap steps on CPU for usability
            
        print(f"[LOCAL-MANAGER] 🎨 Generating with {self.current_model_id} on {self.device}")
        
        try:
            with torch.no_grad():
                result = pipe(
                    prompt=prompt,
                    negative_prompt=kwargs.get("negative_prompt", ""),
                    num_inference_steps=steps,
                    guidance_scale=kwargs.get("guidance_scale", 7.5),
                    width=kwargs.get("width", 512),
                    height=kwargs.get("height", 512)
                )
                
            return result.images[0]
        except Exception as e:
            print(f"[LOCAL-MANAGER] ❌ Generation failed: {e}")
            raise e
