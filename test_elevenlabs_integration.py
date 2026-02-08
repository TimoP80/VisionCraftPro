"""
Test ElevenLabs integration in VisionCraft Pro

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os

def test_elevenlabs_api_key():
    """Test if ElevenLabs API key is available"""
    try:
        with open('api_keys.json', 'r') as f:
            keys = json.load(f)
            elevenlabs_key = keys.get('elevenlabs-api')
            if elevenlabs_key:
                print(f"✅ ElevenLabs API key found: {'*' * 10}{elevenlabs_key[-4:]}")
                return elevenlabs_key
            else:
                print("❌ No ElevenLabs API key found")
                return None
    except Exception as e:
        print(f"❌ Error loading API keys: {e}")
        return None

def test_elevenlabs_models_endpoint():
    """Test ElevenLabs models endpoint"""
    api_key = test_elevenlabs_api_key()
    if not api_key:
        return
    
    print("=" * 60)
    print("Testing ElevenLabs Models Endpoint")
    print("=" * 60)
    
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Test models endpoint (if it exists)
        response = requests.get("https://api.elevenlabs.io/v1/models", headers=headers, timeout=30)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Models endpoint works! Found {len(models)} models")
            
            # Show some model examples
            if isinstance(models, list) and models:
                print(f"\n📋 Available Models:")
                for i, model in enumerate(models[:5]):  # Show first 5
                    print(f"   {i+1}. {model.get('id', 'Unknown')}: {model.get('name', 'Unknown')}")
            elif isinstance(models, dict):
                print(f"\n📋 Model Data:")
                print(json.dumps(models, indent=2))
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing models endpoint: {e}")

def test_elevenlabs_generation():
    """Test ElevenLabs image generation"""
    api_key = test_elevenlabs_api_key()
    if not api_key:
        return
    
    print(f"\n" + "=" * 60)
    print("Testing ElevenLabs Image Generation")
    print("=" * 60)
    
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test with a simple generation
    payload = {
        "prompt": "beautiful woman, high quality, detailed",
        "model": "realistic-vision-v6",
        "width": 512,
        "height": 512,
        "num_images": 1,
        "negative_prompt": "blurry, low quality",
        "num_inference_steps": 20,
        "guidance_scale": 7.0,
        "style": "photorealistic",
        "scheduler": "KLMS",
        "output_format": "png"
    }
    
    try:
        print(f"🧪 Testing generation with payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            "https://api.elevenlabs.io/v1/text2image",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful!")
            print(f"📋 Response structure: {list(result.keys())}")
            
            # Check for images
            if "images" in result:
                images = result["images"]
                print(f"🖼️  Generated {len(images)} image(s)")
                
                if images and len(images) > 0:
                    image_data = images[0]
                    print(f"📋 Image data keys: {list(image_data.keys())}")
                    
                    if "url" in image_data:
                        print(f"🔗 Image URL: {image_data['url']}")
                    elif "image_base64" in image_data:
                        print(f"📄 Base64 image data: {len(image_data['image_base64'])} characters")
                    else:
                        print(f"❓ Unknown image format")
                else:
                    print(f"❌ No images found in response")
            else:
                print(f"❌ No 'images' key in response")
                print(f"📋 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"📋 Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")

def test_visioncraft_integration():
    """Test VisionCraft Pro ElevenLabs integration"""
    print(f"\n" + "=" * 60)
    print("Testing VisionCraft Pro Integration")
    print("=" * 60)
    
    try:
        # Test models endpoint
        response = requests.get("http://localhost:8000/models", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ VisionCraft Pro models endpoint works!")
            
            # Check if ElevenLabs is in the models
            if "elevenlabs-api" in models:
                print(f"✅ ElevenLabs API found in VisionCraft Pro models!")
                elevenlabs_info = models["elevenlabs-api"]
                print(f"📋 ElevenLabs Info:")
                print(f"   Name: {elevenlabs_info.get('name', 'Unknown')}")
                print(f"   Type: {elevenlabs_info.get('type', 'Unknown')}")
                print(f"   Description: {elevenlabs_info.get('description', 'Unknown')}")
                
                # Check models
                if "models" in elevenlabs_info:
                    elevenlabs_models = elevenlabs_info["models"]
                    print(f"   Available Models: {list(elevenlabs_models.keys())}")
                    
                    # Show some model details
                    for model_key, model_info in list(elevenlabs_models.items())[:3]:
                        print(f"   🎨 {model_info.get('name', 'Unknown')}: {model_info.get('description', 'Unknown')}")
                else:
                    print(f"   ❌ No models found")
            else:
                print(f"❌ ElevenLabs API not found in VisionCraft Pro models")
                print(f"   Available models: {list(models.keys())}")
        else:
            print(f"❌ VisionCraft Pro models endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing VisionCraft Pro integration: {e}")

if __name__ == "__main__":
    print("🧪 ElevenLabs Integration Test")
    print("=" * 60)
    
    # Test API key
    api_key = test_elevenlabs_api_key()
    
    if api_key:
        # Test ElevenLabs API directly
        test_elevenlabs_models_endpoint()
        test_elevenlabs_generation()
        
        # Test VisionCraft Pro integration
        test_visioncraft_integration()
    else:
        print("\n💡 Please add your ElevenLabs API key to api_keys.json:")
        print('   {"elevenlabs-api": "your_api_key_here"}')
    
    print(f"\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
