"""
Test fal.ai with UUID key format

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

def test_fal_uuid_key():
    """Test fal.ai with UUID key format"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        return False
    
    print("🧪 Testing fal.ai with UUID Key")
    print("=" * 40)
    print(f"🔑 Key format: UUID (not fal- prefixed)")
    
    # Try different auth methods for UUID keys
    auth_methods = [
        {"Authorization": f"Bearer {fal_key}"},
        {"Authorization": f"Key {fal_key}"},
        {"X-API-Key": fal_key},
        {"api-key": fal_key},
        {"Authorization": fal_key}  # No prefix
    ]
    
    for i, headers in enumerate(auth_methods):
        print(f"\n📡 Method {i+1}: {list(headers.keys())[0]}")
        
        try:
            # Test with a simple model
            payload = {
                "prompt": "beautiful woman, high quality, detailed",
                "image_size": "square_hd",
                "num_inference_steps": 4,
                "guidance_scale": 2.0,
                "num_images": 1
            }
            
            response = requests.post(
                "https://fal.run/fal-ai/fast-sdxl",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and result['images']:
                    print(f"   ✅ SUCCESS with method {i+1}!")
                    image_url = result['images'][0]['url']
                    print(f"   🖼️  Image URL: {image_url}")
                    
                    # Download and save
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        image.save("fal_uuid_test.png")
                        print(f"   💾 Saved as: fal_uuid_test.png")
                        return True
                else:
                    print(f"   ❌ No image in response")
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden - wrong key format")
            else:
                print(f"   📋 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n❌ UUID key format not working")
    return False

if __name__ == "__main__":
    success = test_fal_uuid_key()
    
    if not success:
        print(f"\n💡 Recommendation:")
        print(f"   Get a proper fal.ai API key starting with 'fal-'")
        print(f"   Go to: https://fal.ai/dashboard")
    else:
        print(f"\n✅ fal.ai working with UUID key!")
