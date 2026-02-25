"""
Modern Commercial Image Generators
Support for Nano Banana Pro, Seedream, Leonardo.ai API-based generators, and Modal
"""

import requests
import json
import base64
import io
from typing import Dict, Any, Optional, List
from PIL import Image
import json
import os
import time
import asyncio
from datetime import datetime

# Modal imports - will be imported conditionally
try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    print("Modal not installed. Install with: pip install modal")

class ModernGeneratorManager:
    """Manages modern commercial image generators"""
    
    def __init__(self):
        self.generators = {}
        self.current_generator = None
        self.api_keys = {}
        self.api_keys_file = "api_keys.json"
        self.pending_callbacks = {}
        self._leonardo_platform_models_cache = {
            "fetched_at": 0.0,
            "models": []
        }
        
        # Load API keys on initialization
        print("Initializing ModernGeneratorManager...")
        self._load_api_keys()
        print(f"Loaded {len(self.api_keys)} API key(s)")
        
        # Initialize available generators
        self.available_generators = {}
        self._setup_leonardo_ai()
        self._setup_modal()  # Move this before Leonardo to ensure Modal is added
        print(f"Initialized {len(self.available_generators)} generator(s)")
        print(f"[SETUP] Modal setup completed. Available generators: {list(self.available_generators.keys())}")

    def _fetch_leonardo_platform_models(self, force: bool = False) -> List[Dict[str, Any]]:
        """Fetch Leonardo platform models (requires API key). Cached to avoid repeated calls."""
        cache_ttl_s = 10 * 60
        now = time.time()

        if not force and (now - float(self._leonardo_platform_models_cache.get("fetched_at", 0.0)) < cache_ttl_s):
            print(f"[LEONARDO] Using cached platform models ({len(self._leonardo_platform_models_cache.get('models', []))} models)")
            return self._leonardo_platform_models_cache.get("models", [])

        api_key = self.api_keys.get("leonardo-api")
        if not api_key:
            print("[LEONARDO] No API key configured, cannot fetch platform models")
            return []

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
        }

        url = "https://cloud.leonardo.ai/api/rest/v1/platformModels"
        print(f"[LEONARDO] Fetching platform models from: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            print(f"[LEONARDO] Response status: {resp.status_code}")
            resp.raise_for_status()
            data = resp.json() or {}
            print(f"[LEONARDO] Response keys: {list(data.keys())}")

            models = data.get("platformModels") or data.get("models") or []
            if not isinstance(models, list):
                models = []
            print(f"[LEONARDO] Fetched {len(models)} platform models")

            self._leonardo_platform_models_cache = {
                "fetched_at": now,
                "models": models,
            }
            return models
        except Exception as e:
            print(f"[WARNING] Failed to fetch Leonardo platform models: {e}")
            return self._leonardo_platform_models_cache.get("models", [])

    def _merge_leonardo_platform_models_into_generator(self):
        """Merge live Leonardo platform models into available_generators['leonardo-api']['models']."""
        if "leonardo-api" not in self.available_generators:
            print("[LEONARDO] leonardo-api not in available_generators")
            return

        generator_info = self.available_generators["leonardo-api"]
        base_models = generator_info.get("models", {})
        if not isinstance(base_models, dict):
            base_models = {}

        platform_models = self._fetch_leonardo_platform_models(force=False)
        merged = dict(base_models)

        print(f"[LEONARDO] Merging {len(platform_models)} platform models into {len(base_models)} base models")
        for m in platform_models:
            model_id = m.get("id")
            name = m.get("name")
            if not model_id:
                continue

            merged[str(model_id)] = {
                "id": str(model_id),
                "name": name or str(model_id),
                "description": m.get("description") or "",
                "max_resolution": generator_info.get("max_resolution", (1024, 1024)),
                "aspect_ratios": [ar.get("id") for ar in generator_info.get("aspect_ratios", []) if isinstance(ar, dict) and ar.get("id")],
                "note": "Platform model (fetched from Leonardo API)",
            }

        generator_info["models"] = merged
        print(f"[LEONARDO] After merge: {len(merged)} total models")

    def _leonardo_model_config(self, model_key: str) -> dict:
        """Return Leonardo model config: api_version, endpoint, modelId, and payload shape."""
        # Explicit mappings from Leonardo docs
        # These map both UUIDs and human-readable internal keys to their config
        mapping = {
            # Leonardo Phoenix (V1)
            "phoenix-1-0": {"name": "Phoenix 1.0", "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", "api_version": "v1", "endpoint": "generations"},
            "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3": {"name": "Phoenix 1.0", "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", "api_version": "v1", "endpoint": "generations"},
            
            # Leonardo Legacy / Phoenix 0.9 (V1)
            "phoenix-0-9": {"name": "Phoenix 0.9", "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042", "api_version": "v1", "endpoint": "generations"},
            "6b645e3a-d64f-4341-a6d8-7a3690fbf042": {"name": "Phoenix 0.9", "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042", "api_version": "v1", "endpoint": "generations"},
            
            # Universal / Vision XL (V1)
            "universal": {"name": "Universal Enhanced", "id": "6bef9f1b-713b-4271-9231-ef9090632332", "api_version": "v1", "endpoint": "generations"},
            "6bef9f1b-713b-4271-9231-ef9090632332": {"name": "Universal Enhanced", "id": "6bef9f1b-713b-4271-9231-ef9090632332", "api_version": "v1", "endpoint": "generations"},

            # FLUX models (V1)
            "b2614463-296c-462a-9586-aafdb8f00e36": {"name": "FLUX Dev", "id": "b2614463-296c-462a-9586-aafdb8f00e36", "api_version": "v1", "endpoint": "generations"},
            "1dd50843-d653-4516-a8e3-f0238ee453ff": {"name": "FLUX Schnell", "id": "1dd50843-d653-4516-a8e3-f0238ee453ff", "api_version": "v1", "endpoint": "generations"},
            "28aeddf8-bd19-4803-80fc-79602d1a9989": {"name": "FLUX.1 Kontext [pro]", "id": "28aeddf8-bd19-4803-80fc-79602d1a9989", "api_version": "v1", "endpoint": "generations"},
            
            # V2 models (Nano Banana Pro, FLUX.2 Pro, etc.)
            "gemini-image-2": {"name": "Nano Banana Pro", "id": "gemini-image-2", "api_version": "v2", "endpoint": "generations"},
            "flux-pro-2.0": {"name": "FLUX.2 Pro", "id": "flux-pro-2.0", "api_version": "v2", "endpoint": "generations"},
        }

        # Fallback: try to infer by modelId pattern
        if model_key in mapping:
            return mapping[model_key]
        
        # If we don't have an explicit mapping, assume V1 for legacy compatibility but log it
        print(f"[WARNING] No explicit mapping for Leonardo model: {model_key}, using fallback")
        return {"name": model_key, "id": model_key, "api_version": "v1", "endpoint": "generations"}

    def _build_leonardo_payload_v1(self, model_key: str, model_config: dict, prompt: str, **kwargs) -> dict:
        """Build Leonardo V1 payload (modelId, styleUUID, enhancePrompt, etc.)."""
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        payload = {
            "prompt": prompt,
            "modelId": model_config.get("id", model_key),
            "width": width,
            "height": height,
            "num_images": 1,
            "contrast": kwargs.get("contrast", 3.5),
            "enhancePrompt": kwargs.get("enhancePrompt", False),
        }

        # Add optional parameters if provided
        if "preset_style" in kwargs:
            # Map preset style names to styleUUIDs (use a common Leonardo UUID for now)
            style_uuid_map = {
                "LEONARDO": "111dc692-d470-4eec-b791-3475abac4c46",
                "CREATIVE": "3cbb655a-7ca4-463f-b697-8a03ad67327c",
                "DYNAMIC": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
                "CINEMATIC": "594c1a08-a522-4e0e-b7ff-e4dac4b6b622",
                "FANTASY_ART": "09d2b5b5-d7c02-905d-9f84051640f4",
                "ANIME": "7d7c2bc5-4b12-4ac3-81a9-630057e9e89f",
                "COMIC_BOOK": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
                "ILLUSTRATION": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
            }
            style_uuid = style_uuid_map.get(kwargs["preset_style"], "111dc692-d470-4eec-b791-3475abac4c46")
            payload["styleUUID"] = style_uuid

        # Add negative prompt if provided
        if kwargs.get("negative_prompt"):
            payload["negative_prompt"] = kwargs["negative_prompt"]

        # Add guidance scale if provided (V1 uses guidance_scale)
        if "guidance_scale" in kwargs:
            payload["guidance_scale"] = kwargs["guidance_scale"]

        # Add num_inference_steps if provided
        if "num_inference_steps" in kwargs:
            payload["num_inference_steps"] = kwargs["num_inference_steps"]

        # Add seed if provided (must be a valid integer, not None)
        if "seed" in kwargs and kwargs["seed"] is not None and kwargs["seed"] >= 0:
            payload["seed"] = kwargs["seed"]

        return payload

    def _build_leonardo_payload_v2(self, model_key: str, model_config: dict, prompt: str, **kwargs) -> dict:
        """Build Leonardo V2 payload (model, parameters wrapper, prompt_enhance, style_ids)."""
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        parameters = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "quantity": 1,
            "prompt_enhance": "OFF",  # Default to OFF for V2 models
        }

        # Add style_ids if preset_style is provided
        if "preset_style" in kwargs:
            # Map preset style names to style_ids (use common Leonardo style UUIDs)
            style_id_map = {
                "LEONARDO": ["111dc692-d470-4eec-b791-3475abac4c46"],
                "CREATIVE": ["3cbb655a-7ca4-463f-b697-8a03ad67327c"],
                "DYNAMIC": ["6fedbf1f-4a17-45ec-84fb-92fe524a29ef"],
                "CINEMATIC": ["594c1a08-a522-4e0e-b7ff-e4dac4b6b622"],
                "FANTASY_ART": ["09d2b5b5-d7c02-905d-9f84051640f4"],
                "ANIME": ["7d7c2bc5-4b12-4ac3-81a9-630057e9e89f"],
                "COMIC_BOOK": ["645e4195-f63d-4715-a3f2-3fb1e6eb8c70"],
                "ILLUSTRATION": ["556c1ee5-ec38-42e8-955a-1e82dad0ffa1"],
            }
            style_ids = style_id_map.get(kwargs["preset_style"], ["111dc692-d470-4eec-b791-3475abac4c46"])
            parameters["style_ids"] = style_ids

        # Add negative prompt if provided
        if kwargs.get("negative_prompt"):
            parameters["negative_prompt"] = kwargs["negative_prompt"]

        # Add guidance scale if provided (V2 uses guidance_scale in parameters)
        if "guidance_scale" in kwargs:
            parameters["guidance_scale"] = kwargs["guidance_scale"]

        # Add num_inference_steps if provided (V2 uses steps)
        if "num_inference_steps" in kwargs:
            parameters["steps"] = kwargs["num_inference_steps"]

        # Add seed if provided (must be a valid integer, not None)
        if "seed" in kwargs and kwargs["seed"] is not None and kwargs["seed"] >= 0:
            parameters["seed"] = kwargs["seed"]

        payload = {
            "model": model_config.get("id", model_key),
            "parameters": parameters,
            "public": False,
        }

        return payload
    
    def _setup_leonardo_ai(self):
        """Setup Leonardo.ai generator configuration"""
        self.available_generators["leonardo-api"] = {
            "name": "Leonardo.ai API",
            "type": "api",
            "description": "Professional game asset generator with model selection",
            "api_endpoint": "https://cloud.leonardo.ai/api/rest/v1/generations",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Fast",
            "cost": "Paid",
            "features": ["text-to-image", "fine-tuned-models", "texture-generation"],
            "models": {
                "phoenix-1-0": {
                    "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",
                    "name": "Leonardo Phoenix Enhanced",
                    "description": "Optimized SD 1.5 with LEONARDO preset (best available with current plan)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Requires higher-tier subscription for true Phoenix models"
                },
                "phoenix-0-9": {
                    "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",
                    "name": "Leonardo Legacy Enhanced",
                    "description": "Enhanced SD 1.5 with optimizations",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Legacy model with enhanced prompt engineering"
                },
                "universal": {
                    "id": "6bef9f1b-713b-4271-9231-ef9090632332",
                    "name": "Universal Enhanced",
                    "description": "Universal model with advanced prompt optimization",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Optimized for all content types"
                }
            },
            "preset_styles": [
                {"id": "CREATIVE", "name": "Creative", "description": "Balanced creative output"},
                {"id": "DYNAMIC", "name": "Dynamic", "description": "More dynamic and dramatic"},
                {"id": "CINEMATIC", "name": "Cinematic", "description": "Movie-like quality"},
                {"id": "FANTASY_ART", "name": "Fantasy Art", "description": "Fantasy themed"},
                {"id": "ANIME", "name": "Anime", "description": "Anime style"},
                {"id": "COMIC_BOOK", "name": "Comic Book", "description": "Comic book style"}
            ],
            "quality_levels": [
                {"id": "standard", "name": "Standard", "description": "Good quality, faster generation"},
                {"id": "high", "name": "High", "description": "Better quality, moderate time"},
                {"id": "ultra", "name": "Ultra", "description": "Best quality, longer time"}
            ],
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": (1024, 1024)},
                {"id": "16:9", "name": "Widescreen", "resolution": (1344, 768)},
                {"id": "9:16", "name": "Portrait", "resolution": (768, 1344)},
                {"id": "4:3", "name": "Standard", "resolution": (1024, 768)},
                {"id": "3:4", "name": "Vertical", "resolution": (768, 1024)},
                {"id": "2:3", "name": "Tall", "resolution": (832, 1216)},
                {"id": "3:2", "name": "Wide", "resolution": (1216, 832)}
            ]
        }
    
    def _setup_modal(self):
        """Setup Modal generator configuration"""
        print(f"[SETUP] Setting up Modal generator...")
        print(f"[SETUP] MODAL_AVAILABLE: {MODAL_AVAILABLE}")
        
        if not MODAL_AVAILABLE:
            print("[SETUP] Modal not available - skipping setup")
            return
            
        print("[SETUP] Adding Modal to available generators...")
        self.available_generators["modal"] = {
            "name": "Modal (gpu selectable)",
            "type": "modal",
            "description": "Remote H100 GPU generation via Modal platform",
            "api_endpoint": "modal://remote",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Very Fast",
            "cost": "Pay-per-use",
            "features": ["text-to-image", "h100-gpu", "fast-generation", "scalable"],
            "models": {
                "runwayml/stable-diffusion-v1-5": {
                    "name": "Stable Diffusion v1.5",
                    "description": "Classic Stable Diffusion model",
                    "max_resolution": (768, 768),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Fast generation on H100"
                },
                "stabilityai/stable-diffusion-xl-base-1.0": {
                    "name": "Stable Diffusion XL",
                    "description": "High-quality SDXL model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Higher quality, longer generation"
                },
                "stabilityai/sdxl-turbo": {
                    "name": "SDXL Turbo",
                    "description": "Ultra-fast SDXL variant",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Very fast, fewer steps recommended"
                },
                "stabilityai/stable-diffusion-2-1-base": {
                    "name": "Stable Diffusion v2.1",
                    "description": "Stable Diffusion 2.1 (base checkpoint)",
                    "max_resolution": (768, 768),
                    "aspect_ratios": ["1:1", "9:16", "16:9"],
                    "note": "Good general-purpose model"
                },
                "black-forest-labs/FLUX.1-schnell": {
                    "name": "FLUX.1 Schnell",
                    "description": "Fast FLUX model (non-SD pipeline)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Uses FluxPipeline on Modal"
                },
                "stabilityai/stable-diffusion-3.5-large": {
                    "name": "Stable Diffusion 3.5 Large",
                    "description": "SD3.5 (StableDiffusion3Pipeline)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Uses StableDiffusion3Pipeline on Modal"
                }
            },
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": (768, 768)},
                {"id": "16:9", "name": "Widescreen", "resolution": (1024, 576)},
                {"id": "9:16", "name": "Portrait", "resolution": (576, 1024)},
                {"id": "4:3", "name": "Standard", "resolution": (896, 672)},
                {"id": "3:4", "name": "Vertical", "resolution": (672, 896)}
            ],
            "quality_levels": [
                {"id": "standard", "name": "Standard", "description": "20 steps, good quality"},
                {"id": "high", "name": "High", "description": "30 steps, better quality"},
                {"id": "ultra", "name": "Ultra", "description": "50 steps, best quality"}
            ]
        }

        # Restore additional modern generators that were supported before Modal integration
        # (they require API keys to actually run).
        self.available_generators.setdefault("nano-banana-pro", {
            "name": "Nano Banana Pro",
            "type": "api",
            "description": "Fast commercial generator (requires API key)",
            "api_endpoint": "",
            "max_resolution": (1024, 1024),
            "quality": "High",
            "speed": "Very Fast",
            "cost": "Paid",
            "features": ["text-to-image"],
        })

        self.available_generators.setdefault("seedream", {
            "name": "Seedream",
            "type": "api",
            "description": "Professional generator with style control (requires API key)",
            "api_endpoint": "",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Fast",
            "cost": "Paid",
            "features": ["text-to-image"],
        })
    
    def set_api_key(self, generator_name: str, api_key: str):
        """Set API key for a generator and persist to file"""
        self.api_keys[generator_name] = api_key
        if generator_name == "leonardo-api":
            self._leonardo_platform_models_cache = {
                "fetched_at": 0.0,
                "models": []
            }
        self._save_api_keys()
        print(f"[OK] API key set for {generator_name}")

        if generator_name == "leonardo-api":
            self._merge_leonardo_platform_models_into_generator()
    
    def _load_api_keys(self):
        """Load API keys from file"""
        try:
            if os.path.exists(self.api_keys_file):
                with open(self.api_keys_file, 'r') as f:
                    loaded_keys = json.load(f)
                    # Validate API keys to ensure they're not corrupted
                    for key, value in loaded_keys.items():
                        if isinstance(value, str) and len(value) > 1000:
                            print(f"[WARNING] API key for {key} appears corrupted (too long), skipping")
                            continue
                        if not isinstance(value, str) or len(value) < 10:
                            print(f"[WARNING] API key for {key} appears invalid, skipping")
                            continue
                        self.api_keys[key] = value
                    print(f"[OK] Loaded {len(self.api_keys)} valid API key(s)")
        except Exception as e:
            print(f"[WARNING] Could not load API keys: {e}")
            self.api_keys = {}
    
    def _save_api_keys(self):
        """Save API keys to file"""
        try:
            with open(self.api_keys_file, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
            print(f"[SAVE] Saved API keys to {self.api_keys_file}")
        except Exception as e:
            print(f"[ERROR] Could not save API keys: {e}")
    
    def get_available_generators(self) -> Dict[str, Dict]:
        """Get all available modern generators"""
        # Keep Leonardo model list fresh if API key is configured.
        if "leonardo-api" in self.api_keys:
            print("[LEONARDO] API key present, attempting to merge platform models")
            self._merge_leonardo_platform_models_into_generator()
        return self.available_generators
    
    def get_generator_info(self, generator_name: str) -> Optional[Dict]:
        """Get information about a specific generator"""
        return self.available_generators.get(generator_name)
    
    async def generate_with_nano_banana_pro(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Nano Banana Pro API"""
        if "nano-banana-pro" not in self.api_keys:
            raise ValueError("API key required for Nano Banana Pro")

        endpoint = (self.available_generators.get("nano-banana-pro") or {}).get("api_endpoint")
        if not endpoint or not isinstance(endpoint, str) or not endpoint.startswith("http"):
            raise ValueError(
                "Nano Banana Pro api_endpoint is not configured. "
                "Set a valid URL in modern_generators.py available_generators['nano-banana-pro']['api_endpoint']."
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['nano-banana-pro']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
            "steps": kwargs.get("num_inference_steps", 20),
            "guidance_scale": kwargs.get("guidance_scale", 7.5),
            "style": kwargs.get("style", "realistic"),
            "quality": kwargs.get("quality", "high")
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            image_data = base64.b64decode(result["image"])
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            print(f"[ERROR] Nano Banana Pro generation failed: {e}")
            raise
    
    async def generate_with_seedream(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Seedream API"""
        if "seedream" not in self.api_keys:
            raise ValueError("API key required for Seedream")

        endpoint = (self.available_generators.get("seedream") or {}).get("api_endpoint")
        if not endpoint or not isinstance(endpoint, str) or not endpoint.startswith("http"):
            raise ValueError(
                "Seedream api_endpoint is not configured. "
                "Set a valid URL in modern_generators.py available_generators['seedream']['api_endpoint']."
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['seedream']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
            "style_preset": kwargs.get("style_preset", "photorealistic"),
            "quality": kwargs.get("quality", "ultra"),
            "negative_prompt": kwargs.get("negative_prompt", "")
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            
            result = response.json()
            image_data = base64.b64decode(result["image"])
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            print(f"[ERROR] Seedream generation failed: {e}")
            raise
    
    async def generate_with_modal(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Modal (gpu selectable) via web endpoint"""
        # Get model name from kwargs
        model_name = kwargs.get("model", "runwayml/stable-diffusion-v1-5")

        width = int(kwargs.get("width", 512) or 512)
        height = int(kwargs.get("height", 512) or 512)
        num_inference_steps = int(kwargs.get("num_inference_steps", 20) or 20)
        guidance_scale = float(kwargs.get("guidance_scale", 7.5) or 7.5)

        # Prefer env var so you can paste the URL that `modal serve modal_web.py` prints.
        # Example: https://timop80--visioncraft-modal-fastapi-app-dev.modal.run
        base_url = os.environ.get(
            "VISIONCRAFT_MODAL_ENDPOINT",
            "https://timop80--visioncraft-modal-fastapi-app-dev.modal.run",
        ).rstrip("/")
        url = f"{base_url}/generate"

        try:
            import httpx
            import io
            from PIL import Image

            print(f"[MODAL] Calling Modal web endpoint...")
            print(f"[MODAL] Endpoint: {url}")
            print(f"[MODAL] Model: {model_name}")
            print(f"[MODAL] Prompt: {prompt[:100]}...")

            request_params = {
                "prompt": prompt,
                "model_name": model_name,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
            }

            async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
                response = await client.post(url, params=request_params)

            if getattr(response, "history", None):
                for r in response.history:
                    loc = r.headers.get("location")
                    print(f"[MODAL] Redirect {r.status_code} {r.url} -> {loc}")

            if response.status_code == 200:
                print(f"[MODAL] Received {len(response.content)} bytes from Modal")
                image = Image.open(io.BytesIO(response.content))
                print(f"[MODAL] Image loaded: {image.size}")
                return image

            # Non-200
            print(f"[MODAL] Error: HTTP {response.status_code}")
            print(f"[MODAL] Response: {response.text}")
            raise ValueError(f"Modal web endpoint error: {response.status_code} {response.text}")

        except Exception as e:
            print(f"[ERROR] Modal generation failed: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise
    
    async def generate_with_dall_e_3(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using DALL-E 3 API"""
        if "dall-e-3" not in self.api_keys:
            raise ValueError("API key required for DALL-E 3")
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['dall-e-3']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": f"{kwargs.get('width', 1024)}x{kwargs.get('height', 1024)}",
            "quality": kwargs.get("quality", "standard"),
            "n": 1
        }
        
        try:
            response = requests.post(
                self.available_generators["dall-e-3"]["api_endpoint"],
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            image_url = result["data"][0]["url"]
            
            # Download the image
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            image = Image.open(io.BytesIO(image_response.content))
            return image
            
        except Exception as e:
            print(f"[ERROR] DALL-E 3 generation failed: {e}")
            raise
    
    def _enhance_prompt_for_leonardo(self, prompt: str) -> str:
        """Enhance prompt for maximum quality with SD 1.5"""
        
        # Base quality terms that work well with SD 1.5
        quality_base = [
            "high quality", "highly detailed", "sharp focus", "well-defined",
            "professional", "masterpiece", "best quality", "8k resolution"
        ]
        
        # Style-specific enhancements
        style_enhancements = {
            "photorealistic": [
                "photorealistic", "realistic", "lifelike", "professional photography",
                "DSLR", "shot on Sony A7R IV", "85mm lens", "f/1.4", "sharp details",
                "natural lighting", "studio lighting", "cinematic lighting"
            ],
            "portrait": [
                "photorealistic portrait", "detailed face", "realistic skin texture",
                "professional photography", "studio lighting", "soft lighting",
                "sharp eyes", "detailed hair", "natural expression", "high resolution"
            ],
            "cinematic": [
                "cinematic shot", "film still", "movie quality", "epic composition",
                "dramatic lighting", "cinematic color grading", "film grain",
                "anamorphic lens", "widescreen", "professional cinematography"
            ],
            "artistic": [
                "digital art", "concept art", "detailed illustration", "trending on artstation",
                "masterpiece", "award-winning", "highly detailed", "professional art",
                "sharp details", "vibrant colors", "perfect composition"
            ],
            "anime": [
                "high quality anime", "detailed anime art", "masterpiece", "best quality",
                "trending on pixiv", "sharp details", "vibrant colors", "professional anime art",
                "clean lines", "detailed background", "perfect anatomy"
            ]
        }
        
        # Determine content type and apply appropriate enhancements
        prompt_lower = prompt.lower()
        
        # Detect content type
        if "portrait" in prompt_lower or "woman" in prompt_lower or "man" in prompt_lower or "person" in prompt_lower:
            content_type = "portrait"
        elif "cinematic" in prompt_lower or "movie" in prompt_lower or "film" in prompt_lower:
            content_type = "cinematic"
        elif "anime" in prompt_lower or "manga" in prompt_lower:
            content_type = "anime"
        elif "art" in prompt_lower or "painting" in prompt_lower or "illustration" in prompt_lower:
            content_type = "artistic"
        else:
            content_type = "photorealistic"
        
        # Build enhanced prompt
        enhanced_parts = [prompt]
        
        # Add style-specific enhancements
        if content_type in style_enhancements:
            enhanced_parts.extend(style_enhancements[content_type])
        
        # Add base quality terms
        enhanced_parts.extend(quality_base)
        
        # Add technical photography terms for realism
        if content_type in ["photorealistic", "portrait", "cinematic"]:
            enhanced_parts.extend([
                "RAW photo", "no compression", "uncompressed", "high resolution",
                "professional grade", "commercial photography"
            ])
        
        return ", ".join(enhanced_parts)
    
    def _get_optimized_negative_prompt(self, original_negative: str = "") -> str:
        """Create comprehensive negative prompt for SD 1.5"""
        base_negative = (
            "blurry, low quality, worst quality, low resolution, pixelated, "
            "jpeg artifacts, compression artifacts, noisy, grainy, distorted, "
            "deformed, disfigured, bad anatomy, bad proportions, extra limbs, "
            "missing limbs, fused fingers, too many fingers, watermark, signature, "
            "text, username, error, mutated, mutation, ugly, disgusting"
        )
        
        if original_negative:
            return f"{original_negative}, {base_negative}"
        return base_negative
    
    async def generate_with_leonardo(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Leonardo.ai API"""
        print(f"[ART] Leonardo.ai generation with {prompt[:100]}...")

        endpoint = (self.available_generators.get("leonardo-api") or {}).get("api_endpoint")
        if not endpoint or not isinstance(endpoint, str) or not endpoint.startswith("http"):
            raise ValueError(
                f"Leonardo api_endpoint is misconfigured: {endpoint!r}. "
                "Expected a full https URL."
            )
        
        # Check API key
        if 'leonardo-api' not in self.api_keys:
            raise ValueError("Leonardo.ai API key not set. Please set your API key first.")
        
        api_key = self.api_keys['leonardo-api']
        
        # Validate API key format
        if not isinstance(api_key, str) or len(api_key) > 1000 or len(api_key) < 10:
            raise ValueError("Leonardo.ai API key appears to be corrupted or invalid. Please check your API key configuration.")
        
        # Check if API key contains unexpected characters (like NSIS output)
        if 'MakeNSIS' in api_key or 'Copyright' in api_key or '\r\n' in api_key:
            raise ValueError("Leonardo.ai API key appears to be corrupted with system output. Please reset your API key.")
        
        print(f"API key found: {'*' * 10}{api_key[-4:]}")
        
        # Enhance prompt for better quality
        enhanced_prompt = prompt
        print(f"[PROMPT] Enhanced: {enhanced_prompt[:100]}...")
        
        # ... rest of the function continues ...
        
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        
        print(f"[SEARCH] Headers prepared: {list(headers.keys())}")
        
        # Generate a unique callback ID for this generation
        callback_id = f"leonardo_{int(time.time())}_{hash(prompt) % 10000}"
        print(f"[SEARCH] Generated callback ID: {callback_id}")
        
        # Get parameters with defaults
        model_key = kwargs.get("model", "phoenix-1-0")
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        
        print(f"[SEARCH] Model key: {model_key}")
        print(f"[SEARCH] Aspect ratio: {aspect_ratio}")
        
        # Get model info
        generator_info = self.available_generators["leonardo-api"]
        models = generator_info["models"]
        
        print(f"[SEARCH] Available models: {list(models.keys())}")
        
        if model_key not in models:
            # Allow passing a raw Leonardo platform modelId directly (UI may send the platform id)
            model_info = {
                "id": model_key,
                "name": model_key,
                "description": "Platform model id",
                "max_resolution": generator_info.get("max_resolution", (1024, 1024)),
                "aspect_ratios": [ar.get("id") for ar in generator_info.get("aspect_ratios", []) if isinstance(ar, dict) and ar.get("id")],
                "note": "Using raw modelId",
            }
            print(f"[SEARCH] Using raw Leonardo modelId: {model_key}")
        else:
            model_info = models[model_key]
            print(f"[SEARCH] Selected model: {model_info['name']} (ID: {model_info['id']})")
        
        # Get resolution from aspect ratio
        aspect_ratios = {ar["id"]: ar for ar in generator_info["aspect_ratios"]}
        if aspect_ratio not in aspect_ratios:
            aspect_ratio = "1:1"  # Default fallback
        
        resolution = aspect_ratios[aspect_ratio]["resolution"]
        width, height = resolution
        print(f"[SEARCH] Resolution: {width}x{height}")

        # Determine model config (api version, endpoint, etc.)
        model_config = self._leonardo_model_config(model_key)
        api_version = model_config["api_version"]
        endpoint_path = model_config["endpoint"]
        full_endpoint = f"https://cloud.leonardo.ai/api/rest/{api_version}/{endpoint_path}"

        print(f"[LEONARDO] Model: {model_config['name']} ({model_key})")
        print(f"[LEONARDO] API version: {api_version}")
        print(f"[LEONARDO] Endpoint: {full_endpoint}")

        # Build payload based on API version
        if api_version == "v2":
            generation_payload = self._build_leonardo_payload_v2(model_key, model_config, prompt, **kwargs)
        else:
            generation_payload = self._build_leonardo_payload_v1(model_key, model_config, prompt, **kwargs)

        print(f"[LEONARDO] Payload: {json.dumps(generation_payload, indent=2)}")

        # Update headers for V2 if needed
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }

        print(f"[LEONARDO] Sending to: {full_endpoint}")
        print(f"[LEONARDO] Headers: {list(headers.keys())}")
        print(f"[LEONARDO] Payload: {json.dumps(generation_payload, indent=2)}")

        try:
            print(f"[SEND] Sending POST request...")
            # Start generation
            response = requests.post(
                full_endpoint,
                headers=headers,
                json=generation_payload,
                timeout=30
            )
            
            if response.status_code >= 500:
                print(f"[CRITICAL] Leonardo.ai server error (500). Usually this means an invalid model ID or payload parameter.")
                print(f"[CRITICAL] Endpoint: {full_endpoint}")
                print(f"[CRITICAL] Payload sent: {json.dumps(generation_payload)}")
                
            response.raise_for_status()
            
            data = response.json()
            print(f"[SEND] Response data: {json.dumps(data, indent=2)}")
            
            # Extract generation ID from the response
            if "sdGenerationJob" in data and "generationId" in data["sdGenerationJob"]:
                generation_id = data["sdGenerationJob"]["generationId"]
            elif "generations_by_pk" in data and "id" in data["generations_by_pk"]:
                generation_id = data["generations_by_pk"]["id"]
            else:
                print(f"� Full response structure: {json.dumps(data, indent=2)}")
                raise ValueError("Could not extract generation ID from response")
            
            print(f"[OK] Leonardo.ai generation started: {generation_id}")
            
            # Poll for completion
            return await self._poll_leonardo_generation(generation_id, headers)
            
        except Exception as e:
            print(f"[ERROR] Leonardo.ai generation failed: {e}")
            print(f"[SEARCH] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            # Check if it was a timeout - the generation might have actually completed
            if "timeout" in str(e).lower():
                print(f"[SEARCH] Checking if generation completed despite timeout...")
                try:
                    # Final check for completion
                    status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
                    final_response = requests.get(status_url, headers=headers, timeout=10)
                    final_response.raise_for_status()
                    final_data = final_response.json()
                    
                    if final_data.get("status") == "COMPLETE":
                        print(f"[OK] Generation completed despite timeout! Retrieving image...")
                        if "generated_images" in final_data and len(final_data["generated_images"]) > 0:
                            image_url = final_data["generated_images"][0]["url"]
                            image_response = requests.get(image_url, timeout=30)
                            image_response.raise_for_status()
                            image = Image.open(io.BytesIO(image_response.content))
                            print(f"[OK] Leonardo.ai image retrieved successfully!")
                            return image
                except Exception as final_check_error:
                    print(f"[SEARCH] Final check failed: {final_check_error}")
            
            raise
    
    async def _wait_for_leonardo_callback(self, generation_id: str, callback_id: str, headers: dict) -> Image.Image:
        """Wait for Leonardo.ai callback or fall back to polling"""
        print(f"[WAIT] Waiting for Leonardo.ai callback: {callback_id}")
        
        # Store callback info for the webhook handler
        if not hasattr(self, 'pending_callbacks'):
            self.pending_callbacks = {}
        
        # Create an event to wait for the callback
        callback_event = asyncio.Event()
        self.pending_callbacks[callback_id] = {
            "event": callback_event,
            "generation_id": generation_id,
            "headers": headers
        }
        
        # Wait for callback (timeout after 3 minutes)
        try:
            await asyncio.wait_for(callback_event.wait(), timeout=180)
            
            # Get the result from the callback handler
            if callback_id in self.pending_callbacks and "result" in self.pending_callbacks[callback_id]:
                result = self.pending_callbacks[callback_id]["result"]
                del self.pending_callbacks[callback_id]
                
                if result["success"]:
                    # Download the image
                    image_response = requests.get(result["image_url"], timeout=30)
                    image_response.raise_for_status()
                    
                    image = Image.open(io.BytesIO(image_response.content))
                    print(f"[OK] Leonardo.ai generation completed via callback")
                    return image
                else:
                    raise Exception(f"Leonardo.ai callback error: {result['error']}")
            else:
                raise TimeoutError("Callback received but no result found")
                
        except asyncio.TimeoutError:
            print(f"[TIME] Leonardo.ai callback timeout, falling back to polling")
            del self.pending_callbacks[callback_id]
            return await self._poll_leonardo_generation(generation_id, headers)
    
    async def _poll_leonardo_generation(self, generation_id: str, headers: dict) -> Image.Image:
        """Official Leonardo.ai API polling method following their documentation"""
        print(f"[RELOAD] Polling Leonardo.ai generation: {generation_id}")
        
        # Use the correct endpoint for getting generation status
        status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        
        for attempt in range(180):  # Poll for up to 6 minutes (180 * 2 seconds)
            try:
                status_response = requests.get(status_url, headers=headers, timeout=10)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                
                # Leonardo.ai nests the generation data under "generations_by_pk"
                generation_data = status_data.get("generations_by_pk", {})
                current_status = generation_data.get("status")
                
                print(f"[RELOAD] Poll attempt {attempt + 1}/180 - Status: {current_status}")
                
                # Check if generation is complete
                if current_status == "COMPLETE":
                    print(f"[OK] Generation complete! Retrieving image...")
                    
                    # Get the image URL from the nested structure
                    generated_images = generation_data.get("generated_images", [])
                    if len(generated_images) > 0:
                        image_url = generated_images[0]["url"]
                        
                        # Download the image
                        image_response = requests.get(image_url, timeout=30)
                        image_response.raise_for_status()
                        
                        image = Image.open(io.BytesIO(image_response.content))
                        print(f"[OK] Leonardo.ai generation completed via polling")
                        return image
                    else:
                        raise Exception("Generation marked as COMPLETE but no images found")
                
                # Check for failed status
                elif current_status == "FAILED":
                    error_message = generation_data.get("errorMessage", "Unknown error")
                    raise Exception(f"Leonardo.ai generation failed: {error_message}")
                
                # Continue polling for other statuses (PENDING, RUNNING, etc.)
                else:
                    # Implement delay as per best practices (2-3 seconds between requests)
                    await asyncio.sleep(3)  # Using 3 seconds as recommended
                    
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Polling request failed: {e}")
                await asyncio.sleep(3)  # Wait before retry
        
        raise TimeoutError("Generation timed out after 6 minutes")
    
    def handle_leonardo_callback(self, callback_id: str, webhook_data: dict):
        """Handle Leonardo.ai webhook callback"""
        print(f"[CALLBACK] Received Leonardo.ai callback: {callback_id}")
        
        if hasattr(self, 'pending_callbacks') and callback_id in self.pending_callbacks:
            callback_info = self.pending_callbacks[callback_id]
            
            try:
                # Parse the webhook data
                if webhook_data.get("status") == "COMPLETE":
                    callback_info["result"] = {
                        "success": True,
                        "image_url": webhook_data["url"],
                        "generation_id": webhook_data.get("generationId")
                    }
                else:
                    callback_info["result"] = {
                        "success": False,
                        "error": webhook_data.get("error", "Unknown error")
                    }
                
                # Signal that callback was received
                callback_info["event"].set()
                print(f"[OK] Leonardo.ai callback processed: {callback_id}")
                
            except Exception as e:
                print(f"[ERROR] Error processing Leonardo.ai callback: {e}")
                callback_info["result"] = {
                    "success": False,
                    "error": str(e)
                }
                callback_info["event"].set()
        else:
            print(f"[WARNING] Unknown callback ID: {callback_id}")
    
    def get_webhook_endpoints(self) -> Dict[str, str]:
        """Get webhook endpoints for supported generators"""
        return {
            "leonardo-api": "/webhook/leonardo/{callback_id}",
            "nano-banana-pro": "/webhook/nano-banana/{callback_id}",  # Future support
            "seedream": "/webhook/seedream/{callback_id}"  # Future support
        }
    
    async def generate_image(self, generator_name: str, prompt: str, **kwargs) -> Image.Image:
        """Generate image using specified modern generator"""
        print(f"[ART] Starting generation with {generator_name}")
        print(f"[NOTE] Prompt: {prompt[:100]}...")
        print(f"[SEARCH] Available generators: {list(self.available_generators.keys())}")
        
        if generator_name not in self.available_generators:
            raise ValueError(f"Generator {generator_name} not available")
        
        generator_info = self.available_generators[generator_name]
        print(f"[SEARCH] Generator info: {generator_info}")
        
        try:
            if generator_name == "leonardo-api":
                return await self.generate_with_leonardo(prompt, **kwargs)
            elif generator_name == "nano-banana-pro":
                return await self.generate_with_nano_banana_pro(prompt, **kwargs)
            elif generator_name == "seedream":
                return await self.generate_with_seedream(prompt, **kwargs)
            elif generator_name == "modal":
                return await self.generate_with_modal(prompt, **kwargs)
            elif generator_name == "midjourney-api":
                return await self.generate_with_midjourney(prompt, **kwargs)
            elif generator_name == "dall-e-3":
                return await self.generate_with_dalle3(prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported generator: {generator_name}")
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            print(f"[SEARCH] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _generate_demo_image(self, generator_name: str, prompt: str, **kwargs) -> Image.Image:
        """Generate a demo image for testing without API keys"""
        print(f"[ART] Demo mode: Generating with {self.available_generators[generator_name]['name']}")
        
        # Create a simple demo image with text
        width = kwargs.get("width", 512)
        height = kwargs.get("height", 512)
        
        # Create a gradient background
        image = Image.new('RGB', (width, height), color=(100, 150, 200))
        
        # Add some visual interest with a simple pattern
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(image)
        
        # Create a gradient effect
        for y in range(height):
            color_value = int(100 + (155 * y / height))
            draw.line([(0, y), (width, y)], fill=(color_value, 150, 200))
        
        # Add text
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Add generator name and prompt
        generator_name_display = self.available_generators[generator_name]['name']
        text_lines = [
            f"{generator_name_display}",
            "Demo Mode",
            f"Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"Prompt: {prompt}",
            "Set API key for real generation"
        ]
        
        y_offset = 50
        for line in text_lines:
            if font:
                # Add text with shadow for better visibility
                draw.text((20, y_offset + 2), line, fill=(0, 0, 0), font=font)
                draw.text((18, y_offset), line, fill=(255, 255, 255), font=font)
            else:
                # Fallback to simple text without font
                draw.text((20, y_offset), line, fill=(255, 255, 255))
            y_offset += 40
        
        # Simulate generation time
        await asyncio.sleep(2)  # Simulate API call time
        
        return image
    
    def get_leonardo_options(self) -> Dict[str, Any]:
        """Get Leonardo.ai specific options for frontend"""
        if "leonardo-api" not in self.available_generators:
            return {}
        
        generator_info = self.available_generators["leonardo-api"]
        return {
            "models": generator_info["models"],
            "preset_styles": generator_info["preset_styles"],
            "quality_levels": generator_info["quality_levels"],
            "aspect_ratios": generator_info["aspect_ratios"],
            "default_settings": {
                "model": "leonardo-diffusion-xl",
                "preset_style": "CREATIVE",
                "quality": "standard",
                "aspect_ratio": "1:1",
                "guidance_scale": 7.5,
                "num_inference_steps": 15
            }
        }
    
    def get_optimal_settings(self, generator_name: str) -> Dict[str, Any]:
        """Get optimal settings for a specific modern generator"""
        generator_info = self.available_generators.get(generator_name, {})
        
        base_settings = {
            "default_steps": 20,
            "max_steps": 50,
            "default_guidance": 7.5,
            "default_resolution": generator_info.get("max_resolution", (1024, 1024))
        }
        
        # Generator-specific optimizations
        if generator_name == "nano-banana-pro":
            return {
                **base_settings,
                "default_steps": 15,
                "max_steps": 30,
                "default_guidance": 6.0,
                "supported_styles": ["realistic", "artistic", "anime", "3d"]
            }
        elif generator_name == "seedream":
            return {
                **base_settings,
                "default_steps": 25,
                "max_steps": 40,
                "default_guidance": 7.0,
                "supported_styles": ["photorealistic", "cinematic", "fantasy", "abstract"]
            }
        elif generator_name == "dall-e-3":
            return {
                **base_settings,
                "default_steps": 1,  # DALL-E 3 doesn't use steps
                "max_steps": 1,
                "default_guidance": 0,  # Not applicable
                "supported_sizes": ["1024x1024", "1792x1024", "1024x1792"]
            }
        elif generator_name == "leonardo-api":
            return {
                **base_settings,
                "default_steps": 15,
                "max_steps": 30,
                "default_guidance": 6.5,
                "supported_presets": ["CREATIVE", "DYNAMIC", "ARTISTIC", "PHOTOGRAPHIC"]
            }
        
        return base_settings
    
    def get_generator_recommendations(self) -> Dict[str, str]:
        """Get recommendations for different use cases"""
        return {
            "speed": "nano-banana-pro - Fastest generation with excellent quality",
            "quality": "dall-e-3 - Best overall quality and natural language understanding",
            "professional": "seedream - Professional-grade results with style control",
            "artistic": "leonardo-api - Great for artistic and creative styles",
            "balance": "nano-banana-pro - Best balance of speed and quality"
        }
