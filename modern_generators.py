"""
Modern Commercial Image Generators
Support for Nano Banana Pro, Seedream, and other API-based generators
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
        print(f"Initialized {len(self.available_generators)} generator(s)")
    
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
                    "name": "Phoenix 1.0",
                    "description": "Universal model for all types of images",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"]
                },
                "phoenix-0-9": {
                    "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",
                    "name": "Phoenix 0.9",
                    "description": "Previous version of Phoenix model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"]
                },
                "universal": {
                    "id": "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8",
                    "name": "Universal",
                    "description": "General purpose model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"]
                }
            },
            "preset_styles": [
                {"id": "CREATIVE", "name": "Creative", "description": "Balanced creative output"},
                {"id": "DYNAMIC", "name": "Dynamic", "description": "More dynamic and dramatic"},
                {"id": "ARTISTIC", "name": "Artistic", "description": "Enhanced artistic style"},
                {"id": "PHOTOGRAPHIC", "name": "Photographic", "description": "Photorealistic output"},
                {"id": "CINEMATIC", "name": "Cinematic", "description": "Movie-like quality"},
                {"id": "FANTASY_ART", "name": "Fantasy Art", "description": "Fantasy themed"},
                {"id": "STEAMPUNK", "name": "Steampunk", "description": "Victorian sci-fi"},
                {"id": "ANIME", "name": "Anime", "description": "Anime style"},
                {"id": "COMIC_BOOK", "name": "Comic Book", "description": "Comic book style"},
                {"id": "3D_RENDER", "name": "3D Render", "description": "3D rendered look"}
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
        
        # Build generation payload according to official docs - without webhook
        generation_payload = {
            "prompt": prompt,
            "modelId": model_info["id"],
            "width": width,
            "height": height,
            "num_images": 1,
            "alchemy": False,
            "ultra": kwargs.get("quality", "standard") == "ultra",
            "contrast": kwargs.get("contrast", 3.5),  # Valid values: 3, 3.5, 4
            "negative_prompt": kwargs.get("negative_prompt", "")
        }
        
        # Only add optional parameters if they might be causing issues
        if kwargs.get("guidance_scale", 7.5) != 7.5:
            generation_payload["guidance_scale"] = kwargs.get("guidance_scale")
        if kwargs.get("num_inference_steps", 15) != 15:
            generation_payload["num_inference_steps"] = kwargs.get("num_inference_steps")
        
        # Note: preset_style is not being used in the payload for now
        # Leonardo.ai requires specific styleUUIDs which need to be fetched from their API
        preset_style = kwargs.get("preset_style", "CREATIVE")
        print(f"[STYLE] Preset style selected: {preset_style} (not applied to payload)")
        
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
