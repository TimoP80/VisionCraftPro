"""
Test different Hugging Face endpoints to find the correct one

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os

def load_api_keys():
    """Load API keys from file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def test_hf_endpoints():
    """Test different Hugging Face endpoints"""
    api_keys = load_api_keys()
    hf_key = api_keys.get('huggingface-api')
    
    if not hf_key:
        print("❌ No Hugging Face API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json"
    }
    
    # Test different endpoints
    endpoints = [
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        "https://huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        "https://inference-api.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        "https://api.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    payload = {
        "inputs": "beautiful woman, high quality, detailed",
        "parameters": {
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }
    
    print("🧪 Testing Hugging Face Endpoints")
    print("=" * 60)
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: {endpoint}")
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"   🖼️  Image received: {len(response.content)} bytes")
                else:
                    print(f"   📋 Response: {response.text[:200]}...")
                return endpoint
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n💡 No working endpoints found")
    return None

def test_hf_models_endpoint():
    """Test if we can list available models"""
    api_keys = load_api_keys()
    hf_key = api_keys.get('huggingface-api')
    
    if not hf_key:
        print("❌ No Hugging Face API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing models endpoint...")
    
    # Try to get user info first
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=30)
        print(f"   Whoami Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ User: {user_info.get('name', 'Unknown')}")
            print(f"   📋 Type: {user_info.get('type', 'Unknown')}")
            
            # Check if user has pro account
            if user_info.get('isPro', False):
                print(f"   💎 Pro account: Yes")
            else:
                print(f"   🆓 Pro account: No (limited access)")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_hf_endpoints()
    test_hf_models_endpoint()
