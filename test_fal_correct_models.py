"""
Test fal.ai with correct model endpoints

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

def test_fal_correct_models():
    """Test fal.ai with correct model endpoints"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        return False
    
    print("🧪 Testing fal.ai with Correct Model Names")
    print("=" * 50)
    print(f"🔑 API Key: {'*' * 10}{fal_key[-4:] if len(fal_key) > 4 else 'Too short'}")
    
    # Correct fal.ai authentication
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    # Correct model endpoints from fal.ai documentation
    models_to_test = [
        {
            "name": "FLUX.1 [dev]",
            "endpoint": "fal-ai/flux/dev",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed, photorealistic",
                "image_size": "square_hd",
                "num_inference_steps": 4,
                "guidance_scale": 3.5,
                "num_images": 1
            }
        },
        {
            "name": "FLUX.1 [schnell]",
            "endpoint": "fal-ai/flux/schnell", 
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
                        filename = f"fal_{model['name'].replace(' ', '_').replace('[', '').replace(']', '').replace('.', '').lower()}.png"
                        image.save(filename)
                        print(f"   💾 Saved as: {filename}")
                        print(f"   📏 Image size: {image.size}")
                        working_models.append(model['name'])
                else:
                    print(f"   ❌ No image in response")
                    print(f"   📋 Response: {json.dumps(result, indent=2)[:300]}...")
            else:
                error_text = response.text
                print(f"   ❌ Failed: {error_text}")
                
                # Analyze error
                if "Invalid token" in error_text:
                    print(f"   💡 API key is invalid")
                elif "insufficient credit" in error_text or "Exhausted balance" in error_text:
                    print(f"   💡 INSUFFICIENT CREDITS - Add credits at fal.ai/dashboard/billing")
                elif "rate limit" in error_text.lower():
                    print(f"   💡 Rate limited")
                elif "not found" in error_text.lower():
                    print(f"   💡 Model endpoint not found")
                elif "locked" in error_text.lower():
                    print(f"   💡 Account locked - need credits")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return working_models

def test_fal_balance():
    """Check fal.ai balance/status"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        return
    
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n💰 Checking fal.ai Balance")
    print("=" * 50)
    
    try:
        # Try to get user info (this might work with correct auth)
        response = requests.get(
            "https://api.fal.ai/v1/models",
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ API access working!")
            print(f"📊 Available models: {len(models.get('models', []))}")
            
            # Show some available models
            for model in models.get('models', [])[:5]:
                print(f"   🎨 {model.get('display_name', 'Unknown')} ({model.get('endpoint_id', 'Unknown')})")
        else:
            print(f"❌ API access failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 fal.ai Correct Models Test")
    print("=" * 50)
    
    # Check balance first
    test_fal_balance()
    
    # Test correct models
    working_models = test_fal_correct_models()
    
    print(f"\n" + "=" * 50)
    if working_models:
        print("✅ fal.ai is working!")
        print(f"🎯 Working models: {', '.join(working_models)}")
        print("💡 Ready to integrate into VisionCraft Pro")
    else:
        print("❌ fal.ai not working")
        print("💡 Most likely need to add credits at: fal.ai/dashboard/billing")
        print("💡 Or check if account is verified")
