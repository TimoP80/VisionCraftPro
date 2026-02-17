#!/usr/bin/env python3
"""
VisionCraft Pro - Production Server
Web server for VisionCraft Pro with Puter.com integration
"""

import os
import io
import base64
import json
import time
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from PIL import Image
from io import BytesIO
from datetime import datetime

# Add current directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modern_generators import ModernGeneratorManager
    from api_keys_simple import load_api_keys
    from image_gallery import ImageGallery
    from enhanced_gallery import EnhancedImageGallery
    from cuda_diagnostic import CudaDiagnostic
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure modern_generators.py, api_keys_simple.py, image_gallery.py, enhanced_gallery.py, and cuda_diagnostic.py exist")
    ModernGeneratorManager = None
    load_api_keys = None
    ImageGallery = None
    EnhancedImageGallery = None
    CudaDiagnostic = None

app = FastAPI(title="VisionCraft Pro - Production Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Serve the main VisionCraft Pro page"""
    # Read the static index.html file
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VisionCraft Pro</title>
        </head>
        <body>
            <h1>VisionCraft Pro</h1>
            <p>Error: static/index.html not found</p>
            <p>Please make sure the static/index.html file exists.</p>
        </body>
        </html>
        """)

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify FastAPI is working"""
    return {"message": "Test endpoint working"}

@app.get("/models")
async def get_models_direct():
    """Direct models endpoint for frontend"""
    print("🔍 /models endpoint called!")
    try:
        global generator_manager
        
        # Get local models
        local_models = {}
        if generator_manager and hasattr(generator_manager, 'available_generators'):
            # Add local models if available
            local_models = generator_manager.available_generators.get('local', {})
            print(f"🔍 Found {len(local_models)} local models")
        
        # Get modern generators with full details
        modern_generators = {}
        if generator_manager and hasattr(generator_manager, 'get_available_generators'):
            available_generators = generator_manager.get_available_generators()
            print(f"🔍 Available generators: {list(available_generators.keys())}")
            
            # Add Leonardo.ai with full model details
            if 'leonardo-api' in available_generators:
                leonardo_data = available_generators['leonardo-api']
                print(f"🔍 Leonardo.ai data keys: {list(leonardo_data.keys())}")
                print(f"🔍 Leonardo.ai has models: {'models' in leonardo_data}")
                if 'models' in leonardo_data:
                    print(f"🔍 Leonardo.ai models count: {len(leonardo_data['models'])}")
                modern_generators['leonardo-api'] = leonardo_data
            else:
                print(f"❌ leonardo-api not found in available_generators")
            
            # Add Replicate models
            if 'replicate-api' in available_generators:
                modern_generators['replicate-api'] = available_generators['replicate-api']
                print(f"🔍 Added replicate-api")
            
            # Add Kandinsky
            if 'kandinsky-22' in available_generators:
                modern_generators['kandinsky-22'] = available_generators['kandinsky-22']
                print(f"🔍 Added kandinsky-22")
            
            # Add Azure AI
            if 'azure-ai' in available_generators:
                modern_generators['azure-ai'] = available_generators['azure-ai']
                print(f"🔍 Added azure-ai")
        else:
            print(f"❌ Generator manager not available or missing get_available_generators")
        
        # Add Puter.com models
        modern_generators.update({
            'puter-dall-e-3': {
                'name': '🆓 DALL-E 3 (FREE)',
                'cost': 'FREE',
                'speed': 'Medium',
                'max_resolution': [1024, 1024],
                'description': 'Best quality image generation - completely FREE!',
                'type': 'puter'
            },
            'puter-gpt-image-1.5': {
                'name': '🆓 GPT Image 1.5 (FREE)',
                'cost': 'FREE',
                'speed': 'Medium',
                'max_resolution': [1024, 1024],
                'description': 'OpenAI GPT Image model - FREE access!',
                'type': 'puter'
            },
            'puter-gemini-2.5-flash': {
                'name': '🆓 Gemini 2.5 Flash (FREE)',
                'cost': 'FREE',
                'speed': 'Fast',
                'max_resolution': [1024, 1024],
                'description': 'Google Gemini Flash model - FREE access!',
                'type': 'puter'
            }
        })
        
        print(f"🔍 Final modern_generators keys: {list(modern_generators.keys())}")
        
        result = {
            "local_models": local_models,
            "modern_generators": modern_generators
        }
        
        print(f"🔍 Returning result with {len(result['local_models'])} local models and {len(result['modern_generators'])} modern generators")
        return result
        
    except Exception as e:
        print(f"❌ Error in /models endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/models")
async def get_models():
    """Get available models including Puter.com models"""
    print("🔍 /api/models endpoint called!")
    global generator_manager
    
    # Get local models
    local_models = {}
    if generator_manager and hasattr(generator_manager, 'available_generators'):
        # Add local models if available
        local_models = generator_manager.available_generators.get('local', {})
        print(f"🔍 Found {len(local_models)} local models")
    
    # Get modern generators with full details
    modern_generators = {}
    if generator_manager and hasattr(generator_manager, 'get_available_generators'):
        available_generators = generator_manager.get_available_generators()
        print(f"🔍 Available generators: {list(available_generators.keys())}")
        
        # Add Leonardo.ai with full model details
        if 'leonardo-api' in available_generators:
            leonardo_data = available_generators['leonardo-api']
            print(f"🔍 Leonardo.ai data keys: {list(leonardo_data.keys())}")
            print(f"🔍 Leonardo.ai has models: {'models' in leonardo_data}")
            if 'models' in leonardo_data:
                print(f"🔍 Leonardo.ai models count: {len(leonardo_data['models'])}")
            modern_generators['leonardo-api'] = leonardo_data
        else:
            print(f"❌ leonardo-api not found in available_generators")
        
        # Add Replicate models
        if 'replicate-api' in available_generators:
            modern_generators['replicate-api'] = available_generators['replicate-api']
            print(f"🔍 Added replicate-api")
        
        # Add Kandinsky
        if 'kandinsky-22' in available_generators:
            modern_generators['kandinsky-22'] = available_generators['kandinsky-22']
            print(f"🔍 Added kandinsky-22")
        
        # Add Azure AI
        if 'azure-ai' in available_generators:
            modern_generators['azure-ai'] = available_generators['azure-ai']
            print(f"🔍 Added azure-ai")
    else:
        print(f"❌ Generator manager not available or missing get_available_generators")
    
    # Add Puter.com models
    modern_generators.update({
        'puter-dall-e-3': {
            'name': '🆓 DALL-E 3 (FREE)',
            'cost': 'FREE',
            'speed': 'Medium',
            'max_resolution': [1024, 1024],
            'description': 'Best quality image generation - completely FREE!',
            'type': 'puter'
        },
        'puter-gpt-image-1.5': {
            'name': '🆓 GPT Image 1.5 (FREE)',
            'cost': 'FREE',
            'speed': 'Medium',
            'max_resolution': [1024, 1024],
            'description': 'OpenAI GPT Image model - FREE access!',
            'type': 'puter'
        },
        'puter-gemini-2.5-flash': {
            'name': '🆓 Gemini 2.5 Flash (FREE)',
            'cost': 'FREE',
            'speed': 'Fast',
            'max_resolution': [1024, 1024],
            'description': 'Google Gemini Flash model - FREE access!',
            'type': 'puter'
        }
    })
    
    print(f"🔍 Final modern_generators keys: {list(modern_generators.keys())}")
    
    return {
        "local_models": local_models,
        "modern_generators": modern_generators
    }

# Global variables
api_keys = {}
test_results = []
generator_manager = None
generated_images = []  # Simple gallery storage
image_gallery = None  # Enhanced gallery system
enhanced_gallery = None  # Enhanced gallery with tagging

# Persistent API key storage
API_KEYS_FILE = Path("api_keys.json")

def load_api_keys_persistent():
    """Load API keys from persistent storage"""
    global api_keys
    try:
        if API_KEYS_FILE.exists():
            with open(API_KEYS_FILE, 'r') as f:
                api_keys = json.load(f)
            print(f"📋 Loaded {len(api_keys)} API keys from persistent storage")
            for key, value in api_keys.items():
                print(f"  {key}: {'Configured' if value else 'Not set'}")
        else:
            print("📋 No persistent API keys file found, starting with empty keys")
            api_keys = {}
    except Exception as e:
        print(f"❌ Failed to load persistent API keys: {e}")
        api_keys = {}

def save_api_keys_persistent():
    """Save API keys to persistent storage"""
    global api_keys
    try:
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(api_keys, f, indent=2)
        print(f"💾 Saved {len(api_keys)} API keys to persistent storage")
    except Exception as e:
        print(f"❌ Failed to save persistent API keys: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize the server and load API keys"""
    global api_keys, generator_manager, image_gallery, enhanced_gallery
    
    print("🚀 Starting VisionCraft Pro Production Server...")
    
    # Initialize gallery systems
    if ImageGallery:
        try:
            image_gallery = ImageGallery()
            print("✅ Image Gallery initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Image Gallery: {e}")
            image_gallery = None
    else:
        print("⚠️ Image Gallery not available")
    
    if EnhancedImageGallery:
        try:
            enhanced_gallery = EnhancedImageGallery()
            print("✅ Enhanced Gallery initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Enhanced Gallery: {e}")
            enhanced_gallery = None
    else:
        print("⚠️ Enhanced Gallery not available")
    
    # Load API keys from persistent storage
    load_api_keys_persistent()
    
    # Initialize generator manager
    if ModernGeneratorManager:
        try:
            print("🔧 Initializing ModernGeneratorManager...")
            generator_manager = ModernGeneratorManager()
            print(f"🔧 Generator manager created: {type(generator_manager)}")
            print(f"🔧 Available generators: {list(generator_manager.get_available_generators().keys()) if hasattr(generator_manager, 'get_available_generators') else 'No method'}")
            
            # Check if Leonardo.ai models are loaded
            if hasattr(generator_manager, 'get_available_generators'):
                available = generator_manager.get_available_generators()
                if 'leonardo-api' in available:
                    leonardo_data = available['leonardo-api']
                    print(f"🔧 Leonardo.ai data keys: {list(leonardo_data.keys())}")
                    print(f"🔧 Leonardo.ai has models: {'models' in leonardo_data}")
                    if 'models' in leonardo_data:
                        print(f"🔧 Leonardo.ai models count: {len(leonardo_data['models'])}")
                    else:
                        print("❌ Leonardo.ai models property missing")
                else:
                    print("❌ leonardo-api not found in available generators")
            else:
                print("❌ Generator manager missing get_available_generators method")
            
            # Update generator manager with loaded API keys
            for key, value in api_keys.items():
                generator_manager.api_keys[key] = value
            print("✅ Modern Generator Manager initialized")
        except Exception as e:
            print(f"❌ Failed to initialize generator manager: {e}")
            import traceback
            traceback.print_exc()
            generator_manager = None
    else:
        print("⚠️ Modern Generator Manager not available")

@app.post("/generate")
async def generate_image(request: Request):
    """Generate image using specified model"""
    try:
        data = await request.json()
        model = data.get('model')
        prompt = data.get('prompt')
        
        print(f"🎨 Generation request for model: {model}")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        if model == 'leonardo-api':
            return await generate_with_leonardo(data)
        elif model == 'azure-ai':
            return await generate_with_azure_ai(data)
        elif model.startswith('puter-'):
            return {"success": True, "message": "Puter.com models are handled in frontend"}
        elif model in ['stable-diffusion-1.5', 'stable-diffusion-xl', 'sdxl-turbo']:
            return await generate_with_local_model(data)
        elif model in ['replicate-api', 'kandinsky-22'] or model.startswith('black-forest-labs/') or model.startswith('stability-ai/') or model.startswith('jyoung105/') or model.startswith('ai-forever/'):
            return await generate_with_replicate(data)
        else:
            return {"success": False, "message": f"Unknown model: {model}"}
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return {"success": False, "message": f"Generation failed: {str(e)}"}

async def generate_with_replicate(data):
    """Generate image using Replicate API"""
    try:
        if not generator_manager:
            return {"success": False, "message": "Replicate generator not initialized"}
        
        # Check if Replicate API key is available
        if 'replicate-api' not in api_keys:
            return {"success": False, "message": "Replicate API key not set. Please set your API key first."}
        
        print(f"🎨 Replicate generation with {data.get('prompt')[:100]}...")
        
        # Get parameters
        prompt = data.get('prompt')
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        steps = data.get('num_inference_steps', 25)
        guidance_scale = data.get('guidance_scale', 7.5)
        negative_prompt = data.get('negative_prompt', '')
        replicate_model = data.get('replicate_model', 'black-forest-labs/flux-schnell')
        
        # Generate image
        result = await generator_manager.generate_with_replicate(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            negative_prompt=negative_prompt,
            replicate_model=replicate_model
        )
        
        if result:
            # Convert to base64
            import base64
            from io import BytesIO
            
            buffered = BytesIO()
            result.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Save to gallery
            if image_gallery:
                image_gallery.add_image(
                    image_data=img_base64,
                    prompt=prompt,
                    model=replicate_model,
                    generation_time=0.0,
                    vram_used=0.0,
                    steps=steps,
                    guidance=guidance_scale,
                    resolution=(width, height),
                    negative_prompt=negative_prompt,
                    category="replicate_generation",
                    tags=["replicate", replicate_model.split('/')[-1]]
                )
            
            return {
                "success": True,
                "image": img_base64,
                "generation_time": 0.0,
                "vram_used": 0.0,
                "device": "Replicate API",
                "model": replicate_model,
                "timestamp": datetime.now().isoformat(),
                "gallery_id": len(generated_images) + 1
            }
        else:
            return {"success": False, "message": "Replicate generation failed"}
            
    except Exception as e:
        print(f"❌ Replicate generation failed: {e}")
        return {"success": False, "message": f"Replicate generation failed: {str(e)}"}

async def generate_with_local_model(data):
    """Generate image using local models"""
    try:
        # For now, we'll simulate local model generation
        # In a real implementation, this would use actual Stable Diffusion models
        print(f"🏠 Local model generation with {data.get('model')}")
        
        # Since we don't have actual local models loaded, we'll use Leonardo.ai as fallback
        # but with local model parameters
        print("⚠️ Local models not loaded, using Leonardo.ai as fallback")
        
        # Convert local model to Leonardo model
        local_to_leonardo = {
            'stable-diffusion-1.5': 'phoenix-0-9',
            'stable-diffusion-xl': 'phoenix-1-0',
            'sdxl-turbo': 'phoenix-1-0'
        }
        
        leonardo_model = local_to_leonardo.get(data.get('model'), 'phoenix-1-0')
        
        # Create Leonardo-compatible data
        leonardo_data = data.copy()
        leonardo_data['leonardo_model'] = leonardo_model
        leonardo_data['model'] = 'leonardo-api'
        
        # Add local model info to prompt for tracking
        leonardo_data['prompt'] = f"[Local model: {data.get('model')}] {data.get('prompt')}"
        
        return await generate_with_leonardo(leonardo_data)
        
    except Exception as e:
        print(f"❌ Local model generation failed: {e}")
        return {"success": False, "message": f"Local model generation failed: {str(e)}"}

async def generate_with_leonardo(data):
    """Generate image using Leonardo.ai API"""
    try:
        if not generator_manager:
            return {"success": False, "message": "Leonardo.ai generator not initialized"}
        
        # Check if Leonardo API key is available
        if 'leonardo-api' not in api_keys:
            return {"success": False, "message": "Leonardo.ai API key not set. Please set your API key first."}
        
        print(f"🎨 Starting Leonardo.ai real API generation...")
        
        # Extract parameters from data
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        num_inference_steps = data.get('num_inference_steps', 30)  # Increased from 25
        guidance_scale = data.get('guidance_scale', 7.5)
        leonardo_model = data.get('leonardo_model', 'phoenix-1-0')
        aspect_ratio = data.get('aspect_ratio', '1:1')
        preset_style = data.get('preset_style', 'LEONARDO')
        
        # Debug parameters
        print(f"🎨 Leonardo.ai Parameters:")
        print(f"  📝 Prompt: {prompt[:100]}...")
        print(f"  📏 Size: {width}x{height}")
        print(f"  ⚙️ Steps: {num_inference_steps}, Guidance: {guidance_scale}")
        print(f"  🎭 Model: {leonardo_model}")
        print(f"  📐 Aspect: {aspect_ratio}")
        print(f"  🎨 Style: {preset_style}")
        print(f"  ❌ Negative: {negative_prompt[:50]}...")
        
        # Validate and optimize parameters for better quality
        if not prompt or len(prompt.strip()) < 3:
            raise ValueError("Prompt is too short or empty")
        
        # Keep original prompt for Leonardo.ai (don't over-optimize)
        original_prompt = prompt
        
        # Only add minimal negative prompt if user provided one
        if negative_prompt and negative_prompt.strip() != '':
            # Clean up negative prompt to avoid conflicts
            negative_prompt = negative_prompt.strip()
        else:
            # Use specific negative prompt to prevent multiple faces
            negative_prompt = "multiple faces, double faces, triple faces, group of people, crowd, multiple people, extra faces, duplicate faces, blurry, bad quality, distorted"
        
        # Add single subject emphasis to prompt if it's about people
        if any(word in prompt.lower() for word in ['woman', 'man', 'person', 'girl', 'boy', 'people']):
            if not 'single' in prompt.lower() and not 'one' in prompt.lower():
                prompt = f"single {prompt}"
                print(f"🔧 Added 'single' to prevent multiple subjects")
        
        # Add portrait emphasis if it's a person
        if any(word in prompt.lower() for word in ['woman', 'man', 'person', 'girl', 'boy']):
            if not 'portrait' in prompt.lower():
                prompt = f"portrait of {prompt}"
                print(f"🔧 Added 'portrait' for single subject focus")
        
        # Use Leonardo.ai's default quality settings (don't over-optimize)
        num_inference_steps = 25  # Back to default
        guidance_scale = 7.5  # Back to default
        
        # Use recommended resolution but don't force it if user specified smaller
        if width < 512 or height < 512:
            print(f"⚠️ Small resolution detected: {width}x{height}, may affect quality")
            # Let user's choice but warn about it
        elif width > 1024 or height > 1024:
            print(f"⚠️ Large resolution detected: {width}x{height}, may affect generation time")
        
        print('🎨 Leonardo.ai Parameters:')
        print(f"  📝 Prompt: {original_prompt[:100]}...")
        print(f"  📏 Size: {width}x{height}")
        print(f"  ⚙️ Steps: {num_inference_steps}, Guidance: {guidance_scale}")
        print(f"  🎭 Model: {leonardo_model}")
        print(f"  📐 Aspect: {aspect_ratio}")
        print(f"  🎨 Style: {preset_style}")
        print(f"  ❌ Negative: {negative_prompt[:50]}...")
        
        # Call the real Leonardo.ai API
        start_time = time.time()
        image = await generator_manager.generate_with_leonardo(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            model=leonardo_model,
            aspect_ratio=aspect_ratio,
            preset_style=preset_style
        )
        generation_time = time.time() - start_time
        
        # Convert PIL image to base64
        buffer = io.BytesIO()
        
        # Save image with optimal settings for Leonardo.ai
        image.save(buffer, format='PNG', quality=95, optimize=True)
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Log image details for debugging
        print(f"🖼️ Image converted: {image.size} pixels, format: PNG")
        print(f"📊 Base64 size: {len(image_base64)} characters")
        
        # Validate the base64 string
        if len(image_base64) < 1000:
            raise ValueError("Generated image appears to be too small or corrupted")
        
        print(f"✅ Leonardo.ai real API generation successful! Time: {generation_time:.2f}s")
        
        # Save image to gallery systems
        global generated_images, image_gallery, enhanced_gallery
        
        # Save to simple in-memory gallery
        image_entry = {
            "id": len(generated_images) + 1,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "model": leonardo_model,
            "generation_time": generation_time,
            "timestamp": datetime.now().isoformat(),
            "image": image_base64,
            "size": len(image_base64) // 1024,  # Size in KB
            "width": width,
            "height": height
        }
        generated_images.append(image_entry)
        print(f"🖼️ Image saved to in-memory gallery (ID: {image_entry['id']})")
        
        # Save to persistent gallery if available
        gallery_id = None
        if image_gallery:
            try:
                # Save to gallery with metadata using add_image method
                gallery_id = image_gallery.add_image(
                    image_data=image_base64,
                    prompt=prompt,
                    model=leonardo_model,
                    generation_time=generation_time,
                    vram_used=0.0,  # Cloud-based service
                    steps=25,  # Leonardo.ai steps
                    guidance=7.5,  # Leonardo.ai guidance
                    resolution=(width, height),
                    negative_prompt=negative_prompt,
                    category="portrait" if any(word in prompt.lower() for word in ['woman', 'man', 'person', 'girl', 'boy']) else "other",
                    tags=["leonardo_ai", "ai_generated"]
                )
                print(f"💾 Image saved to persistent gallery (ID: {gallery_id})")
                
                # Also save to enhanced gallery if available
                if enhanced_gallery:
                    try:
                        # Convert base64 back to PIL Image for enhanced gallery
                        img_data = base64.b64decode(image_base64)
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        enhanced_id = enhanced_gallery.add_image(
                            image=pil_image,
                            prompt=prompt,
                            model=leonardo_model,
                            generation_time=generation_time,
                            width=width,
                            height=height,
                            api_used="leonardo_ai"
                        )
                        print(f"🎨 Image saved to enhanced gallery (ID: {enhanced_id})")
                    except Exception as e:
                        print(f"⚠️ Failed to save to enhanced gallery: {e}")
                        
            except Exception as e:
                print(f"⚠️ Failed to save to persistent gallery: {e}")
        
        # Return success with real image data
        return {
            "success": True,
            "message": "Leonardo.ai generation successful",
            "generation_time": generation_time,
            "image": image_base64,
            "vram_used": 0.0,  # Cloud-based service
            "device": "Leonardo.ai API",
            "timestamp": datetime.now().isoformat(),
            "gallery_id": image_entry['id'],  # Return gallery ID for frontend
            "persistent_id": gallery_id if image_gallery else None  # Return persistent ID if available
        }
        
    except Exception as e:
        print(f"❌ Leonardo.ai real API generation failed: {e}")
        return {"success": False, "message": f"Leonardo.ai generation failed: {str(e)}"}

async def generate_with_azure_ai(data):
    """Generate image using Azure AI API"""
    try:
        if not generator_manager:
            return {"success": False, "message": "Azure AI generator not initialized"}
        
        # Check if Azure AI API key is available
        if 'azure-ai' not in api_keys:
            return {"success": False, "message": "Azure AI API key not set. Please set your API key first."}
        
        print(f"🔵 Azure AI generation with {data.get('prompt')[:100]}...")
        
        # Get parameters
        prompt = data.get('prompt')
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        azure_model = data.get('azure_model', 'flux-2-pro')
        
        # Generate image
        result = await generator_manager.generate_with_azure_ai(
            prompt=prompt,
            width=width,
            height=height,
            model=azure_model
        )
        
        if isinstance(result, Image.Image):
            # Convert PIL image to base64
            import base64
            from io import BytesIO
            
            buffered = BytesIO()
            result.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Add to gallery if available
            image_entry = None
            gallery_id = None
            print(f"[DEBUG] image_gallery available: {image_gallery is not None}")
            if image_gallery:
                try:
                    print(f"[DEBUG] Attempting to add to gallery...")
                    gallery_id = image_gallery.add_image(
                        image_data=img_base64,
                        prompt=prompt,
                        model="azure-ai",
                        generation_time=0,
                        vram_used=0,
                        steps=1,
                        guidance=7.5,
                        resolution=(width, height),
                        negative_prompt="",
                        category="other"
                    )
                    image_entry = image_gallery.get_image(gallery_id)
                    print(f"[DEBUG] gallery.add_image returned ID: {gallery_id}")
                    print(f"[DEBUG] image_gallery.get_image returned: {image_entry is not None}")
                    print(f"📁 Added to gallery: {gallery_id}")
                except Exception as gallery_error:
                    print(f"⚠️ Failed to add to gallery: {gallery_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print("[DEBUG] image_gallery is None, skipping gallery save")
            
            return {
                "success": True,
                "image": img_base64,
                "generation_time": 0,  # Could add timing if needed
                "vram_used": None,  # Cloud API doesn't use local VRAM
                "device": "Azure AI API",
                "timestamp": datetime.now().isoformat(),
                "gallery_id": image_entry['id'] if image_entry else None,
                "persistent_id": gallery_id if image_gallery else None
            }
        else:
            return {"success": False, "message": "Azure AI generation failed - no image returned"}
        
    except Exception as e:
        print(f"❌ Azure AI generation failed: {e}")
        return {"success": False, "message": f"Azure AI generation failed: {str(e)}"}

@app.post("/set-api-key")
async def set_api_key(request: Request):
    """Set API key for a generator"""
    try:
        data = await request.json()
        api_key = data.get('api_key')
        generator_name = data.get('generator_name')  # Accept both formats
        generator = data.get('generator')  # Accept both formats
        
        # Use whichever field name is provided
        final_generator = generator or generator_name
        
        if not api_key or not final_generator:
            return {"success": False, "message": "API key and generator are required"}
        
        # Store the API key
        api_keys[final_generator] = api_key
        print(f"🔑 Setting API key for {final_generator}: {'*' * 10}{api_key[-4:] if len(api_key) > 4 else 'None'}")
        
        # Save API keys to persistent storage
        save_api_keys_persistent()
        
        # Also update the generator manager's API keys if it exists
        if generator_manager and hasattr(generator_manager, 'api_keys'):
            generator_manager.api_keys[final_generator] = api_key
            print(f"🔄 Updated generator manager API key for {final_generator}")
        
        return {"success": True, "message": f"API key set for {final_generator}"}
        
    except Exception as e:
        return {"success": False, "message": f"Error setting API key: {str(e)}"}

@app.get("/api/modern-generators")
async def get_modern_generators():
    """Get modern generators info"""
    return {
        "api_keys_set": list(api_keys.keys()),  # Return actual set keys
        "available": ["leonardo-api", "puter-dall-e-3", "puter-gpt-image-1-5", "puter-gemini-2-5-flash"]
    }

@app.get("/debug/sync-api-keys")
async def debug_sync_api_keys():
    """Debug endpoint to sync API keys with generator manager"""
    try:
        if generator_manager and hasattr(generator_manager, 'api_keys'):
            # Sync all API keys from server to generator manager
            for key, value in api_keys.items():
                generator_manager.api_keys[key] = value
            return {
                "success": True, 
                "message": "API keys synced",
                "server_keys": list(api_keys.keys()),
                "generator_keys": list(generator_manager.api_keys.keys())
            }
        else:
            return {"success": False, "message": "Generator manager not available"}
    except Exception as e:
        return {"success": False, "message": f"Sync failed: {str(e)}"}

@app.get("/status")
async def get_status_simple():
    """Simple status endpoint for frontend with real GPU detection"""
    global generator_manager
    
    # Default values
    status = {
        "vram_reserved": 0,
        "vram_total": 0,
        "vram_used_percent": 0,
        "vram_used": 0,
        "gpu_available": False,
        "model_loaded": None,
        "generation_active": False,
        "gpu_name": "No GPU",
        "gpu_memory": "Unknown",
        "device": "CPU"
    }
    
    # Try to get real GPU information
    if CudaDiagnostic:
        try:
            diagnostic = CudaDiagnostic()
            gpu_info = diagnostic._get_gpu_info()
            
            if gpu_info["gpus"] and len(gpu_info["gpus"]) > 0:
                gpu = gpu_info["gpus"][0]  # Use first GPU
                memory_total_gb = gpu["memory_total_mb"] / 1024
                memory_used_gb = gpu["memory_used_mb"] / 1024
                
                status.update({
                    "vram_reserved": memory_used_gb,
                    "vram_total": memory_total_gb,
                    "vram_used_percent": (memory_used_gb / memory_total_gb) * 100 if memory_total_gb > 0 else 0,
                    "vram_used": memory_used_gb,
                    "gpu_available": True,
                    "gpu_name": gpu["name"],
                    "gpu_memory": f"{memory_total_gb:.1f}GB",
                    "device": f"{gpu['name']} ({memory_total_gb:.1f}GB)"
                })
                # Previously logged GPU info every poll; silence to reduce spam
                pass
            
            return status
        except Exception as e:
            print(f"⚠️ GPU detection failed: {e}")
            # Keep default values
    
    # Check if model is loaded
    if generator_manager and hasattr(generator_manager, 'current_model'):
        status["model_loaded"] = generator_manager.current_model
    
    return status

@app.get("/api/stats")
async def get_stats():
    """Get gallery stats"""
    return {
        "total_images": 0,
        "total_size": 0,
        "recent_images": [],
        "models_used": []  # Add missing models_used field
    }

@app.get("/stats")
async def get_stats_direct():
    """Direct stats endpoint for frontend"""
    return {
        "total_images": 0,
        "total_size": 0,
        "recent_images": [],
        "models_used": []  # Add missing models_used field
    }

@app.get("/api/gallery")
async def get_gallery():
    """Get gallery images"""
    global generated_images, image_gallery, enhanced_gallery
    
    # First, try to get images from persistent gallery
    if image_gallery:
        try:
            # Get all images from persistent gallery
            persistent_images = image_gallery.get_recent_images(limit=100)  # Get up to 100 images
            if persistent_images and len(persistent_images) > 0:
                # Add image data to each entry
                images_with_data = []
                for img_entry in persistent_images:
                    # Get the actual image data as base64
                    image_data = image_gallery.get_image_data(img_entry["id"])
                    if image_data:
                        img_entry["image"] = image_data  # Add base64 image data
                        images_with_data.append(img_entry)
                        print(f"✅ Loaded image data for {img_entry['id']}: {len(image_data)} characters")
                    else:
                        print(f"⚠️ Could not load image data for {img_entry['id']}")
                        # Check if the file exists
                        image_path = os.path.join(image_gallery.images_dir, img_entry["filename"])
                        if os.path.exists(image_path):
                            file_size = os.path.getsize(image_path)
                            print(f"📁 File exists but failed to load: {image_path} ({file_size} bytes)")
                        else:
                            print(f"❌ File does not exist: {image_path}")
                
                print(f"🖼️ Found {len(images_with_data)} images in persistent gallery")
                return {
                    "images": images_with_data,
                    "stats": image_gallery.get_stats(),
                    "total": len(images_with_data),
                    "source": "persistent_gallery"
                }
        except Exception as e:
            print(f"⚠️ Failed to get persistent gallery: {e}")
    
    # Fallback to enhanced gallery
    if enhanced_gallery:
        try:
            enhanced_images = enhanced_gallery.get_all_images()
            if enhanced_images and len(enhanced_images) > 0:
                print(f"🎨 Found {len(enhanced_images)} images in enhanced gallery")
                return {
                    "images": enhanced_images,
                    "stats": enhanced_gallery.get_stats(),
                    "total": len(enhanced_images),
                    "source": "enhanced_gallery"
                }
        except Exception as e:
            print(f"⚠️ Failed to get enhanced gallery: {e}")
    
    # Last fallback to in-memory gallery
    print(f"📋 Using in-memory gallery with {len(generated_images)} images")
    return {
        "images": generated_images,
        "stats": {
            "total_images": len(generated_images),
            "total_size": sum(img.get('size', 0) for img in generated_images),
            "recent_images": generated_images[-5:] if generated_images else []
        },
        "total": len(generated_images),
        "source": "in_memory"
    }

@app.get("/gallery")
async def get_gallery_direct():
    """Direct gallery endpoint for frontend"""
    return await get_gallery()

@app.post("/enhance-prompt")
async def enhance_prompt(request: Request):
    """Enhance prompt for better image generation"""
    try:
        data = await request.json()
        prompt = data.get('prompt', '')
        style = data.get('style', 'balanced')
        detail_level = data.get('detail_level', 'medium')
        
        if not prompt or len(prompt.strip()) < 3:
            return {"success": False, "message": "Prompt is too short or empty"}
        
        # Create multiple enhancement options based on style and detail level
        enhancements = {}
        
        # Basic enhancement
        base_enhanced = f"masterpiece, best quality, highly detailed, {prompt}"
        
        # Style-specific enhancements
        if style == 'artistic':
            style_enhanced = f"artistic masterpiece, beautiful composition, {prompt}, digital painting, concept art"
        elif style == 'realistic':
            style_enhanced = f"photorealistic, professional photography, {prompt}, 8k resolution, ultra detailed"
        elif style == 'cinematic':
            style_enhanced = f"cinematic lighting, dramatic composition, {prompt}, movie still, high quality"
        elif style == 'anime':
            style_enhanced = f"anime style, beautiful artwork, {prompt}, manga style, high quality illustration"
        else:  # balanced
            style_enhanced = base_enhanced
        
        # Detail level enhancements
        if detail_level == 'minimal':
            detail_enhanced = f"simple, clean, {prompt}"
        elif detail_level == 'medium':
            detail_enhanced = base_enhanced
        elif detail_level == 'detailed':
            detail_enhanced = f"ultra detailed, intricate, {prompt}, masterpiece, best quality, 8k resolution"
        elif detail_level == 'extreme':
            detail_enhanced = f"hyper detailed, extremely intricate, {prompt}, masterpiece, best quality, 8k resolution, ultra realistic"
        
        # Combine enhancements
        final_enhanced = style_enhanced if style != 'balanced' else detail_enhanced
        
        enhancements = {
            'balanced': base_enhanced,
            'artistic': style_enhanced if style == 'artistic' else f"artistic masterpiece, {prompt}",
            'realistic': style_enhanced if style == 'realistic' else f"photorealistic, {prompt}",
            'cinematic': style_enhanced if style == 'cinematic' else f"cinematic, {prompt}",
            'anime': style_enhanced if style == 'anime' else f"anime style, {prompt}",
            'minimal': detail_enhanced if detail_level == 'minimal' else f"simple, {prompt}",
            'medium': detail_enhanced if detail_level == 'medium' else base_enhanced,
            'detailed': detail_enhanced if detail_level == 'detailed' else f"detailed, {prompt}",
            'extreme': detail_enhanced if detail_level == 'extreme' else f"hyper detailed, {prompt}"
        }
        
        return {
            "success": True,
            "original_prompt": prompt,
            "enhanced_prompt": final_enhanced,
            "all_enhancements": enhancements,
            "style": style,
            "detail_level": detail_level
        }
        
    except Exception as e:
        return {"success": False, "message": f"Failed to enhance prompt: {str(e)}"}

@app.get("/gallery/{image_id}")
async def get_gallery_image(image_id: str):
    """Get individual gallery image by ID"""
    try:
        global generated_images, image_gallery, enhanced_gallery
        
        print(f"🔍 Looking for image ID: {image_id}")
        
        # First, try persistent gallery
        if image_gallery:
            try:
                # Try to get image from persistent gallery
                image_data = image_gallery.get_image_data(image_id)
                if image_data:
                    # Get the metadata for this image
                    metadata = image_gallery.get_image_by_id(image_id)
                    if metadata:
                        # Combine metadata with image data
                        result = metadata.copy()
                        result["image"] = image_data
                        print(f"✅ Found image {image_id} in persistent gallery")
                        return result
                    else:
                        print(f"⚠️ Found image data but no metadata for {image_id}")
                        return {"error": "Image metadata not found"}
                else:
                    print(f"⚠️ No image data found for {image_id} in persistent gallery")
            except Exception as e:
                print(f"⚠️ Failed to get from persistent gallery: {e}")
        
        # Try enhanced gallery
        if enhanced_gallery:
            try:
                enhanced_images = enhanced_gallery.get_all_images()
                for img in enhanced_images:
                    if img.get('id') == image_id:
                        print(f"✅ Found image {image_id} in enhanced gallery")
                        return img
            except Exception as e:
                print(f"⚠️ Failed to get from enhanced gallery: {e}")
        
        # Finally, try in-memory gallery
        for img in generated_images:
            if img.get('id') == image_id:
                print(f"✅ Found image {image_id} in in-memory gallery")
                return img
        
        print(f"❌ Image not found: {image_id}")
        return {"error": "Image not found"}
        
    except Exception as e:
        print(f"❌ Failed to get image {image_id}: {e}")
        return {"error": f"Failed to get image: {str(e)}"}

# Global variables for batch generation
batch_jobs = {}
batch_job_counter = 0

@app.post("/api/batch-generate")
async def batch_generate(request: Request):
    """Start batch generation with multiple prompts"""
    global batch_jobs, batch_job_counter
    
    try:
        data = await request.json()
        prompts = data.get('prompts', [])
        model = data.get('model', 'stable-diffusion-1.5')
        base_params = data.get('parameters', {})
        
        if not prompts:
            return {"success": False, "message": "No prompts provided"}
        
        # Create batch job
        batch_job_counter += 1
        job_id = f"batch_{batch_job_counter}"
        
        batch_job = {
            "id": job_id,
            "status": "pending",
            "prompts": prompts,
            "model": model,
            "parameters": base_params,
            "results": [],
            "current_index": 0,
            "total_count": len(prompts),
            "completed_count": 0,
            "failed_count": 0,
            "start_time": time.time(),
            "estimated_completion": None
        }
        
        batch_jobs[job_id] = batch_job
        
        # Start batch processing in background
        asyncio.create_task(process_batch_job(job_id))
        
        return {
            "success": True,
            "job_id": job_id,
            "total_prompts": len(prompts),
            "message": f"Batch generation started for {len(prompts)} prompts"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Failed to start batch generation: {str(e)}"}

async def process_batch_job(job_id: str):
    """Process a batch generation job"""
    global batch_jobs, generator_manager
    
    job = batch_jobs.get(job_id)
    if not job:
        return
    
    job["status"] = "processing"
    
    try:
        for i, prompt in enumerate(job["prompts"]):
            job["current_index"] = i
            
            # Create generation parameters for this prompt
            gen_params = job["parameters"].copy()
            # Don't include prompt in gen_params since we're passing it separately
            gen_params.pop('prompt', None)
            
            print(f"🎨 Processing batch item {i+1}/{job['total_count']}: {prompt[:50]}...")
            
            # Generate image using Leonardo.ai
            if generator_manager:
                try:
                    result = await generator_manager.generate_with_leonardo(
                        prompt=prompt,
                        **gen_params
                    )
                    
                    if result:
                        # Convert to base64
                        import base64
                        from io import BytesIO
                        
                        buffered = BytesIO()
                        result.save(buffered, format="PNG")
                        img_base64 = base64.b64encode(buffered.getvalue()).decode()
                        
                        # Save to gallery
                        if image_gallery:
                            image_gallery.add_image(
                                image_data=img_base64,
                                prompt=prompt,
                                model=job["model"],
                                generation_time=0.0,  # Will be updated by actual generation
                                vram_used=0.0,
                                steps=gen_params.get("steps", 20),
                                guidance=gen_params.get("guidance_scale", 7.5),
                                resolution=(gen_params.get("width", 512), gen_params.get("height", 512)),
                                negative_prompt=gen_params.get("negative_prompt", ""),
                                category="batch_generation",
                                tags=["batch", job["model"]]
                            )
                        
                        job["results"].append({
                            "prompt": prompt,
                            "image": img_base64,
                            "success": True,
                            "index": i
                        })
                        job["completed_count"] += 1
                        print(f"✅ Batch item {i+1} completed successfully")
                    else:
                        job["results"].append({
                            "prompt": prompt,
                            "success": False,
                            "error": "Generation failed - no result returned",
                            "index": i
                        })
                        job["failed_count"] += 1
                        print(f"❌ Batch item {i+1} failed - no result")
                        
                except Exception as e:
                    print(f"❌ Batch item {i+1} failed with error: {e}")
                    job["results"].append({
                        "prompt": prompt,
                        "success": False,
                        "error": str(e),
                        "index": i
                    })
                    job["failed_count"] += 1
            else:
                job["results"].append({
                    "prompt": prompt,
                    "success": False,
                    "error": "Generator not available",
                    "index": i
                })
                job["failed_count"] += 1
                print(f"❌ Batch item {i+1} failed - generator not available")
            
            # Update estimated completion time
            elapsed = time.time() - job["start_time"]
            if job["completed_count"] + job["failed_count"] > 0:
                avg_time_per_image = elapsed / (job["completed_count"] + job["failed_count"])
                remaining_images = job["total_count"] - (job["completed_count"] + job["failed_count"])
                job["estimated_completion"] = time.time() + (avg_time_per_image * remaining_images)
        
        job["status"] = "completed"
        print(f"✅ Batch job {job_id} completed: {job['completed_count']} successful, {job['failed_count']} failed")
        
    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        print(f"❌ Batch job {job_id} failed: {e}")

@app.get("/api/batch-status/{job_id}")
async def get_batch_status(job_id: str):
    """Get status of a batch generation job"""
    job = batch_jobs.get(job_id)
    if not job:
        return {"error": "Batch job not found"}
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "current_index": job["current_index"],
        "total_count": job["total_count"],
        "completed_count": job["completed_count"],
        "failed_count": job["failed_count"],
        "progress_percentage": (job["completed_count"] + job["failed_count"]) / job["total_count"] * 100,
        "start_time": job["start_time"],
        "estimated_completion": job.get("estimated_completion"),
        "results": job["results"] if job["status"] == "completed" else []
    }

@app.get("/api/batch-jobs")
async def get_batch_jobs():
    """Get all batch jobs"""
    return {
        "jobs": list(batch_jobs.values()),
        "total_count": len(batch_jobs)
    }

@app.post("/api/generate-with-reference")
async def generate_with_reference(request: Request):
    """Generate image with reference image for style transfer"""
    try:
        form = await request.form()
        
        # Get form data
        prompt = form.get('prompt', '')
        model = form.get('model', 'stable-diffusion-1.5')
        reference_image = form.get('reference_image')
        
        if not reference_image:
            return {"success": False, "message": "No reference image provided"}
        
        if not prompt:
            return {"success": False, "message": "Prompt is required"}
        
        print(f"🎨 Generating with reference: {prompt[:50]}...")
        
        # For now, we'll use the reference image as inspiration but generate normally
        # In a full implementation, this would use ControlNet or img2img
        enhanced_prompt = f"Style transfer inspired by reference image: {prompt}"
        
        # Get generation parameters
        # For Leonardo.ai, we need to use their model names
        leonardo_model = 'phoenix-1-0'  # Use Leonardo's best model for reference generation
        
        parameters = {
            'model': leonardo_model,
            'width': int(form.get('width', 512)),
            'height': int(form.get('height', 512)),
            'steps': int(form.get('steps', 20)),
            'guidance_scale': float(form.get('guidance_scale', 7.5)),
            'negative_prompt': form.get('negative_prompt', ''),
        }
        
        # Generate image using Leonardo.ai (simplified reference generation)
        if generator_manager:
            result = await generator_manager.generate_with_leonardo(
                prompt=enhanced_prompt,
                **parameters
            )
            
            if result:
                # Convert to base64
                import base64
                from io import BytesIO
                
                buffered = BytesIO()
                result.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Save to gallery
                if image_gallery:
                    image_gallery.add_image(
                        image_data=img_base64,
                        prompt=prompt,
                        model=leonardo_model,  # Use the actual Leonardo model
                        generation_time=0.0,
                        vram_used=0.0,
                        steps=parameters['steps'],
                        guidance=parameters['guidance_scale'],
                        resolution=(parameters['width'], parameters['height']),
                        negative_prompt=parameters['negative_prompt'],
                        category="reference_generation",
                        tags=["reference", leonardo_model]
                    )
                
                return {
                    "success": True,
                    "image": img_base64,
                    "generation_time": 0.0,
                    "vram_used": 0.0,
                    "device": "GPU",
                    "model": leonardo_model,  # Use the actual Leonardo model
                    "gallery_id": len(generated_images) + 1
                }
            else:
                return {"success": False, "message": "Generation failed"}
        else:
            return {"success": False, "message": "Generator not available"}
            
    except Exception as e:
        print(f"❌ Reference generation failed: {e}")
        return {"success": False, "message": f"Generation failed: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print("🚀 Starting VisionCraft Pro Production Server...")
    print("📋 Open http://localhost:8000 in your browser")
    print("🆓 Puter.com integration is active - login should work properly")
    print("🎨 Generate unlimited FREE images with DALL-E 3, GPT Image, and Gemini!")
    print()
    print("💡 Tips:")
    print("  • Puter.com login requires server mode (not static HTML)")
    print("  • Select FREE models: DALL-E 3, GPT Image 1.5, Gemini 2.5 Flash")
    print("  • No API keys required for Puter.com models")
    print("  • Generate unlimited premium images for FREE!")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
