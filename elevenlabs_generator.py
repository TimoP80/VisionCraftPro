"""
ElevenLabs Image Generators Integration
Support for ElevenLabs API with multiple models and features

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import base64
import io
from typing import Dict, Any, Optional, List
from PIL import Image
import os
import time
import asyncio

class ElevenLabsGeneratorManager:
    """Manages ElevenLabs image generation services"""
    
    def __init__(self):
        self.generators = {}
        self.current_generator = None
        self.api_keys = {}
        self.api_keys_file = "api_keys.json"
        
        # Load API keys on initialization
        print("Initializing ElevenLabs GeneratorManager...")
        self._load_api_keys()
        print(f"Loaded {len(self.api_keys)} API key(s)")
        
        # Initialize available generators
        self.available_generators = {}
        self._setup_elevenlabs_generators()
        print(f"Initialized {len(self.available_generators)} generator(s)")
    
    def _setup_elevenlabs_generators(self):
        """Setup ElevenLabs generator configuration"""
        self.available_generators["elevenlabs-api"] = {
            "name": "ElevenLabs API",
            "type": "api",
            "description": "Advanced AI image generation with multiple models",
            "api_endpoint": "https://api.elevenlabs.io/v1/text2image",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Fast",
            "cost": "Paid",
            "features": ["text-to-image", "multiple-models", "high-resolution", "controlnet"],
            "models": {
                "realistic-vision-v6": {
                    "id": "realistic-vision-v6",
                    "name": "Realistic Vision v6",
                    "description": "Photorealistic model with high detail",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["photorealistic", "high-detail", "professional"]
                },
                "dreamshaper-v8": {
                    "id": "dreamshaper-v8",
                    "name": "DreamShaper v8",
                    "description": "Artistic model with creative capabilities",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["artistic", "creative", "detailed"]
                },
                "absolutereality-v1.8.6": {
                    "id": "absolutereality-v1.8.6",
                    "name": "Absolute Reality v1.8.6",
                    "description": "Hyperrealistic model with extreme detail",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["hyperrealistic", "extreme-detail", "professional"]
                },
                "amazing-realism-v5.2": {
                    "id": "amazing-realism-v5.2",
                    "name": "Amazing Realism v5.2",
                    "description": "Realistic model with artistic flair",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["realistic", "artistic", "detailed"]
                },
                "cinematic-v1": {
                    "id": "cinematic-v1",
                    "name": "Cinematic v1",
                    "description": "Cinematic and movie-like image generation",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["cinematic", "film-like", "dramatic"]
                },
                "fantasy-art-v6": {
                    "id": "fantasy-art-v6",
                    "name": "Fantasy Art v6",
                    "description": "Fantasy and artistic model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["fantasy", "artistic", "creative"]
                },
                "anime-v3": {
                    "id": "anime-v3",
                    "name": "Anime v3",
                    "description": "Anime and manga-style generation",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["anime", "manga", "cartoon"]
                },
                "3d-animation-v2.1": {
                    "id": "3d-animation-v2.1",
                    "name": "3D Animation v2.1",
                    "description": "3D and animation-style generation",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["3d", "animation", "cartoon"]
                },
                "sdxl-lightning-v1": {
                    "id": "sdxl-lightning-v1",
                    "name": "SDXL Lightning v1",
                    "description": "Fast SDXL generation with 4-8 steps",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["sdxl", "fast", "lightning"]
                },
                "sdxl-turbo-v1": {
                    "id": "sdxl-turbo-v1",
                    "name": "SDXL Turbo v1",
                    "description": "Optimized SDXL for fast generation",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "features": ["sdxl", "turbo", "optimized"]
                }
            },
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
            ],
            "style_presets": [
                {"id": "photorealistic", "name": "Photorealistic", "description": "Realistic and detailed"},
                {"id": "artistic", "name": "Artistic", "description": "Creative and stylized"},
                {"id": "cinematic", "name": "Cinematic", "description": "Film-like and dramatic"},
                {"id": "fantasy", "name": "Fantasy", "description": "Imaginative and magical"},
                {"id": "anime", "name": "anime", "description": "Anime and manga style"},
                {"id": "3d", "name": "3D", "description": "3D rendered look"},
                {"id": "oil", "name": "Oil Painting", "description": "Traditional oil painting style"},
                {"id": "watercolor", "name": "Watercolor", "description": "Watercolor painting style"},
                {"id": "sketch", "name": "Sketch", "description": "Pencil sketch style"}
            ]
        }
    
    def set_api_key(self, generator_name: str, api_key: str):
        """Set API key for a generator and persist to file"""
        self.api_keys[generator_name] = api_key
        self._save_api_keys()
        print(f"[OK] API key set for {generator_name}")
    
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
        return self.available_generators
    
    def get_generator_info(self, generator_name: str) -> Optional[Dict]:
        """Get information about a specific generator"""
        return self.available_generators.get(generator_name)
    
    async def generate_with_elevenlabs(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using ElevenLabs API"""
        print(f"[ELEVENLABS] ElevenLabs generation with {prompt[:100]}...")
        
        # Check API key
        if 'elevenlabs-api' not in self.api_keys:
            raise ValueError("ElevenLabs API key not set. Please set your API key first.")
        
        api_key = self.api_keys['elevenlabs-api']
        
        # Validate API key format
        if not isinstance(api_key, str) or len(api_key) > 1000 or len(api_key) < 10:
            raise ValueError("ElevenLabs API key appears to be corrupted or invalid. Please check your API key configuration.")
        
        # Check if API key contains unexpected characters
        if 'MakeNSIS' in api_key or 'Copyright' in api_key or '\r\n' in api_key:
            raise ValueError("ElevenLabs API key appears to be corrupted with system output. Please reset your API key.")
        
        print(f"API key found: {'*' * 10}{api_key[-4:]}")
        
        # Get model information
        generator_info = self.available_generators['elevenlabs-api']
        models = generator_info['models']
        
        # Get model selection
        model_key = kwargs.get('model', 'realistic-vision-v6')
        if model_key not in models:
            raise ValueError(f"Model {model_key} not available for ElevenLabs. Available models: {list(models.keys())}")
        
        model_info = models[model_key]
        print(f"[MODEL] Using ElevenLabs model: {model_info['name']}")
        
        # Get resolution from aspect ratio
        aspect_ratios = {ar["id"]: ar for ar in generator_info["aspect_ratios"]}
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        if aspect_ratio not in aspect_ratios:
            aspect_ratio = "1:1"  # Default fallback
        
        resolution = aspect_ratios[aspect_ratio]["resolution"]
        width, height = resolution
        print(f"[RESOLUTION] {width}x{height} (aspect ratio: {aspect_ratio})")
        
        # Build generation payload
        generation_payload = {
            "prompt": prompt,
            "model": model_key,
            "width": width,
            "height": height,
            "num_images": 1,
            "negative_prompt": kwargs.get("negative_prompt", ""),
            "seed": kwargs.get("seed", -1) if kwargs.get("seed", -1) != -1 else None,
            "guidance_scale": kwargs.get("guidance_scale", 7.0),
            "num_inference_steps": kwargs.get("num_inference_steps", 30),
            "style": kwargs.get("style", "photorealistic"),
            "scheduler": kwargs.get("scheduler", "KLMS"),
            "output_format": "png"
        }
        
        # Add quality settings
        quality = kwargs.get("quality", "high")
        if quality == "ultra":
            generation_payload["num_inception_steps"] = 50
            generation_payload["guidance_scale"] = 8.0
        elif quality == "standard":
            generation_payload["num_inception_steps"] = 20
            generation_payload["guidance_scale"] = 6.0
        
        print(f"[QUALITY] Quality: {quality}")
        print(f"[QUALITY] Steps: {generation_payload['num_inference_steps']}, Guidance: {generation_payload['guidance_scale']}")
        print(f"[QUALITY] Style: {generation_payload['style']}")
        print(f"[QUALITY] Scheduler: {generation_payload['scheduler']}")
        
        print(f"[PAYLOAD] Final payload: {json.dumps(generation_payload, indent=2)}")
        
        headers = {
            "accept": "application/json",
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        try:
            print(f"[SEND] Sending POST request to ElevenLabs API...")
            
            # Start generation
            response = requests.post(
                generator_info["api_endpoint"],
                headers=headers,
                json=generation_payload,
                timeout=120  # Longer timeout for ElevenLabs
            )
            
            print(f"[OK] Response received: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if it's a synchronous generation (immediate result)
                if "images" in result:
                    # Synchronous generation
                    images = result["images"]
                    if images and len(images) > 0:
                        image_data = images[0]
                        
                        # Convert base64 to PIL Image
                        if "url" in image_data:
                            # Download the image from URL
                            img_response = requests.get(image_data["url"], timeout=30)
                            img_response.raise_for_status()
                            image = Image.open(io.BytesIO(img_response.content))
                        elif "image_base64" in image_data:
                            # Decode base64 image
                            image_bytes = base64.b64decode(image_data["image_base64"])
                            image = Image.open(io.BytesIO(image_bytes))
                        else:
                            raise ValueError("Unknown image format in response")
                        
                        generation_time = 0.0  # Synchronous generation
                        vram_used = 0.0  # API generation
                        
                        print(f"[OK] Synchronous generation completed in {generation_time:.2f}s")
                        return image
                    else:
                        raise ValueError("No image in response")
                else:
                    raise ValueError("Unknown response format")
            else:
                print(f"[ERROR] HTTP Error: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                raise requests.exceptions.HTTPError(f"ElevenLabs API error: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] ElevenLabs generation failed: {e}")
            raise
    
    async def generate_image(self, generator_name: str, prompt: str, **kwargs) -> Image.Image:
        """Generate image using specified generator"""
        if generator_name == "elevenlabs-api":
            return await self.generate_with_elevenlabs(prompt, **kwargs)
        else:
            raise ValueError(f"Unknown generator: {generator_name}")
    
    def get_generator_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for ElevenLabs generators"""
        return {
            "elevenlabs-api": {
                "recommended_for": ["photorealistic", "artistic", "professional"],
                "best_models": ["realistic-vision-v6", "absolutereality-v1.8.6"],
                "fast_models": ["sdxl-lightning-v1", "sdxl-turbo-v1"],
                "creative_models": ["dreamshaper-v8", "fantasy-art-v6", "anime-v3"],
                "description": "Advanced AI image generation with professional quality"
            }
        }
    
    def get_webhook_endpoints(self) -> Dict[str, str]:
        """Get webhook endpoints for async generation"""
        return {
            "elevenlabs-api": {
                "status": "ElevenLabs supports synchronous generation only",
                "webhook": "Not applicable"
            }
        }
    
    def get_leonardo_options(self) -> Dict[str, Any]:
        """Get Leonardo-specific options (for compatibility)"""
        return {
            "preset_styles": [],
            "quality_levels": self.available_generators.get("elevenlabs-api", {}).get("quality_levels", []),
            "aspect_ratios": self.available_generators.get("elevenlabs-api", {}).get("aspect_ratios", [])
        }
