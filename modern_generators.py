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
                    "id": None,
                    "name": "Leonardo Phoenix Enhanced",
                    "description": "Optimized SD 1.5 with LEONARDO preset (best available with current plan)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Requires higher-tier subscription for true Phoenix models"
                },
                "phoenix-0-9": {
                    "id": None,
                    "name": "Leonardo Legacy Enhanced",
                    "description": "Enhanced SD 1.5 with optimizations",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Legacy model with enhanced prompt engineering"
                },
                "universal": {
                    "id": None,
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
            "name": "Modal H100 GPU",
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
                    "max_resolution": (512, 512),
                    "aspect_ratios": ["1:1"],
                    "note": "Fast generation on H100"
                },
                "stabilityai/stable-diffusion-xl-base-1.0": {
                    "name": "Stable Diffusion XL",
                    "description": "High-quality SDXL model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Higher quality, longer generation"
                },
                "runwayml/stable-diffusion-v2-1": {
                    "name": "Stable Diffusion v2.1",
                    "description": "Improved Stable Diffusion v2",
                    "max_resolution": (768, 768),
                    "aspect_ratios": ["1:1", "9:16", "16:9"],
                    "note": "Better composition and quality"
                }
            },
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": (512, 512)},
                {"id": "16:9", "name": "Widescreen", "resolution": (768, 432)},
                {"id": "9:16", "name": "Portrait", "resolution": (432, 768)}
            ],
            "quality_levels": [
                {"id": "standard", "name": "Standard", "description": "20 steps, good quality"},
                {"id": "high", "name": "High", "description": "30 steps, better quality"},
                {"id": "ultra", "name": "Ultra", "description": "50 steps, best quality"}
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
    
    async def generate_with_nano_banana_pro(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Nano Banana Pro API"""
        if "nano-banana-pro" not in self.api_keys:
            raise ValueError("API key required for Nano Banana Pro")
        
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
                self.available_generators["nano-banana-pro"]["api_endpoint"],
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
                self.available_generators["seedream"]["api_endpoint"],
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
        """Generate image using Modal H100 GPU"""
        if not MODAL_AVAILABLE:
            raise ValueError("Modal not installed. Install with: pip install modal")
        
        # Get model name from kwargs
        model_name = kwargs.get("model", "runwayml/stable-diffusion-v1-5")
        
        # Create Modal function stub if not already created
        try:
            # Import Modal app and function
            import modal_integration
            from modal_integration import generate_image
            
            print(f"[MODAL] Modal function imported successfully")
            print(f"[MODAL] Function object: {generate_image}")
            
        except ImportError:
            print("[ERROR] Modal integration module not found")
            raise ValueError("Modal integration not properly imported")
        
        try:
            # Call Modal function remotely - this will execute on Modal's infrastructure
            print(f"[MODAL] Calling remote Modal function...")
            print(f"[MODAL] Model: {model_name}")
            print(f"[MODAL] Prompt: {prompt[:100]}...")
            
            # Use Modal's remote execution - this runs on Modal's servers, not local GPU
            image_bytes = generate_image.remote(prompt, model_name)
            
            print(f"[MODAL] Received {len(image_bytes)} bytes from remote Modal GPU")
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize if target dimensions specified
            target_width = kwargs.get("width", None)
            target_height = kwargs.get("height", None)
            
            if target_width and target_height and image.size != (target_width, target_height):
                try:
                    resample = getattr(Image, "Resampling", Image).LANCZOS
                except Exception:
                    resample = Image.LANCZOS
                image = ImageOps.fit(image, (target_width, target_height), method=resample)
                print(f"[MODAL] Resized image to: {image.size}")
            
            print(f"[MODAL] Generated image: {image.size}")
            return image
            
        except Exception as e:
            print(f"[ERROR] Modal generation failed: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Error details: {str(e)}")
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
        enhanced_prompt = self._enhance_prompt_for_leonardo(prompt)
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
            raise ValueError(f"Model {model_key} not available for Leonardo.ai")
        
        model_info = models[model_key]
        print(f"[SEARCH] Selected model: {model_info['name']} (ID: {model_info['id']})")
        
        # Get resolution from aspect ratio
        aspect_ratios = {ar["id"]: ar for ar in generator_info["aspect_ratios"]}
        if aspect_ratio not in aspect_ratios:
            aspect_ratio = "1:1"  # Default fallback
        
        resolution = aspect_ratios[aspect_ratio]["resolution"]
        width, height = resolution
        print(f"[SEARCH] Resolution: {width}x{height}")
        
        # Build generation payload with optimized SD 1.5 settings
        generation_payload = {
            "prompt": enhanced_prompt,  # Use enhanced prompt
            "width": width,
            "height": height,
            "num_images": 1,
            "alchemy": False,  # Not supported by SD 1.5
            "ultra": False,    # Not supported by SD 1.5
            "contrast": 3.5,   # Standard contrast for SD 1.5
            "negative_prompt": self._get_optimized_negative_prompt(kwargs.get("negative_prompt", "")),
            "num_inference_steps": kwargs.get("num_inference_steps", 30),  # More steps for better quality
            "guidance_scale": kwargs.get("guidance_scale", 8.0)   # Higher guidance for better prompt adherence
        }
        
        # Add preset style if specified and valid
        preset_style = kwargs.get("preset_style", "LEONARDO")  # Default to LEONARDO for best quality
        valid_styles = ["LEONARDO", "CREATIVE", "DYNAMIC", "CINEMATIC", "FANTASY_ART", "ANIME", "COMIC_BOOK", "ILLUSTRATION"]
        if preset_style in valid_styles:
            generation_payload["presetStyle"] = preset_style
            print(f"[STYLE] Applying Leonardo preset style: {preset_style}")
        else:
            print(f"[STYLE] Invalid style {preset_style}, using LEONARDO default")
            generation_payload["presetStyle"] = "LEONARDO"
        
        # Only add modelId if it's not None (let Leonardo choose default model)
        if model_info["id"] is not None:
            generation_payload["modelId"] = model_info["id"]
            print(f"[SEARCH] Using specific model ID: {model_info['id']}")
        else:
            print(f"[SEARCH] Using Leonardo default model (no modelId specified)")
        
        print(f"[QUALITY] SD 1.5 Optimized Settings: steps={generation_payload['num_inference_steps']}, guidance={generation_payload['guidance_scale']}")
        print(f"[QUALITY] Enhanced prompt with {len(enhanced_prompt.split(','))} quality terms")
        print(f"[QUALITY] Comprehensive negative prompt for maximum quality")
        
        print(f"[SEARCH] Final payload: {json.dumps(generation_payload, indent=2)}")
        
        print(f"[ART] Leonardo.ai generation with {model_info['name']}")
        print(f"[RATIO] Aspect Ratio: {aspect_ratio} ({width}x{height})")
        print(f"[STYLE] Style: {preset_style}")
        print(f"[QUALITY] Quality: {kwargs.get('quality', 'standard')}")
        print(f"[SEARCH] Payload: {json.dumps(generation_payload, indent=2)}")
        print(f"[SEARCH] Sending request to: {self.available_generators['leonardo-api']['api_endpoint']}")
        print(f"[SEARCH] Headers: {headers}")
        print(f"[SEARCH] Payload: {json.dumps(generation_payload, indent=2)}")
        
        try:
            print(f"[SEND] Sending POST request...")
            # Start generation
            response = requests.post(
                self.available_generators["leonardo-api"]["api_endpoint"],
                headers=headers,
                json=generation_payload,
                timeout=30
            )
            
            print(f"[OK] Response received: {response.status_code}")
            print(f"[HEADERS] Response headers: {dict(response.headers)}")
            print(f"[BODY] Response body: {response.text}")
            
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
                return await self.generate_with_nano_banana(prompt, **kwargs)
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
