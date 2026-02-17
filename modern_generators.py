"""
Modern Commercial Image Generators
Support for Nano Banana Pro, Seedream, Leonardo.ai API-based generators
"""

import os
import json
import time
import requests
import base64
import io
import random
from typing import Dict, List, Optional, Any, Union
from PIL import Image, ImageOps
from datetime import datetime

# Try to import Azure Identity for Entra ID authentication
try:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    AZURE_IDENTITY_AVAILABLE = True
    print("✅ Azure Identity package available for Entra ID authentication")
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False
    print("⚠️ Azure Identity package not available, falling back to API key authentication")

def retry_with_backoff(request_func, max_retries=3, base_delay=1.0, max_delay=60.0):
    """
    Retry function with exponential backoff for handling rate limits
    """
    for attempt in range(max_retries):
        try:
            response = request_func()
            
            # If successful, return the response
            if response.status_code == 200:
                return response
            
            # If rate limited, wait and retry
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    # Calculate exponential backoff with jitter
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    print(f"[AZURE] Rate limited (429), retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"[AZURE] Rate limited after {max_retries} attempts")
                    return response
            
            # For other errors, don't retry
            return response
            
        except Exception as e:
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"[AZURE] Request failed: {e}, retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            else:
                print(f"[AZURE] Request failed after {max_retries} attempts: {e}")
                raise

import asyncio
import replicate

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
        self._setup_replicate()
        self._setup_azure_ai()
        print(f"Initialized {len(self.available_generators)} generator(s)")
    
    def _setup_replicate(self):
        """Setup Replicate generator configuration"""
        self.available_generators["replicate-api"] = {
            "name": "Replicate API",
            "type": "api",
            "description": "Professional AI models including Stable Diffusion XL, SDXL Turbo, and more",
            "api_endpoint": "https://api.replicate.com/v1/predictions",
            "cost": "$0.01-0.10 per image",
            "speed": "Fast",
            "max_resolution": [1024, 1024],
            "models": {
                "black-forest-labs/flux-schnell": {
                    "name": "FLUX.1 Schnell",
                    "description": "Fastest image generation model, 1-4 steps only",
                    "cost": "~$0.003 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 4
                },
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b": {
                    "name": "Stable Diffusion XL",
                    "description": "High-quality general purpose model",
                    "cost": "~$0.005 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 25
                },
                "black-forest-labs/flux-1.1-pro": {
                    "name": "FLUX.1.1 Pro",
                    "description": "Most powerful FLUX model, professional quality",
                    "cost": "~$0.015 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 25
                },
                "jyoung105/sdxl-turbo:93c488b9fbd6bea622d354c8dcce2724c5f67adb92ccf909038042a21c5238a7": {
                    "name": "SDXL Turbo",
                    "description": "Fast generation with good quality",
                    "cost": "~$0.003 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 10
                },
                "ideogram-ai/ideogram-v3-turbo": {
                    "name": "Ideogram V3 Turbo",
                    "description": "Excellent for text and logos in images",
                    "cost": "~$0.008 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 25
                },
                "lucataco/realistic-vision-v5.1:2c8e954decbf70b7607a4414e5785ef9e4de4b8c51d50fb8b8b349160e0ef6bb": {
                    "name": "Realistic Vision v5.1",
                    "description": "Photorealistic images with high detail",
                    "cost": "~$0.015 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 25
                },
                "google/nano-banana-pro": {
                    "name": "Nano Banana Pro",
                    "description": "Google's fast text-to-image model",
                    "cost": "~$0.008 per image",
                    "resolution": [1024, 1024],
                    "recommended_steps": 20
                },
                "ai-forever/kandinsky-2.2": {
                    "name": "Kandinsky 2.2",
                    "description": "Artistic model with unique style",
                    "cost": "~$0.008 per image",
                    "resolution": [512, 512],
                    "recommended_steps": 50
                }
            },
            "quality_levels": {
                "standard": {"description": "Standard quality", "cost_multiplier": 1.0},
                "high": {"description": "High quality", "cost_multiplier": 1.5}
            },
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": [1024, 1024]},
                {"id": "16:9", "name": "Landscape", "resolution": [1344, 768]},
                {"id": "9:16", "name": "Portrait", "resolution": [768, 1344]},
                {"id": "4:3", "name": "Standard", "resolution": [1024, 768]},
                {"id": "3:4", "name": "Vertical", "resolution": [768, 1024]}
            ]
        }
        
        # Also add Kandinsky as a separate generator for easier access
        self.available_generators["kandinsky-22"] = {
            "name": "Kandinsky 2.2",
            "type": "api",
            "description": "Artistic model with unique Russian aesthetic",
            "api_endpoint": "https://api.replicate.com/v1/predictions",
            "cost": "~$0.008 per image",
            "speed": "Medium",
            "max_resolution": [512, 512],
            "models": {
                "ai-forever/kandinsky-2.2": {
                    "name": "Kandinsky 2.2",
                    "description": "Artistic model with unique style",
                    "cost": "~$0.008 per image",
                    "resolution": [512, 512],
                    "recommended_steps": 50
                }
            }
        }
    
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
                    "name": "Phoenix",
                    "description": "Leonardo's flagship model - highest quality",
                    "max_resolution": (1472, 832),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Best available model for highest quality",
                    "api_version": "v1"
                },
                "phoenix-0-9": {
                    "id": None,
                    "name": "Phoenix 0.9",
                    "description": "Previous version of Phoenix model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Still high quality but older version",
                    "api_version": "v1"
                },
                "universal": {
                    "id": None,
                    "name": "Universal Enhanced",
                    "description": "Universal model with advanced prompt optimization",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Optimized for all content types",
                    "api_version": "v1"
                },
                "flux-dev": {
                    "id": "b2614463-296c-462a-9586-aafdb8f00e36",
                    "name": "FLUX Dev",
                    "description": "FLUX development model for testing",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Development version of FLUX",
                    "api_version": "v1"
                },
                "flux-schnell": {
                    "id": "1dd50843-d653-4516-a8e3-f0238ee453ff",
                    "name": "FLUX Schnell",
                    "description": "Fastest FLUX model for quick generation",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Ultra-fast generation with good quality",
                    "api_version": "v1"
                },
                "flux-1-kontext": {
                    "id": "28aeddf8-bd19-4803-80fc-79602d1a9989",
                    "name": "FLUX.1 Kontext [pro]",
                    "description": "FLUX 1.1 with context awareness",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Professional model with context understanding",
                    "api_version": "v1"
                },
                "flux-2-pro": {
                    "id": None,
                    "name": "FLUX.2 Pro",
                    "description": "Latest FLUX 2.0 Pro model",
                    "max_resolution": (1440, 1440),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "2:3"],
                    "note": "Most advanced FLUX model",
                    "api_version": "v2"
                },
                "gpt-image-1-5": {
                    "id": None,
                    "name": "GPT Image-1.5",
                    "description": "OpenAI's GPT Image generation model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "AI-powered image generation",
                    "api_version": "v2"
                },
                "ideogram-3-0": {
                    "id": None,
                    "name": "Ideogram 3.0",
                    "description": "Text-to-image with typography",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Excellent for text and logo generation",
                    "api_version": "v2"
                },
                "lucid-origin": {
                    "id": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9",
                    "name": "Lucid Origin",
                    "description": "Creative and artistic model",
                    "max_resolution": (1920, 1080),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Perfect for creative and artistic content",
                    "api_version": "v1"
                },
                "lucid-realism": {
                    "id": "05ce0082-2d80-4a2d-8653-4d1c85e2418e",
                    "name": "Lucid Realism",
                    "description": "Photorealistic and detailed model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Highly realistic and detailed",
                    "api_version": "v1"
                },
                "nano-banana": {
                    "id": None,
                    "name": "Nano Banana",
                    "description": "Fast and efficient model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Quick generation with good quality",
                    "api_version": "v2"
                },
                "nano-banana-pro": {
                    "id": None,
                    "name": "Nano Banana Pro",
                    "description": "Enhanced Nano Banana model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1"],  # Only 1:1 confirmed working
                    "note": "Higher quality Nano Banana model - 1024x1024 only",
                    "api_version": "v2"
                },
                "phoenix": {
                    "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",
                    "name": "Phoenix",
                    "description": "Leonardo's flagship model",
                    "max_resolution": (1472, 832),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Best available model for highest quality",
                    "api_version": "v1"
                },
                "seedream-4-0": {
                    "id": None,
                    "name": "Seedream 4.0",
                    "description": "Creative and imaginative model",
                    "max_resolution": (1920, 1080),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Perfect for creative concepts",
                    "api_version": "v2"
                },
                "seedream-4-5": {
                    "id": None,
                    "name": "Seedream 4.5",
                    "description": "Enhanced Seedream model",
                    "max_resolution": (1920, 1080),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    "note": "Latest version with improved quality",
                    "api_version": "v2"
                }
            },
            "preset_styles": [
                {"id": "CREATIVE", "name": "Creative", "description": "Balanced creative output"},
                {"id": "DYNAMIC", "name": "Dynamic", "description": "More dynamic and dramatic"},
                {"id": "CINEMATIC", "name": "Cinematic", "description": "Movie-like quality"},
                {"id": "FANTASY_ART", "name": "Fantasy Art", "description": "Fantasy themed"},
                {"id": "ANIME", "name": "Anime", "description": "Anime style"},
                {"id": "COMIC_BOOK", "name": "Comic Book", "description": "Comic book style"},
                {"id": "REALISTIC", "name": "Realistic", "description": "Photorealistic style"},
                {"id": "ARTISTIC", "name": "Artistic", "description": "Painterly and artistic"},
                {"id": "3D_RENDER", "name": "3D Render", "description": "3D rendering style"},
                {"id": "PHOTOGRAPHIC", "name": "Photographic", "description": "Photography style"},
                {"id": "ILLUSTRATION", "name": "Illustration", "description": "Book illustration style"},
                {"id": "CONCEPT_ART", "name": "Concept Art", "description": "Concept design style"},
                {"id": "SKETCH", "name": "Sketch", "description": "Pencil sketch style"},
                {"id": "OIL_PAINTING", "name": "Oil Painting", "description": "Oil painting style"},
                {"id": "WATERCOLOR", "name": "Watercolor", "description": "Watercolor painting"},
                {"id": "CHARACTER", "name": "Character", "description": "Character design"},
                {"id": "LANDSCAPE", "name": "Landscape", "description": "Landscape photography"},
                {"id": "PORTRAIT", "name": "Portrait", "description": "Portrait photography"},
                {"id": "ABSTRACT", "name": "Abstract", "description": "Abstract art"},
                {"id": "MINIMALIST", "name": "Minimalist", "description": "Clean and minimal"},
                {"id": "VINTAGE", "name": "Vintage", "description": "Vintage and retro"},
                {"id": "GOTHIC", "name": "Gothic", "description": "Dark and gothic"},
                {"id": "STEAMPUNK", "name": "Steampunk", "description": "Victorian steampunk"},
                {"id": "CYBERPUNK", "name": "Cyberpunk", "description": "Futuristic cyberpunk"},
                {"id": "RETRO", "name": "Retro", "description": "80s and 90s retro"},
                {"id": "PIXEL_ART", "name": "Pixel Art", "description": "Pixel art style"},
                {"id": "CARTOON", "name": "Cartoon", "description": "Cartoon style"},
                {"id": "MANGA", "name": "Manga", "description": "Manga comic style"},
                {"id": "CHIBI", "name": "Chibi", "description": "Cute chibi style"},
                {"id": "TATTOO", "name": "Tattoo", "description": "Tattoo design style"},
                {"id": "GRAFFITI", "name": "Graffiti", "description": "Street art graffiti"},
                {"id": "NEON", "name": "Neon", "description": "Neon lighting effects"},
                {"id": "PASTEL", "name": "Pastel", "description": "Soft pastel colors"},
                {"id": "MONOCHROME", "name": "Monochrome", "description": "Black and white"},
                {"id": "SEPIA", "name": "Sepia", "description": "Sepia tone"},
                {"id": "HIGH_CONTRAST", "name": "High Contrast", "description": "Bold and dramatic"},
                {"id": "SOFT_FOCUS", "name": "Soft Focus", "description": "Dreamy and soft"},
                {"id": "HDR", "name": "HDR", "description": "High dynamic range"},
                {"id": "LONG_EXPOSURE", "name": "Long Exposure", "description": "Photography effect"},
                {"id": "MACRO", "name": "Macro", "description": "Close-up photography"},
                {"id": "WIDE_ANGLE", "name": "Wide Angle", "description": "Wide lens effect"},
                {"id": "FISHEYE", "name": "Fisheye", "description": "Fisheye lens effect"},
                {"id": "TILT_SHIFT", "name": "Tilt Shift", "description": "Miniature effect"},
                {"id": "VIGNETTE", "name": "Vignette", "description": "Darkened edges"},
                {"id": "BOKEH", "name": "Bokeh", "description": "Blurry background"},
                {"id": "LENS_FLARE", "name": "Lens Flare", "description": "Light flare effects"},
                {"id": "MOTION_BLUR", "name": "Motion Blur", "description": "Motion blur effect"},
                {"id": "DOUBLE_EXPOSURE", "name": "Double Exposure", "description": "Multiple exposures"},
                {"id": "INFRARED", "name": "Infrared", "description": "Infrared photography"},
                {"id": "THERMAL", "name": "Thermal", "description": "Thermal imaging"},
                {"id": "XRAY", "name": "X-Ray", "description": "X-ray vision"},
                {"id": "NIGHT_VISION", "name": "Night Vision", "description": "Night vision effect"},
                {"id": "UV", "name": "UV Light", "description": "UV lighting effects"},
                {"id": "MIRROR", "name": "Mirror", "description": "Mirror reflection"},
                {"id": "KALEIDOSCOPE", "name": "Kaleidoscope", "description": "Kaleidoscope pattern"},
                {"id": "GLITCH", "name": "Glitch", "description": "Digital glitch effect"},
                {"id": "PIXELATED", "name": "Pixelated", "description": "Pixelated effect"},
                {"id": "DITHERED", "name": "Dithered", "description": "Color dithering"},
                {"id": "POSTER", "name": "Poster", "description": "Poster art style"},
                {"id": "COMIC_STRIP", "name": "Comic Strip", "description": "Comic book panels"},
                {"id": "MANGA_PANEL", "name": "Manga Panel", "description": "Manga comic panels"},
                {"id": "STORYBOARD", "name": "Storyboard", "description": "Film storyboard"},
                {"id": "CONCEPT_BOARD", "name": "Concept Board", "description": "Concept art board"},
                {"id": "MOOD_BOARD", "name": "Mood Board", "description": "Mood and atmosphere"},
                {"id": "COLOR_PALETTE", "name": "Color Palette", "description": "Specific color scheme"},
                {"id": "BLACK_AND_WHITE", "name": "Black and White", "description": "Monochrome photography"},
                {"id": "COLOR_POP", "name": "Color Pop", "description": "Vibrant colors"},
                {"id": "EARTH_TONES", "name": "Earth Tones", "description": "Natural earth colors"},
                {"id": "OCEAN_BLUE", "name": "Ocean Blue", "description": "Ocean blue colors"},
                {"id": "FOREST_GREEN", "name": "Forest Green", "description": "Forest green colors"},
                {"id": "SUNSET_ORANGE", "name": "Sunset Orange", "description": "Sunset orange colors"},
                {"id": "PURPLE_DREAM", "name": "Purple Dream", "description": "Purple fantasy colors"},
                {"id": "GOLDEN_HOUR", "name": "Golden Hour", "description": "Warm golden light"},
                {"id": "BLUE_HOUR", "name": "Blue Hour", "description": "Cool blue light"},
                {"id": "MAGIC_HOUR", "name": "Magic Hour", "description": "Perfect lighting"},
                {"id": "GOLDEN_GLOW", "name": "Golden Glow", "description": "Golden light effect"},
                {"id": "SILVER_GLOW", "name": "Silver Glow", "description": "Silver light effect"},
                {"id": "RAINBOW", "name": "Rainbow", "description": "Rainbow colors"},
                {"id": "NEON_RAINBOW", "name": "Neon Rainbow", "description": "Neon rainbow colors"},
                {"id": "PASTEL_RAINBOW", "name": "Pastel Rainbow", "description": "Soft rainbow colors"},
                {"id": "MONOCHROME_RAINBOW", "name": "Monochrome Rainbow", "description": "B&W rainbow"}
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
    
    def _setup_azure_ai(self):
        """Setup Azure AI generator configuration"""
        self.available_generators["azure-ai"] = {
            "name": "Azure AI",
            "type": "api",
            "description": "Microsoft Azure AI with FLUX models",
            "api_endpoint": "https://azure-flux-2-resource.openai.azure.com",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Fast",
            "cost": "Azure Credits",
            "features": ["text-to-image", "enterprise-grade", "high-availability"],
            "models": {
                "flux-1-1-pro": {
                    "name": "FLUX.1.1 Pro",
                    "description": "FLUX 1.1 Pro model on Azure (working)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1"],
                    "note": "Azure-hosted FLUX.1.1 Pro - 1024x1024",
                    "deployment_name": "FLUX-1.1-pro"
                }
            },
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": (1024, 1024)}
            ],
            "quality_levels": [
                {"id": "standard", "name": "Standard", "description": "Good quality"},
                {"id": "high", "name": "High", "description": "Better quality"}
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
    
    def _map_to_flux_aspect_ratio(self, width: int, height: int) -> str:
        """Map calculated dimensions to nearest supported FLUX aspect ratio"""
        if height == 0:
            return "1:1"
        
        ratio = width / height
        
        # Define supported aspect ratios with their decimal values
        supported_ratios = {
            "21:9": 21/9,    # 2.333
            "16:9": 16/9,    # 1.778
            "3:2": 3/2,      # 1.5
            "4:3": 4/3,      # 1.333
            "5:4": 5/4,      # 1.25
            "1:1": 1.0,      # 1.0
            "4:5": 4/5,      # 0.8
            "3:4": 3/4,      # 0.75
            "2:3": 2/3,      # 0.667
            "9:16": 9/16,    # 0.562
            "9:21": 9/21     # 0.429
        }
        
        # Find the closest supported aspect ratio
        closest_ratio = min(supported_ratios.items(), key=lambda x: abs(x[1] - ratio))
        
        print(f"[REPLICATE] Mapped {width}x{height} (ratio {ratio:.3f}) to {closest_ratio[0]} (ratio {closest_ratio[1]:.3f})")
        return closest_ratio[0]
    
    async def generate_with_replicate(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Replicate API"""
        if "replicate-api" not in self.api_keys:
            raise ValueError("API key required for Replicate")
        
        print(f"[REPLICATE] Replicate generation with {prompt[:100]}...")
        
        try:
            # Set the API token
            os.environ["REPLICATE_API_TOKEN"] = self.api_keys["replicate-api"]
            
            # Get parameters
            width = kwargs.get("width", 1024)
            height = kwargs.get("height", 1024)
            steps = kwargs.get("num_inference_steps", 25)
            guidance_scale = kwargs.get("guidance_scale", 7.5)
            negative_prompt = kwargs.get("negative_prompt", "")
            
            # Choose model - default to FLUX Schnell (fastest)
            model = kwargs.get("replicate_model", "black-forest-labs/flux-schnell")
            
            print(f"[REPLICATE] Using model: {model}")
            print(f"[REPLICATE] Available models: black-forest-labs/flux-schnell, stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b, stability-ai/sdxl-turbo, ideogram-ai/ideogram-v3-turbo, google/nano-banana-pro, lucataco/realistic-v5.1, ai-forever/kandinsky-2.2")
            print(f"[REPLICATE] Parameters: {width}x{height}, steps={steps}, guidance={guidance_scale}")
            print(f"[REPLICATE] Requested dimensions: width={width}, height={height}")
            print(f"[REPLICATE] Aspect ratio: {width/height if height != 0 else 'N/A'}")
            
            # Special handling for FLUX 1.1 Pro - it might not exist or have different name
            if model == "black-forest-labs/flux-1.1-pro":
                print(f"[REPLICATE] FLUX 1.1 Pro requested, but this model might not exist or have fixed aspect ratio.")
                print(f"[REPLICATE] Checking if custom aspect ratio is requested...")
                
                # Check if custom aspect ratio (not 1:1) is requested
                aspect_ratio = width / height if height != 0 else 1.0
                print(f"[REPLICATE] Requested aspect ratio: {aspect_ratio:.2f}")
                
                if abs(aspect_ratio - 1.0) > 0.1:  # Not close to 1:1
                    print(f"[REPLICATE] Custom aspect ratio detected, falling back to FLUX Schnell for better aspect ratio support.")
                    model = "black-forest-labs/flux-schnell"
                    print(f"[REPLICATE] Using fallback model: {model}")
                else:
                    print(f"[REPLICATE] Using FLUX 1.1 Pro with square aspect ratio")
                # Continue with FLUX 1.1 Pro processing below
            
            # Special handling for Nano Banana Pro - check if it exists
            if model == "google/nano-banana-pro":
                print(f"[REPLICATE] Nano Banana Pro requested - trying text-to-image generation...")
                # Continue with Nano Banana Pro processing below
            
            # Run Replicate model
            if model == "black-forest-labs/flux-schnell":
                # FLUX Schnell - fastest model, 1-4 steps
                print(f"[REPLICATE] Running FLUX Schnell with dimensions: {width}x{height}")
                
                # Map calculated dimensions to nearest supported aspect ratio
                aspect_ratio_value = self._map_to_flux_aspect_ratio(width, height)
                print(f"[REPLICATE] Using aspect ratio: {aspect_ratio_value}")
                
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio_value,  # Use supported aspect ratio
                        "num_inference_steps": min(steps, 4),  # FLUX Schnell only needs 1-4 steps
                        "guidance_scale": guidance_scale,
                        "num_outputs": 1,
                        "go_fast": True  # Use optimized version
                    }
                )
                
                # Handle the output (replicate.run returns a list)
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                    print(f"[REPLICATE] FLUX Schnell returned list: {image_url}")
                else:
                    raise ValueError("No image URL found in Replicate output")
                
            elif model == "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b":
                # Stable Diffusion XL
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "num_inference_steps": steps,
                        "guidance_scale": guidance_scale,
                        "negative_prompt": negative_prompt or "",
                        "num_outputs": 1
                    }
                )
                
                # Handle the output
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                    print(f"[REPLICATE] SDXL returned list: {image_url}")
                else:
                    raise ValueError("No image URL found in Replicate output")
                
            elif model == "black-forest-labs/flux-1.1-pro":
                # FLUX 1.1 Pro - most powerful
                print(f"[REPLICATE] Running FLUX 1.1 Pro with dimensions: {width}x{height}")
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "num_inference_steps": steps,
                        "guidance_scale": guidance_scale,
                        "negative_prompt": negative_prompt or "",
                        "num_outputs": 1
                    }
                )
                
                print(f"[REPLICATE] FLUX 1.1 Pro run completed")
                print(f"[REPLICATE] Output type: {type(output)}")
                print(f"[REPLICATE] Output content: {output}")
                
                # Handle the output
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                    print(f"[REPLICATE] FLUX 1.1 Pro returned list: {image_url}")
                    
                    # Check if the returned image has the correct dimensions
                    try:
                        response = requests.get(image_url, timeout=30)
                        response.raise_for_status()
                        image = Image.open(io.BytesIO(response.content))
                        print(f"[REPLICATE] FLUX 1.1 Pro actual image size: {image.size}")
                        print(f"[REPLICATE] Requested: {width}x{height}, Got: {image.size[0]}x{image.size[1]}")
                        
                        if image.size[0] != width or image.size[1] != height:
                            print(f"[WARNING] FLUX 1.1 Pro ignored dimensions! Model may have fixed aspect ratio.")
                            print(f"[WARNING] Try using FLUX Schnell instead for custom aspect ratios.")
                        
                        return image
                    except Exception as img_error:
                        print(f"[ERROR] Failed to check FLUX 1.1 Pro image dimensions: {img_error}")
                        raise ValueError("Failed to process FLUX 1.1 Pro image")
                        
                else:
                    raise ValueError("No image URL found in FLUX 1.1 Pro output")
                
            elif model == "ideogram-ai/ideogram-v3-turbo":
                # Ideogram V3 Turbo - excellent for text
                print(f"[REPLICATE] Running Ideogram V3 Turbo...")
                try:
                    output = replicate.run(
                        model,
                        input={
                            "prompt": prompt,
                            "width": width,
                            "height": height,
                            "num_inference_steps": steps,
                            "guidance_scale": guidance_scale,
                            "negative_prompt": negative_prompt or "",
                            "num_outputs": 1
                        }
                    )
                    
                    print(f"[REPLICATE] Ideogram V3 Turbo run completed")
                    print(f"[REPLICATE] Output type: {type(output)}")
                    print(f"[REPLICATE] Output content: {output}")
                    
                    # Handle the output with enhanced debugging and FileOutput support
                    if isinstance(output, list) and len(output) > 0:
                        first_item = output[0]
                        if isinstance(first_item, str) and first_item.startswith('http'):
                            # URL returned
                            image_url = first_item
                            print(f"[REPLICATE] Ideogram V3 Turbo returned list with URL: {image_url}")
                        elif hasattr(first_item, 'read'):
                            # FileOutput object from official Replicate client
                            print(f"[REPLICATE] FileOutput detected, using read() method")
                            image_data = first_item.read()
                            print(f"[REPLICATE] Read {len(image_data)} bytes from FileOutput")
                            
                            if len(image_data) < 100:
                                print(f"[ERROR] FileOutput data too small: {len(image_data)} bytes, likely corrupted")
                                raise ValueError(f"Ideogram V3 Turbo returned corrupted FileOutput: {len(image_data)} bytes")
                            
                            try:
                                image = Image.open(io.BytesIO(image_data))
                                print(f"[REPLICATE] Ideogram V3 Turbo image loaded from FileOutput: {image.size}")
                                return image
                            except Exception as img_error:
                                print(f"[ERROR] Failed to load image from FileOutput: {img_error}")
                                raise ValueError(f"Failed to load Ideogram V3 Turbo image from FileOutput: {img_error}")
                        elif isinstance(first_item, bytes):
                            # Binary image data returned directly
                            print(f"[REPLICATE] Ideogram V3 Turbo returned binary image data directly")
                            print(f"[REPLICATE] Binary data length: {len(first_item)} bytes")
                            print(f"[REPLICATE] Binary data preview: {first_item[:50]}...")
                            
                            if len(first_item) < 100:
                                print(f"[ERROR] Binary data too small: {len(first_item)} bytes, likely corrupted")
                                raise ValueError(f"Ideogram V3 Turbo returned corrupted binary data: {len(first_item)} bytes")
                            
                            try:
                                image = Image.open(io.BytesIO(first_item))
                                print(f"[REPLICATE] Ideogram V3 Turbo image loaded directly: {image.size}")
                                return image
                            except Exception as img_error:
                                print(f"[ERROR] Failed to load image from binary data: {img_error}")
                                raise ValueError(f"Failed to load Ideogram V3 Turbo image: {img_error}")
                        else:
                            print(f"[REPLICATE] Ideogram V3 Turbo returned list with non-URL: {first_item}")
                            raise ValueError(f"Ideogram V3 Turbo returned unexpected list item: {type(first_item)}")
                    elif isinstance(output, str):
                        if output.startswith('http'):
                            # URL returned
                            image_url = output
                            print(f"[REPLICATE] Ideogram V3 Turbo returned string URL: {image_url}")
                        elif hasattr(output, 'read'):
                            # FileOutput object from official Replicate client
                            print(f"[REPLICATE] FileOutput detected (single), using read() method")
                            image_data = output.read()
                            print(f"[REPLICATE] Read {len(image_data)} bytes from FileOutput")
                            
                            if len(image_data) < 100:
                                print(f"[ERROR] FileOutput data too small: {len(image_data)} bytes, likely corrupted")
                                raise ValueError(f"Ideogram V3 Turbo returned corrupted FileOutput: {len(image_data)} bytes")
                            
                            try:
                                image = Image.open(io.BytesIO(image_data))
                                print(f"[REPLICATE] Ideogram V3 Turbo image loaded from FileOutput: {image.size}")
                                return image
                            except Exception as img_error:
                                print(f"[ERROR] Failed to load image from FileOutput: {img_error}")
                                raise ValueError(f"Failed to load Ideogram V3 Turbo image from FileOutput: {img_error}")
                        elif output.startswith('\x89') or len(output) > 1000:
                            # Binary image data returned directly (PNG signature or large binary)
                            print(f"[REPLICATE] Ideogram V3 Turbo returned binary string")
                            print(f"[REPLICATE] Binary data length: {len(output)} bytes")
                            print(f"[REPLICATE] Binary data preview: {output[:50]}...")
                            
                            try:
                                image = Image.open(io.BytesIO(output.encode('latin-1')))
                                print(f"[REPLICATE] Ideogram V3 Turbo image loaded from string: {image.size}")
                                return image
                            except Exception as img_error:
                                print(f"[ERROR] Failed to load image from binary string: {img_error}")
                                raise ValueError(f"Failed to load Ideogram V3 Turbo image from string: {img_error}")
                        else:
                            print(f"[REPLICATE] Ideogram V3 Turbo returned string but not URL: {output}")
                            raise ValueError(f"Ideogram V3 Turbo returned non-URL string: {output}")
                    elif isinstance(output, bytes):
                        # Binary image data returned directly
                        print(f"[REPLICATE] Ideogram V3 Turbo returned binary image directly")
                        print(f"[REPLICATE] Binary data length: {len(output)} bytes")
                        print(f"[REPLICATE] Binary data preview: {output[:50]}...")
                        
                        if len(output) < 100:
                            print(f"[ERROR] Binary data too small: {len(output)} bytes, likely corrupted")
                            raise ValueError(f"Ideogram V3 Turbo returned corrupted binary data: {len(output)} bytes")
                        
                        try:
                            image = Image.open(io.BytesIO(output))
                            print(f"[REPLICATE] Ideogram V3 Turbo image loaded: {image.size}")
                            return image
                        except Exception as img_error:
                            print(f"[ERROR] Failed to load image from binary data: {img_error}")
                            raise ValueError(f"Failed to load Ideogram V3 Turbo image: {img_error}")
                    elif hasattr(output, 'read'):
                        # FileOutput object from official Replicate client (direct)
                        print(f"[REPLICATE] FileOutput detected (direct), using read() method")
                        image_data = output.read()
                        print(f"[REPLICATE] Read {len(image_data)} bytes from FileOutput")
                        
                        if len(image_data) < 100:
                            print(f"[ERROR] FileOutput data too small: {len(image_data)} bytes, likely corrupted")
                            raise ValueError(f"Ideogram V3 Turbo returned corrupted FileOutput: {len(image_data)} bytes")
                        
                        try:
                            image = Image.open(io.BytesIO(image_data))
                            print(f"[REPLICATE] Ideogram V3 Turbo image loaded from direct FileOutput: {image.size}")
                            return image
                        except Exception as img_error:
                            print(f"[ERROR] Failed to load image from direct FileOutput: {img_error}")
                            raise ValueError(f"Failed to load Ideogram V3 Turbo image from direct FileOutput: {img_error}")
                    elif hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
                        print(f"[REPLICATE] Ideogram V3 Turbo returned iterator, collecting...")
                        output_list = []
                        try:
                            for item in output:
                                output_list.append(item)
                                break
                            if len(output_list) > 0:
                                first_item = output_list[0]
                                if isinstance(first_item, str) and first_item.startswith('http'):
                                    image_url = first_item
                                    print(f"[REPLICATE] Ideogram V3 Turbo iterator collected URL: {image_url}")
                                elif isinstance(first_item, bytes):
                                    print(f"[REPLICATE] Ideogram V3 Turbo iterator collected binary: {len(first_item)} bytes")
                                    try:
                                        image = Image.open(io.BytesIO(first_item))
                                        print(f"[REPLICATE] Ideogram V3 Turbo iterator image loaded: {image.size}")
                                        return image
                                    except Exception as img_error:
                                        print(f"[ERROR] Failed to load Ideogram V3 Turbo iterator image: {img_error}")
                                        raise ValueError(f"Failed to load Ideogram V3 Turbo iterator image: {img_error}")
                                else:
                                    print(f"[REPLICATE] Ideogram V3 Turbo iterator collected unexpected: {type(first_item)}")
                                    raise ValueError(f"Ideogram V3 Turbo iterator returned unexpected type: {type(first_item)}")
                        except Exception as e:
                            print(f"[ERROR] Failed to iterate Ideogram V3 Turbo output: {e}")
                            raise ValueError("Failed to collect Ideogram V3 Turbo iterator output")
                    else:
                        print(f"[REPLICATE] Ideogram V3 Turbo unexpected output: {type(output)}")
                        print(f"[REPLICATE] Ideogram V3 Turbo output content: {output}")
                        raise ValueError(f"Invalid Ideogram V3 Turbo output format: {type(output)}")
                        
                except Exception as e:
                    print(f"[ERROR] Ideogram V3 Turbo generation failed: {e}")
                    print(f"[ERROR] Exception type: {type(e)}")
                    print(f"[ERROR] Exception details: {str(e)}")
                    # Fall back to FLUX Schnell if Ideogram V3 Turbo fails
                    print(f"[REPLICATE] Falling back to FLUX Schnell due to Ideogram V3 Turbo error...")
                    model = "black-forest-labs/flux-schnell"
                    print(f"[REPLICATE] Using fallback model: {model}")
                    # Continue with FLUX Schnell processing below
                
            elif model == "google/nano-banana-pro":
                # Nano Banana Pro - Google's model (text-to-image generation)
                print(f"[REPLICATE] Running Nano Banana Pro for text-to-image generation...")
                try:
                    # Try with minimal parameters first
                    output = replicate.run(
                        model,
                        input={
                            "prompt": prompt,
                            "num_outputs": 1
                        }
                    )
                    
                    print(f"[REPLICATE] Nano Banana Pro run completed successfully")
                    print(f"[REPLICATE] Output type: {type(output)}")
                    print(f"[REPLICATE] Output content preview: {str(output)[:100]}...")
                    
                    # Handle the output - Nano Banana Pro might return URLs or binary data
                    if isinstance(output, list) and len(output) > 0:
                        first_item = output[0]
                        print(f"[REPLICATE] Nano Banana Pro returned list with {len(output)} items")
                        print(f"[REPLICATE] First item type: {type(first_item)}")
                        
                        if isinstance(first_item, str) and first_item.startswith('http'):
                            # URL returned
                            image_url = first_item
                            print(f"[REPLICATE] Nano Banana Pro returned URL: {image_url}")
                            response = requests.get(image_url, timeout=30)
                            response.raise_for_status()
                            print(f"[REPLICATE] Downloaded {len(response.content)} bytes from URL")
                            image = Image.open(io.BytesIO(response.content))
                            print(f"[REPLICATE] Nano Banana Pro image downloaded: {image.size}")
                            return image
                        elif isinstance(first_item, bytes):
                            # Binary image data returned directly
                            print(f"[REPLICATE] Nano Banana Pro returned binary image data directly")
                            print(f"[REPLICATE] Binary data length: {len(first_item)} bytes")
                            print(f"[REPLICATE] Binary data preview: {first_item[:50]}...")
                            
                            if len(first_item) < 100:
                                print(f"[ERROR] Binary data too small: {len(first_item)} bytes, likely corrupted")
                                raise ValueError(f"Nano Banana Pro returned corrupted binary data: {len(first_item)} bytes")
                            
                            try:
                                image = Image.open(io.BytesIO(first_item))
                                print(f"[REPLICATE] Nano Banana Pro image loaded directly: {image.size}")
                                return image
                            except Exception as img_error:
                                print(f"[ERROR] Failed to load image from binary data: {img_error}")
                                raise ValueError(f"Failed to load Nano Banana Pro image: {img_error}")
                        else:
                            print(f"[REPLICATE] Nano Banana Pro returned unexpected item: {first_item}")
                            raise ValueError(f"Nano Banana Pro returned unexpected item type: {type(first_item)}")
                    elif isinstance(output, str):
                        # Single URL returned
                        if output.startswith('http'):
                            image_url = output
                            print(f"[REPLICATE] Nano Banana Pro returned single URL: {image_url}")
                            response = requests.get(image_url, timeout=30)
                            response.raise_for_status()
                            print(f"[REPLICATE] Downloaded {len(response.content)} bytes from URL")
                            image = Image.open(io.BytesIO(response.content))
                            print(f"[REPLICATE] Nano Banana Pro image downloaded: {image.size}")
                            return image
                        else:
                            print(f"[REPLICATE] Nano Banana Pro returned string but not URL: {output}")
                            raise ValueError(f"Nano Banana Pro returned non-URL string: {output}")
                    else:
                        print(f"[REPLICATE] Nano Banana Pro returned: {output}")
                        print(f"[REPLICATE] Output type: {type(output)}")
                        raise ValueError(f"Nano Banana Pro returned unexpected format: {type(output)}")
                            
                except Exception as e:
                    print(f"[ERROR] Nano Banana Pro generation failed: {e}")
                    print(f"[ERROR] Exception type: {type(e)}")
                    print(f"[ERROR] Exception details: {str(e)}")
                    # Fall back to FLUX Schnell if Nano Banana Pro fails
                    print(f"[REPLICATE] Falling back to FLUX Schnell due to Nano Banana Pro error...")
                    model = "black-forest-labs/flux-schnell"
                    print(f"[REPLICATE] Using fallback model: {model}")
                    # Continue with FLUX Schnell processing below
                
            elif model == "jyoung105/sdxl-turbo:93c488b9fbd6bea622d354c8dcce2724c5f67adb92ccf909038042a21c5238a7":
                # SDXL Turbo
                output = replicate.run(
                    "jyoung105/sdxl-turbo:93c488b9fbd6bea622d354c8dcce2724c5f67adb92ccf909038042a21c5238a7",
                    input={
                        "prompt": prompt,
                        "width": min(width, 1024),
                        "height": min(height, 1024),
                        "num_inference_steps": min(steps, 10),  # Turbo uses fewer steps
                        "guidance_scale": guidance_scale,
                        "num_outputs": 1
                    }
                )
                
                # Handle the output
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                    print(f"[REPLICATE] SDXL Turbo returned list: {image_url}")
                else:
                    raise ValueError("No image URL found in Replicate output")
                
            elif model == "lucataco/realistic-vision-v5.1:2c8e954decbf70b7607a4414e5785ef9e4de4b8c51d50fb8b8b349160e0ef6bb":
                # Realistic Vision
                print(f"[REPLICATE] Running Realistic Vision v5.1...")
                output = replicate.run(
                    "lucataco/realistic-vision-v5.1:2c8e954decbf70b7607a4414e5785ef9e4de4b8c51d50fb8b8b349160e0ef6bb",
                    input={
                        "prompt": prompt,
                        "negative_prompt": negative_prompt if negative_prompt else "deformed, disfigured, poor details, low quality",
                        "width": width,
                        "height": height,
                        "num_inference_steps": steps,
                        "guidance_scale": guidance_scale,
                        "num_outputs": 1
                    }
                )
                
                print(f"[REPLICATE] Realistic Vision run completed")
                print(f"[REPLICATE] Output type: {type(output)}")
                print(f"[REPLICATE] Output content: {output}")
                
                # Handle the output with enhanced debugging and binary data support
                if isinstance(output, list) and len(output) > 0:
                    first_item = output[0]
                    if isinstance(first_item, str) and first_item.startswith('http'):
                        # URL returned
                        image_url = first_item
                        print(f"[REPLICATE] Realistic Vision returned list with URL: {image_url}")
                    elif isinstance(first_item, bytes):
                        # Binary image data returned directly
                        print(f"[REPLICATE] Realistic Vision returned binary image data directly")
                        print(f"[REPLICATE] Binary data length: {len(first_item)} bytes")
                        print(f"[REPLICATE] Binary data preview: {first_item[:50]}...")
                        
                        if len(first_item) < 100:
                            print(f"[ERROR] Binary data too small: {len(first_item)} bytes, likely corrupted")
                            raise ValueError(f"Realistic Vision returned corrupted binary data: {len(first_item)} bytes")
                        
                        try:
                            image = Image.open(io.BytesIO(first_item))
                            print(f"[REPLICATE] Realistic Vision image loaded directly: {image.size}")
                            return image
                        except Exception as img_error:
                            print(f"[ERROR] Failed to load image from binary data: {img_error}")
                            raise ValueError(f"Failed to load Realistic Vision image: {img_error}")
                    else:
                        print(f"[REPLICATE] Realistic Vision returned list with non-URL: {first_item}")
                        raise ValueError(f"Realistic Vision returned unexpected list item: {type(first_item)}")
                elif isinstance(output, str):
                    if output.startswith('http'):
                        # URL returned
                        image_url = output
                        print(f"[REPLICATE] Realistic Vision returned string URL: {image_url}")
                    elif output.startswith('\x89') or len(output) > 1000:
                        # Binary image data returned directly (PNG signature or large binary)
                        print(f"[REPLICATE] Realistic Vision returned binary string")
                        print(f"[REPLICATE] Binary data length: {len(output)} bytes")
                        print(f"[REPLICATE] Binary data preview: {output[:50]}...")
                        
                        try:
                            image = Image.open(io.BytesIO(output.encode('latin-1')))
                            print(f"[REPLICATE] Realistic Vision image loaded from string: {image.size}")
                            return image
                        except Exception as img_error:
                            print(f"[ERROR] Failed to load image from binary string: {img_error}")
                            raise ValueError(f"Failed to load Realistic Vision image from string: {img_error}")
                    else:
                        print(f"[REPLICATE] Realistic Vision returned string but not URL: {output}")
                        raise ValueError(f"Realistic Vision returned non-URL string: {output}")
                elif isinstance(output, bytes):
                    # Binary image data returned directly
                    print(f"[REPLICATE] Realistic Vision returned binary image directly")
                    print(f"[REPLICATE] Binary data length: {len(output)} bytes")
                    print(f"[REPLICATE] Binary data preview: {output[:50]}...")
                    
                    if len(output) < 100:
                        print(f"[ERROR] Binary data too small: {len(output)} bytes, likely corrupted")
                        raise ValueError(f"Realistic Vision returned corrupted binary data: {len(output)} bytes")
                    
                    try:
                        image = Image.open(io.BytesIO(output))
                        print(f"[REPLICATE] Realistic Vision image loaded: {image.size}")
                        return image
                    except Exception as img_error:
                        print(f"[ERROR] Failed to load image from binary data: {img_error}")
                        raise ValueError(f"Failed to load Realistic Vision image: {img_error}")
                elif hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
                    print(f"[REPLICATE] Realistic Vision returned iterator, collecting...")
                    output_list = []
                    try:
                        for item in output:
                            output_list.append(item)
                            break
                        if len(output_list) > 0:
                            first_item = output_list[0]
                            if isinstance(first_item, str) and first_item.startswith('http'):
                                image_url = first_item
                                print(f"[REPLICATE] Realistic Vision iterator collected URL: {image_url}")
                            elif isinstance(first_item, bytes):
                                print(f"[REPLICATE] Realistic Vision iterator collected binary: {len(first_item)} bytes")
                                try:
                                    image = Image.open(io.BytesIO(first_item))
                                    print(f"[REPLICATE] Realistic Vision iterator image loaded: {image.size}")
                                    return image
                                except Exception as img_error:
                                    print(f"[ERROR] Failed to load Realistic Vision iterator image: {img_error}")
                                    raise ValueError(f"Failed to load Realistic Vision iterator image: {img_error}")
                            else:
                                print(f"[REPLICATE] Realistic Vision iterator collected unexpected: {type(first_item)}")
                                raise ValueError(f"Realistic Vision iterator returned unexpected type: {type(first_item)}")
                    except Exception as e:
                        print(f"[ERROR] Failed to iterate Realistic Vision output: {e}")
                        raise ValueError("Failed to collect Realistic Vision iterator output")
                else:
                    print(f"[REPLICATE] Realistic Vision unexpected output: {type(output)}")
                    print(f"[REPLICATE] Realistic Vision output content: {output}")
                    raise ValueError(f"Invalid Realistic Vision output format: {type(output)}")
                
                if not image_url and 'image' not in locals():
                    print(f"[ERROR] No image URL or image found in Realistic Vision output!")
                    raise ValueError("No image URL found in Realistic Vision output")
                
            elif model == "ai-forever/kandinsky-2.2":
                # Kandinsky
                output = replicate.run(
                    "ai-forever/kandinsky-2.2",
                    input={
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "num_inference_steps": steps,
                        "num_outputs": 1
                    }
                )
                
                # Handle the output
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                    print(f"[REPLICATE] Kandinsky returned list: {image_url}")
                else:
                    raise ValueError("No image URL found in Replicate output")
                
            else:
                # Try to run with the provided model name directly
                try:
                    output = replicate.run(
                        model,
                        input={
                            "prompt": prompt,
                            "width": width,
                            "height": height,
                            "num_inference_steps": steps,
                            "guidance_scale": guidance_scale,
                            "negative_prompt": negative_prompt or "",
                            "num_outputs": 1
                        }
                    )
                    
                    # Handle the output
                    if isinstance(output, list) and len(output) > 0:
                        image_url = output[0]
                        print(f"[REPLICATE] Direct model returned list: {image_url}")
                    else:
                        raise ValueError(f"No image URL found in Replicate output")
                        
                except Exception as e:
                    print(f"[ERROR] Failed to run model {model}: {e}")
                    raise ValueError(f"Unsupported Replicate model: {model}")
            
            print(f"[REPLICATE] Generation completed!")
            print(f"[REPLICATE] Output type: {type(output)}")
            print(f"[REPLICATE] Output content: {output}")
            print(f"[REPLICATE] Output length: {len(output) if hasattr(output, '__len__') else 'N/A'}")
            
            # Debug: Try to inspect the output more thoroughly
            if hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
                print(f"[REPLICATE] Output is iterable, converting to list for inspection...")
                try:
                    output_list = list(output)
                    print(f"[REPLICATE] Converted to list: {output_list}")
                    print(f"[REPLICATE] List length: {len(output_list)}")
                    if len(output_list) > 0:
                        print(f"[REPLICATE] First item type: {type(output_list[0])}")
                        print(f"[REPLICATE] First item: {output_list[0]}")
                except Exception as e:
                    print(f"[ERROR] Failed to convert output to list: {e}")
            
            # Handle both direct output and iterator output
            image_url = None
            if isinstance(output, list) and len(output) > 0:
                # Direct output format
                image_url = output[0]
                print(f"[REPLICATE] Direct list output: {image_url}")
            elif hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
                # Iterator output (streaming) - need to iterate through it
                print(f"[REPLICATE] Iterator output detected, collecting results...")
                output_list = []
                try:
                    # Iterate through the async generator
                    async for item in output:
                        output_list.append(item)
                        print(f"[REPLICATE] Iterator item: {item}")
                        # Break after first item for image generation
                        break
                    if len(output_list) > 0:
                        image_url = output_list[0]
                        print(f"[REPLICATE] Iterator collected: {image_url}")
                except Exception as e:
                    print(f"[ERROR] Failed to iterate over output: {e}")
                    raise ValueError("Failed to collect iterator output")
            elif isinstance(output, str):
                # Direct URL string
                image_url = output
                print(f"[REPLICATE] Direct URL output: {image_url}")
            else:
                print(f"[REPLICATE] Unexpected output format: {type(output)}")
                print(f"[REPLICATE] Output content: {output}")
                print(f"[REPLICATE] Output dir(): {dir(output) if hasattr(output, '__dir__') else 'N/A'}")
                raise ValueError(f"Invalid output format from Replicate: {type(output)}")
            
            if not image_url:
                print(f"[ERROR] No image URL found in Replicate output!")
                print(f"[ERROR] Output was: {output}")
                print(f"[ERROR] Output type: {type(output)}")
                raise ValueError("No image URL found in Replicate output")
            
            # Download the image
            print(f"[REPLICATE] Downloading image from: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            print(f"[REPLICATE] Response status: {response.status_code}")
            print(f"[REPLICATE] Response content length: {len(response.content)}")
            
            if len(response.content) == 0:
                raise ValueError("Empty image response from Replicate")
            
            image = Image.open(io.BytesIO(response.content))
            print(f"[REPLICATE] Image size: {image.size}")
            print(f"[REPLICATE] Image downloaded successfully!")
            return image
                
        except Exception as e:
            print(f"[ERROR] Replicate generation failed: {e}")
            raise
    
    async def generate_with_kandinsky(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Kandinsky 2.2 on Replicate"""
        if "replicate-api" not in self.api_keys:
            raise ValueError("API key required for Replicate")
        
        print(f"[KANDINSKY] Kandinsky generation with {prompt[:100]}...")
        
        try:
            os.environ["REPLICATE_API_TOKEN"] = self.api_keys["replicate-api"]
            
            width = kwargs.get("width", 512)
            height = kwargs.get("height", 512)
            steps = kwargs.get("num_inference_steps", 50)
            
            output = await replicate.run(
                "ai-forever/kandinsky-2.2",
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": steps,
                    "num_outputs": 1
                }
            )
            
            if isinstance(output, list) and len(output) > 0:
                image_url = output[0]
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                print(f"[KANDINSKY] Image generated successfully!")
                return image
            else:
                raise ValueError("Invalid output format from Kandinsky")
                
        except Exception as e:
            print(f"[ERROR] Kandinsky generation failed: {e}")
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
        model_key = kwargs.get("leonardo_model", kwargs.get("model", "phoenix-1-0"))
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        width = kwargs.get("width", None)
        height = kwargs.get("height", None)
        
        print(f"[SEARCH] Model key: {model_key}")
        print(f"[SEARCH] Aspect ratio: {aspect_ratio}")
        print(f"[SEARCH] Width: {width}, Height: {height}")
        
        # Get model info
        generator_info = self.available_generators["leonardo-api"]
        models = generator_info["models"]
        
        print(f"[SEARCH] Available models: {list(models.keys())}")
        
        if model_key not in models:
            raise ValueError(f"Model {model_key} not available for Leonardo.ai")
        
        model_info = models[model_key]
        print(f"[SEARCH] Selected model: {model_info['name']} (ID: {model_info['id']})")
        
        # Get API version for this model
        api_version = model_info.get("api_version", "v1")
        print(f"[SEARCH] API version: {api_version}")
        
        # Get resolution from aspect ratio or use provided dimensions
        if width and height:
            # Use dimensions provided by frontend (already calculated)
            print(f"[SEARCH] Using frontend dimensions: {width}x{height}")
            
            # Check if dimensions exceed model's maximum resolution
            max_width, max_height = model_info["max_resolution"]
            if width > max_width or height > max_height:
                print(f"[SEARCH] Dimensions exceed model max resolution {max_width}x{max_height}")
                # Scale down to fit within max resolution while maintaining aspect ratio
                scale_factor = min(max_width / width, max_height / height)
                width = int(width * scale_factor)
                height = int(height * scale_factor)
                print(f"[SEARCH] Scaled down to: {width}x{height}")
            
            # Round dimensions to nearest multiple of 8 (required by most models)
            width = max(8, (width // 8) * 8)
            height = max(8, (height // 8) * 8)
            print(f"[SEARCH] Final dimensions (rounded to 8): {width}x{height}")
        else:
            # Fallback to aspect ratio calculation
            aspect_ratios = {ar["id"]: ar for ar in generator_info["aspect_ratios"]}
            if aspect_ratio not in aspect_ratios:
                aspect_ratio = "1:1"  # Default fallback
            
            resolution = aspect_ratios[aspect_ratio]["resolution"]
            width, height = resolution
            print(f"[SEARCH] Using aspect ratio fallback: {aspect_ratio} -> {width}x{height}")
            
            # Check if dimensions exceed model's maximum resolution
            max_width, max_height = model_info["max_resolution"]
            if width > max_width or height > max_height:
                print(f"[SEARCH] Dimensions exceed model max resolution {max_width}x{max_height}")
                # Scale down to fit within max resolution while maintaining aspect ratio
                scale_factor = min(max_width / width, max_height / height)
                width = int(width * scale_factor)
                height = int(height * scale_factor)
                print(f"[SEARCH] Scaled down to: {width}x{height}")
            
            # Round dimensions to nearest multiple of 8 (required by most models)
            width = max(8, (width // 8) * 8)
            height = max(8, (height // 8) * 8)
            print(f"[SEARCH] Fallback final dimensions (rounded to 8): {width}x{height}")
                    
        # Build generation payload based on API version
        if api_version == "v2":
            # V2 API format
            model_name = model_key.replace("-", ".").replace("_", "-")
            
            # Special handling for specific models
            if model_key == "flux-2-pro":
                model_name = "flux-pro-2.0"
            elif model_key == "gpt-image-1-5":
                model_name = "gpt-image-1.5"
            elif model_key == "ideogram-3-0":
                model_name = "ideogram-v3.0"
            elif model_key == "seedream-4-0":
                model_name = "seedream-4.0"
            elif model_key == "seedream-4-5":
                model_name = "seedream-4.5"
            elif model_key == "nano-banana":
                model_name = "gemini-2.5-flash-image"
            elif model_key == "nano-banana-pro":
                model_name = "gemini-image-2"
            
            # Build V2 payload - seed must NOT be included if not set (null causes validation errors)
            v2_params = {
                "prompt": enhanced_prompt,
                "width": width,
                "height": height,
                "quantity": 1,
                "prompt_enhance": "OFF",
                "style_ids": ["111dc692-d470-4eec-b791-3475abac4c46"]
            }
            seed_val = kwargs.get("seed", -1)
            if seed_val and seed_val != -1:
                v2_params["seed"] = seed_val
            
            generation_payload = {
                "public": False,
                "model": model_name,
                "parameters": v2_params
            }
            print(f"[V2] Payload for {model_key}: model={model_name}, width={width}, height={height}, seed included={seed_val != -1}")
            # Model-specific V2 overrides
            if model_key in ["nano-banana-pro", "nano-banana"]:
                if "seed" in generation_payload["parameters"]:
                    del generation_payload["parameters"]["seed"]
                if model_key == "nano-banana-pro":
                    # Nano Banana Pro only supports 1024x1024
                    generation_payload["parameters"]["width"] = 1024
                    generation_payload["parameters"]["height"] = 1024
            elif model_key == "flux-2-pro":
                # FLUX.2 Pro requires exact dimensions per official documentation
                flux2_dimensions = {
                    "1:1": (1440, 1440),
                    "16:9": (1440, 810),
                    "9:16": (810, 1440),
                    "2:3": (960, 1440),
                }
                if aspect_ratio in flux2_dimensions:
                    w, h = flux2_dimensions[aspect_ratio]
                else:
                    w, h = 1440, 1440
                generation_payload["parameters"]["width"] = w
                generation_payload["parameters"]["height"] = h
                print(f"[V2] FLUX.2 Pro official dimensions: {w}x{h} for {aspect_ratio}")
            elif model_key == "gpt-image-1-5":
                generation_payload["parameters"]["mode"] = "QUALITY"
            elif model_key == "ideogram-3-0":
                generation_payload["parameters"]["mode"] = "TURBO"
            elif model_key in ["seedream-4-0", "seedream-4-5"]:
                generation_payload["parameters"]["guidances"] = {
                    "image_reference": []
                }
            
            # Use V2 endpoint
            api_endpoint = "https://cloud.leonardo.ai/api/rest/v2/generations"
            
        else:
            # V1 API format
            generation_payload = {
                "prompt": enhanced_prompt,  # Use enhanced prompt
                "width": width,
                "height": height,
                "num_images": 1,
                "alchemy": True,  # Use alchemy for Phoenix models (quality mode)
                "ultra": False,    # Ultra not needed for Phoenix
                "contrast": 3.5,   # Standard contrast for Phoenix
                "negative_prompt": self._get_optimized_negative_prompt(kwargs.get("negative_prompt", "")),
                "num_inference_steps": kwargs.get("num_inference_steps", 25),  # Phoenix needs fewer steps
                "guidance_scale": kwargs.get("guidance_scale", 7.0)   # Phoenix works well with lower guidance
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
            
            # Add styleUUID for FLUX models
            if model_key in ["flux-dev", "flux-schnell"]:
                generation_payload["styleUUID"] = "111dc692-d470-4eec-b791-3475abac4c46"
                generation_payload["enhancePrompt"] = False
                generation_payload["contrast"] = 3.5
                # For FLUX models, use num_images instead of alchemy
                generation_payload["num_images"] = 1
                # Remove alchemy for FLUX models
                if "alchemy" in generation_payload:
                    del generation_payload["alchemy"]
                if "ultra" in generation_payload:
                    del generation_payload["ultra"]
                if "negative_prompt" in generation_payload:
                    del generation_payload["negative_prompt"]
                if "num_inference_steps" in generation_payload:
                    del generation_payload["num_inference_steps"]
                if "guidance_scale" in generation_payload:
                    del generation_payload["guidance_scale"]
                print(f"[FLUX] Using FLUX-specific payload format")
            
            # Add modelId if available
            if model_info["id"] is not None:
                generation_payload["modelId"] = model_info["id"]
                print(f"[SEARCH] Using specific model ID: {model_info['id']}")
            
            # Model-specific adjustments
            if model_key in ["phoenix-1-0", "phoenix"]:
                # Phoenix models use alchemy and need specific parameters
                generation_payload["alchemy"] = True
                generation_payload["ultra"] = False
                generation_payload["contrast"] = 3.5
                # Phoenix models don't use negative_prompt
                if "negative_prompt" in generation_payload:
                    del generation_payload["negative_prompt"]
                # Phoenix models use fewer steps
                generation_payload["num_inference_steps"] = 15
                generation_payload["guidance_scale"] = 7.0
            elif model_key in ["flux-dev", "flux-schnell"]:
                # FLUX models already handled above
                pass
            elif model_key in ["lucid-origin", "lucid-realism"]:
                # Lucid models don't use alchemy
                generation_payload["alchemy"] = False
                generation_payload["ultra"] = False
                generation_payload["contrast"] = 3.5
                # Lucid models don't use negative_prompt
                if "negative_prompt" in generation_payload:
                    del generation_payload["negative_prompt"]
            elif model_key == "flux-1-kontext":
                # FLUX.1 Kontext requires exact dimension pairs from the API
                KONTEXT_DIMENSIONS = {
                    "1:1": (1024, 1024),
                    "16:9": (1568, 672),   # Closest to 16:9 (2.33:1)
                    "9:16": (672, 1568),
                    "4:3": (1248, 832),    # Closest to 4:3 (1.5:1)
                    "3:4": (832, 1248),
                    "2:3": (880, 1184),    # Closest to 2:3
                    "3:2": (1184, 880),
                }
                w, h = KONTEXT_DIMENSIONS.get(aspect_ratio, (1024, 1024))
                generation_payload["width"] = w
                generation_payload["height"] = h
                generation_payload["contrast"] = 3.5
                generation_payload["num_images"] = 1
                generation_payload["enhancePrompt"] = False
                generation_payload["styleUUID"] = "111dc692-d470-4eec-b791-3475abac4c46"
                # Remove incompatible parameters not in Kontext docs
                for key in ["alchemy", "ultra", "negative_prompt", "num_inference_steps", "guidance_scale", "presetStyle"]:
                    if key in generation_payload:
                        del generation_payload[key]
                print(f"[FLUX] FLUX.1 Kontext exact dimensions: {w}x{h} for {aspect_ratio}")
            else:
                # Default V1 parameters for other models
                pass
            
            # Use V1 endpoint
            api_endpoint = self.available_generators['leonardo-api']['api_endpoint']
        
        print(f"[SEARCH] Using API endpoint: {api_endpoint}")
        print(f"[QUALITY] Enhanced prompt with {len(enhanced_prompt.split(','))} quality terms")
        print(f"[QUALITY] Comprehensive negative prompt for maximum quality")
        
        print(f"[SEARCH] Final payload: {json.dumps(generation_payload, indent=2)}")
        
        print(f"[ART] Leonardo.ai generation with {model_info['name']}")
        print(f"[RATIO] Aspect Ratio: {aspect_ratio} ({width}x{height})")
        print(f"[STYLE] Style: {kwargs.get('preset_style', 'LEONARDO')}")
        print(f"[QUALITY] Quality: {kwargs.get('quality', 'standard')}")
        print(f"[SEARCH] Payload: {json.dumps(generation_payload, indent=2)}")
        print(f"[SEARCH] Sending request to: {api_endpoint}")
        print(f"[SEARCH] Headers: {headers}")
        print(f"[SEARCH] Payload: {json.dumps(generation_payload, indent=2)}")
        
        try:
            print(f"[SEND] Sending POST request...")
            # Start generation
            response = requests.post(
                api_endpoint,
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
            
            # Extract generation ID from the response based on API version
            if api_version == "v2":
                # V2 API response format - multiple possible structures
                generation_id = None
                
                # Try different V2 response structures
                if "sd_generation_job" in data and "id" in data["sd_generation_job"]:
                    generation_id = data["sd_generation_job"]["id"]
                    print(f"[V2] Found generation ID in sd_generation_job: {generation_id}")
                elif "generations_by_pk" in data and "id" in data["generations_by_pk"]:
                    generation_id = data["generations_by_pk"]["id"]
                    print(f"[V2] Found generation ID in generations_by_pk: {generation_id}")
                elif "id" in data:
                    generation_id = data["id"]
                    print(f"[V2] Found generation ID in root: {generation_id}")
                elif "generationId" in data:
                    generation_id = data["generationId"]
                    print(f"[V2] Found generationId in root: {generation_id}")
                elif "generate" in data and "generationId" in data["generate"]:
                    generation_id = data["generate"]["generationId"]
                    print(f"[V2] Found generation ID in generate object: {generation_id}")
                else:
                    print(f"[ERROR] Full V2 response structure: {json.dumps(data, indent=2)}")
                    
                    # Check if response is a list (error response)
                    if isinstance(data, list):
                        print(f"[ERROR] V2 API returned error list instead of expected object")
                        if len(data) > 0 and isinstance(data[0], dict):
                            error_data = data[0]
                            if "extensions" in error_data:
                                print(f"[ERROR] API Error: {error_data.get('extensions', {}).get('details', {}).get('message', 'Unknown error')}")
                            elif "message" in error_data:
                                print(f"[ERROR] API Error: {error_data['message']}")
                        raise ValueError(f"V2 API returned error: {data}")
                    else:
                        print(f"[ERROR] Response keys: {list(data.keys())}")
                        print(f"[ERROR] Looking for generation ID in any field...")
                        
                        # Try to find any field that might contain the generation ID
                        for key, value in data.items():
                            if isinstance(value, dict) and 'id' in value:
                                print(f"[ERROR] Found potential ID in {key}: {value['id']}")
                            elif isinstance(value, str) and len(value) > 10:
                                print(f"[ERROR] Found potential ID string in {key}: {value}")
                    
                    raise ValueError("Could not extract generation ID from V2 response")
                    
            else:
                # V1 API response format
                if "sdGenerationJob" in data and "generationId" in data["sdGenerationJob"]:
                    generation_id = data["sdGenerationJob"]["generationId"]
                elif "generations_by_pk" in data and "id" in data["generations_by_pk"]:
                    generation_id = data["generations_by_pk"]["id"]
                else:
                    print(f"[ERROR] Full V1 response structure: {json.dumps(data, indent=2)}")
                    raise ValueError("Could not extract generation ID from V1 response")
            
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
    
    async def generate_with_azure_ai(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Azure AI API"""
        print(f"[AZURE] Azure AI generation with {prompt[:100]}...")
        
        if "azure-ai" not in self.api_keys:
            raise ValueError("API key required for Azure AI")
        
        # Get parameters (preserve requested size for post-processing)
        target_width = kwargs.get("width", 1024)
        target_height = kwargs.get("height", 1024)
        model_key = kwargs.get("model", "flux-1-1-pro")
        
        # Get model info
        generator_info = self.available_generators["azure-ai"]
        models = generator_info["models"]
        
        if model_key not in models:
            raise ValueError(f"Model {model_key} not available in Azure AI")
        
        model_info = models[model_key]
        deployment_name = model_info["deployment_name"]
        
        # Azure AI FLUX.2-Pro only supports 1024x1024; we'll fit to requested aspect after generation
        request_width, request_height = 1024, 1024
        
        # Azure OpenAI endpoint (working for FLUX-1.1-pro)
        endpoint = "https://azure-flux-2-resource.openai.azure.com"

        # Use API key header (standard Azure OpenAI)
        api_key = self.api_keys.get("azure-ai")
        if not api_key:
            raise ValueError("API key required for Azure AI")
        auth_headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }

        # Lock to the working endpoint and api-version
        api_versions = ["2024-02-01"]

        # Request body for OpenAI images endpoint (use model name)
        generation_body = {
            "model": "FLUX-1.1-pro",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }

        # Single working endpoint
        generation_url = f"{endpoint}/openai/deployments/{deployment_name}/images/generations?api-version=2024-02-01"

        print(f"[AZURE] Generating with FLUX-1.1-pro at {generation_url}")
        print(f"[AZURE] Prompt: {prompt[:100]}...")
        try:
            response = requests.post(
                generation_url,
                headers=auth_headers,
                json=generation_body,
                timeout=60
            )
            response.raise_for_status()
            response_data = response.json()

            if 'data' not in response_data or not response_data['data']:
                raise ValueError("No image data in response")

            image_data = response_data['data'][0]
            if 'b64_json' in image_data:
                b64_img = image_data['b64_json']
                image_bytes = base64.b64decode(b64_img)
                image = Image.open(io.BytesIO(image_bytes))
                print(f"[AZURE] Generated image: {image.size}")
                if image.size != (target_width, target_height):
                    try:
                        resample = getattr(Image, "Resampling", Image).LANCZOS
                    except Exception:
                        resample = Image.LANCZOS
                    image = ImageOps.fit(image, (target_width, target_height), method=resample)
                    print(f"[AZURE] Fitted image to: {image.size}")
                return image
            else:
                raise ValueError("Unexpected image format in response")
        except Exception as e:
            raise ValueError(f"Azure AI generation failed: {e}")
        raise ValueError("Azure AI generation failed: no response")
    
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
            elif generator_name == "azure-ai":
                return await self.generate_with_azure_ai(prompt, **kwargs)
            elif generator_name == "nano-banana-pro":
                return await self.generate_with_nano_banana(prompt, **kwargs)
            elif generator_name == "seedream":
                return await self.generate_with_seedream(prompt, **kwargs)
            elif generator_name == "midjourney-api":
                return await self.generate_with_midjourney(prompt, **kwargs)
            elif generator_name == "dall-e-3":
                return await self.generate_with_dalle3(prompt, **kwargs)
            elif generator_name == "replicate-api":
                return await self.generate_with_replicate(prompt, **kwargs)
            elif generator_name == "kandinsky-22":
                return await self.generate_with_kandinsky(prompt, **kwargs)
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
