"""
Find the actual working Leonardo.ai models for premium quality

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os
import time

def load_api_key():
    """Load Leonardo API key"""
    try:
        with open('api_keys.json', 'r') as f:
            keys = json.load(f)
            return keys.get('leonardo-api')
    except:
        return None

def test_leonardo_without_model():
    """Test Leonardo without specifying model to see what we get"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Testing Leonardo.ai Default Model")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test with no model ID
    payload = {
        "prompt": "beautiful woman, photorealistic, high quality, detailed",
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "presetStyle": "CREATIVE"
    }
    
    try:
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generation_id = result.get('sdGenerationJob', {}).get('generationId')
            print(f"✅ Generation started: {generation_id}")
            
            # Wait and check details
            time.sleep(5)
            gen_response = requests.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers=headers
            )
            
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                gen_info = gen_data.get('generations_by_pk', {})
                
                print(f"📋 Generation Details:")
                print(f"   Model ID: {gen_info.get('modelId')}")
                print(f"   SD Version: {gen_info.get('sdVersion')}")
                print(f"   Preset Style: {gen_info.get('presetStyle')}")
                print(f"   Status: {gen_info.get('status')}")
                
                # Get the actual image
                if gen_info.get('status') == 'COMPLETE':
                    images = gen_info.get('generated_images', [])
                    if images:
                        img_url = images[0].get('url', '')
                        print(f"   🖼️  Image URL: {img_url}")
                        
                        # Try to get model info from the generation
                        print(f"\n🔍 Analyzing default model quality...")
                        return gen_info
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_leonardo_user_models():
    """Test if user has access to specific models"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Checking user's available models...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try to get user models (this might work with POST)
    try:
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/models",
            headers=headers,
            json={},
            timeout=30
        )
        
        print(f"User models response: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ User models: {models}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_specific_model_ids():
    """Test specific model IDs that might work"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🧪 Testing specific model IDs...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test some common Leonardo model IDs
    test_models = [
        # Try some common Leonardo model IDs
        "1e5a8919-3e1b-4e3a-9b4a-3f4bf3c6a7a2",  # Absolute Reality
        "ac6147dc-5e47-4c8b-9a21-06d9256c92c5",  # DreamShaper
        "989e7ea9-636f-4b1f-9c79-0f6fd0223c69",  # RPG
        "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8",  # Universal
        "c821f938-3de7-4c32-9b2a-5f8961b5c8e5",  # Phoenix
    ]
    
    for model_id in test_models:
        print(f"\n🧪 Testing model ID: {model_id}")
        
        payload = {
            "prompt": "test image",
            "width": 512,
            "height": 512,
            "num_images": 1,
            "modelId": model_id
        }
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ Model {model_id}: WORKING!")
                return model_id
            else:
                print(f"   ❌ Model {model_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error with {model_id}: {e}")
        
        time.sleep(1)
    
    return None

def check_leonardo_plan():
    """Check what Leonardo plan the user has"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Checking Leonardo account details...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try different endpoints to get user info
    endpoints = [
        "https://cloud.leonardo.ai/api/rest/v1/user",
        "https://cloud.leonardo.ai/api/rest/v1/me",
        "https://cloud.leonardo.ai/api/rest/v1/account"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ User info from {endpoint}:")
                print(json.dumps(user_data, indent=2))
                return user_data
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error with {endpoint}: {e}")

if __name__ == "__main__":
    # Test default model
    default_info = test_leonardo_without_model()
    
    # Check user models
    test_leonardo_user_models()
    
    # Test specific model IDs
    working_model = test_specific_model_ids()
    
    # Check account details
    check_leonardo_plan()
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if default_info:
        print(f"✅ Default model working: {default_info.get('sdVersion')}")
    
    if working_model:
        print(f"✅ Working model found: {working_model}")
    else:
        print(f"❌ No specific models working")
    
    print(f"\n💡 Recommendation:")
    if working_model:
        print(f"Use the working model ID: {working_model}")
    else:
        print(f"Stick with default model but enhance prompts and use preset styles")
