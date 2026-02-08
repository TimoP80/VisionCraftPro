"""
Test fal.ai with correct authentication format

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

def test_fal_correct_auth():
    """Test fal.ai with correct authentication format"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        return False
    
    print("🧪 Testing fal.ai with Correct Auth Format")
    print("=" * 50)
    print(f"🔑 API Key: {'*' * 10}{fal_key[-4:] if len(fal_key) > 4 else 'Too short'}")
    print(f"📏 Length: {len(fal_key)} characters")
    print(f"🔤 Format: {fal_key[:10]}...")
    
    # Correct fal.ai authentication format
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 Using Authorization: Key YOUR_API_KEY format")
    
    # Test with FLUX.1-schnell
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
            "https://fal.run/fal-ai/flux.1-schnell",
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
                    image.save("fal_test_correct.png")
                    print(f"💾 Saved as: fal_test_correct.png")
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

def test_fal_alternative_models():
    """Test alternative fal.ai models"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        return
    
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing Alternative Models")
    print("=" * 50)
    
    # Test different models
    models = [
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
    
    for model in models:
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
    
    return working_models

def test_fal_account():
    """Test fal.ai account info"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        return
    
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n👤 Testing Account Info")
    print("=" * 50)
    
    try:
        response = requests.get(
            "https://api.fal.ai/v1/user/me",
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Account access successful!")
            print(f"👤 User ID: {user_info.get('id', 'Unknown')}")
            print(f"📧 Email: {user_info.get('email', 'Unknown')}")
            print(f"📊 Credits: {user_info.get('credits', 'Unknown')}")
            return True
        else:
            print(f"❌ Account access failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 fal.ai Correct Authentication Test")
    print("=" * 50)
    
    # Test account first
    account_success = test_fal_account()
    
    if account_success:
        # Test main functionality
        success = test_fal_correct_auth()
        
        if success:
            # Test alternative models
            working_models = test_fal_alternative_models()
            
            print(f"\n" + "=" * 50)
            print("✅ fal.ai is working!")
            print(f"🎯 Working models: {', '.join(working_models)}")
            print("💡 Ready to integrate into VisionCraft Pro")
        else:
            print(f"\n" + "=" * 50)
            print("❌ fal.ai generation failed")
    else:
        print(f"\n" + "=" * 50)
        print("❌ fal.ai authentication failed")
        print("💡 Check API key format and permissions")
