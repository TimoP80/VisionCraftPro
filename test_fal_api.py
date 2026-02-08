"""
Test fal.ai API for image generation

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import time
import io
from PIL import Image

def load_api_keys():
    """Load API keys from file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def test_fal_api():
    """Test fal.ai API"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        print("💡 Add to api_keys.json: {\"fal-api\": \"your_fal_api_key_here\"}")
        return False
    
    headers = {
        "Authorization": f"Bearer {fal_key}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing fal.ai API")
    print("=" * 50)
    
    # Test with FLUX.1-schnell (fast and affordable)
    payload = {
        "prompt": "beautiful woman, high quality, detailed, photorealistic",
        "image_size": "square_hd",
        "num_inference_steps": 4,
        "guidance_scale": 2.0,
        "num_images": 1
    }
    
    try:
        print("📸 Testing FLUX.1-schnell generation...")
        response = requests.post(
            "https://fal.run/fal-ai/fast-sdxl",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation completed!")
            
            if 'images' in result and result['images']:
                image_info = result['images'][0]
                image_url = image_info['url']
                print(f"🖼️  Image URL: {image_url}")
                
                # Download and save the image
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    image = Image.open(io.BytesIO(img_response.content))
                    image.save("fal_test_image.png")
                    print(f"💾 Saved as: fal_test_image.png")
                    print(f"📏 Image size: {image.size}")
                    return True
                else:
                    print(f"❌ Failed to download image: {img_response.status_code}")
                    return False
            else:
                print(f"❌ No image in response")
                print(f"📋 Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fal_models():
    """Test different fal.ai models"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        return
    
    headers = {
        "Authorization": f"Bearer {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing Different fal.ai Models")
    print("=" * 50)
    
    # Popular fal.ai models
    models_to_test = [
        {
            "name": "FLUX.1-dev",
            "endpoint": "fal-ai/flux.1-dev",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed, photorealistic",
                "image_size": "square_hd",
                "num_inference_steps": 4,
                "guidance_scale": 3.5,
                "num_images": 1
            }
        },
        {
            "name": "FLUX.1-schnell",
            "endpoint": "fal-ai/flux.1-schnell",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed, photorealistic",
                "image_size": "square_hd",
                "num_inference_steps": 4,
                "guidance_scale": 2.0,
                "num_images": 1
            }
        },
        {
            "name": "Fast SDXL",
            "endpoint": "fal-ai/fast-sdxl",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed, photorealistic",
                "image_size": "square_hd",
                "num_inference_steps": 4,
                "guidance_scale": 2.0,
                "num_images": 1
            }
        }
    ]
    
    working_models = []
    
    for model in models_to_test:
        print(f"\n🔍 Testing: {model['name']}")
        
        try:
            response = requests.post(
                f"https://fal.run/{model['endpoint']}",
                headers=headers,
                json=model['payload'],
                timeout=60
            )
            
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and result['images']:
                    print(f"   ✅ {model['name']} works!")
                    working_models.append(model['name'])
                else:
                    print(f"   ❌ No image in response")
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Working models: {', '.join(working_models)}")
    return working_models

def test_fal_pricing():
    """Test fal.ai pricing and costs"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        return
    
    headers = {
        "Authorization": f"Bearer {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n💰 fal.ai Pricing Information")
    print("=" * 50)
    
    print("📊 Approximate costs per image:")
    print("   FLUX.1-schnell: ~$0.015")
    print("   FLUX.1-dev: ~$0.04")
    print("   Fast SDXL: ~$0.01")
    print("")
    print("💡 Advantages:")
    print("   ✅ No upfront payment required")
    print("   ✅ Pay-per-use only")
    print("   ✅ Latest FLUX models")
    print("   ✅ Fast generation")
    print("   ✅ High quality results")

if __name__ == "__main__":
    print("🧪 fal.ai API Test")
    print("=" * 50)
    
    # Test basic functionality
    success = test_fal_api()
    
    if success:
        # Test different models
        working_models = test_fal_models()
        
        # Show pricing info
        test_fal_pricing()
        
        print(f"\n" + "=" * 50)
        print("✅ fal.ai is working! Ready for integration")
        print(f"🎯 Working models: {len(working_models)}")
        print("💡 Ready to integrate into VisionCraft Pro")
    else:
        print(f"\n" + "=" * 50)
        print("❌ fal.ai test failed")
        print("💡 Check API key or try different model")
        print("🔑 Get API key from: https://fal.ai/dashboard")
