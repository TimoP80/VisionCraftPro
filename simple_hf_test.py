"""
Simple Hugging Face test to check basic functionality

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json

def test_hf_basic():
    """Test basic Hugging Face functionality"""
    try:
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)
            hf_token = api_keys.get('huggingface-api')
    except:
        hf_token = None
    
    if not hf_token:
        print("❌ No Hugging Face API key")
        return
    
    headers = {
        "Authorization": f"Bearer {hf_token}"
    }
    
    print("🧪 Testing Hugging Face Basic Access")
    print("=" * 40)
    
    # Test 1: Whoami
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)
        print(f"Whoami: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User: {user_info.get('name', 'Unknown')}")
        else:
            print(f"❌ {response.text}")
    except Exception as e:
        print(f"❌ Whoami error: {e}")
    
    # Test 2: List models (public)
    try:
        response = requests.get("https://huggingface.co/api/models", headers=headers, timeout=10)
        print(f"Models: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models)} public models")
        else:
            print(f"❌ {response.text}")
    except Exception as e:
        print(f"❌ Models error: {e}")
    
    # Test 3: Inference Providers
    try:
        response = requests.get("https://router.huggingface.co/v1/models", headers=headers, timeout=10)
        print(f"Inference: {response.status_code}")
        if response.status_code == 200:
            print("✅ Inference Providers available")
        else:
            print(f"❌ {response.text}")
    except Exception as e:
        print(f"❌ Inference error: {e}")

if __name__ == "__main__":
    test_hf_basic()
