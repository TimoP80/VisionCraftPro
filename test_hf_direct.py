"""
Test Hugging Face direct API calls

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import base64
import io
from PIL import Image

def test_hf_direct():
    """Test Hugging Face direct API calls"""
    try:
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)
            hf_token = api_keys.get('huggingface-api')
    except:
        hf_token = None
    
    if not hf_token:
        print("❌ No Hugging Face API key")
        return
    
    print("🧪 Testing Hugging Face Direct API")
    print("=" * 40)
    
    # Try different authentication methods
    auth_methods = [
        {"Authorization": f"Bearer {hf_token}"},
        {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"},
        {"X-API-Key": hf_token, "Content-Type": "application/json"},
        {"X-Api-Key": hf_token, "Content-Type": "application/json"},
    ]
    
    # Test with a simple model first
    test_payload = {
        "inputs": "A beautiful landscape with mountains",
        "parameters": {
            "num_inference_steps": 10,
            "guidance_scale": 7.5,
            "width": 256,
            "height": 256
        }
    }
    
    endpoints = [
        "https://router.huggingface.co/models/runwayml/stable-diffusion-v1-5",
        "https://router.huggingface.co/models/stabilityai/stable-diffusion-2-1",
        "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        for i, headers in enumerate(auth_methods):
            try:
                print(f"   📡 Auth method {i+1}: {list(headers.keys())[0]}")
                response = requests.post(endpoint, headers=headers, json=test_payload, timeout=30)
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      ✅ SUCCESS!")
                    
                    # Check if it's an image
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        try:
                            # Save the image
                            image = Image.open(io.BytesIO(response.content))
                            image.save(f"hf_test_{endpoint.split('/')[-1]}.png")
                            print(f"      🖼️  Image saved: {image.size}")
                            return True
                        except Exception as e:
                            print(f"      ❌ Image save error: {e}")
                    else:
                        print(f"      📋 Response: {response.text[:100]}...")
                else:
                    print(f"      ❌ Failed: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    print(f"\n❌ All attempts failed")
    return False

def test_hf_alternative():
    """Test alternative Hugging Face approaches"""
    try:
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)
            hf_token = api_keys.get('huggingface-api')
    except:
        hf_token = None
    
    if not hf_token:
        print("❌ No Hugging Face API key")
        return
    
    print(f"\n🔍 Testing Alternative Approaches")
    print("=" * 40)
    
    # Test 1: Direct model API
    try:
        headers = {"Authorization": f"Bearer {hf_token}"}
        response = requests.get(
            "https://huggingface.co/api/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers,
            timeout=10
        )
        print(f"Model API: {response.status_code}")
        if response.status_code == 200:
            model_info = response.json()
            print(f"✅ Model info: {model_info.get('modelId', 'Unknown')}")
    except Exception as e:
        print(f"❌ Model API error: {e}")
    
    # Test 2: Inference API (old way)
    try:
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {
            "inputs": "test image",
            "parameters": {"num_inference_steps": 1}
        }
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers,
            json=payload,
            timeout=10
        )
        print(f"Old Inference: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Old inference works!")
        else:
            print(f"❌ {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Old inference error: {e}")

if __name__ == "__main__":
    success = test_hf_direct()
    test_hf_alternative()
    
    if not success:
        print(f"\n💡 Hugging Face Integration Status:")
        print(f"   ❌ Direct API calls failed")
        print(f"   ✅ Inference Providers available")
        print(f"   💡 May need Pro account or different auth method")
        print(f"   🚀 Consider Replicate or fal.ai instead")
