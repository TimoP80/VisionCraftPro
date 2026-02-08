"""
Test fal.ai direct model generation with correct auth

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

def test_fal_direct():
    """Test fal.ai direct model generation"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        return False
    
    print("🧪 Testing fal.ai Direct Generation")
    print("=" * 50)
    print(f"🔑 API Key: {'*' * 10}{fal_key[-4:] if len(fal_key) > 4 else 'Too short'}")
    
    # Correct fal.ai authentication
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple, working model
    models_to_test = [
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
        },
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
        }
    ]
    
    for model in models_to_test:
        print(f"\n🔍 Testing: {model['name']}")
        print(f"📡 Endpoint: {model['endpoint']}")
        
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
                print(f"   ✅ SUCCESS!")
                
                if 'images' in result and result['images']:
                    image_info = result['images'][0]
                    image_url = image_info['url']
                    print(f"   🖼️  Image URL: {image_url}")
                    
                    # Download and save
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        filename = f"fal_{model['name'].replace(' ', '_').replace('.', '').lower()}.png"
                        image.save(filename)
                        print(f"   💾 Saved as: {filename}")
                        print(f"   📏 Image size: {image.size}")
                        return True
                else:
                    print(f"   ❌ No image in response")
                    print(f"   📋 Response: {json.dumps(result, indent=2)[:500]}...")
            else:
                error_text = response.text
                print(f"   ❌ Failed: {error_text}")
                
                # Analyze error
                if "Invalid token" in error_text:
                    print(f"   💡 API key is invalid")
                elif "insufficient credit" in error_text:
                    print(f"   💡 Insufficient credits")
                elif "rate limit" in error_text.lower():
                    print(f"   💡 Rate limited")
                elif "not found" in error_text.lower():
                    print(f"   💡 Model endpoint not found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def test_fal_simple():
    """Test with minimal parameters"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        return False
    
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🧪 Testing with Minimal Parameters")
    print("=" * 50)
    
    # Try the simplest possible request
    payload = {
        "prompt": "test image",
        "num_images": 1
    }
    
    try:
        response = requests.post(
            "https://fal.run/fal-ai/fast-sdxl",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Simple request works!")
            if 'images' in result:
                print(f"🖼️  Got {len(result['images'])} images")
                return True
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🧪 fal.ai Direct Generation Test")
    print("=" * 50)
    
    # Test direct generation
    success = test_fal_direct()
    
    if not success:
        # Try simple test
        simple_success = test_fal_simple()
        
        if simple_success:
            print(f"\n✅ fal.ai works with simple parameters!")
        else:
            print(f"\n❌ fal.ai not working")
            print(f"💡 Check:")
            print(f"   1. API key is correct")
            print(f"   2. Account has credits")
            print(f"   3. Account is verified")
    else:
        print(f"\n✅ fal.ai is working! Ready for integration!")
