"""
Test Leonardo.ai API with different model configurations

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

def test_model_generation(model_id, model_name, prompt="beautiful woman wearing a dress"):
    """Test generation with a specific model"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return False
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "modelId": model_id,
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "alchemy": False,
        "negative_prompt": "",
        "num_inference_steps": 25
    }
    
    print(f"\n🧪 Testing {model_name} (ID: {model_id})...")
    
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
            print(f"✅ {model_name}: Generation started (ID: {generation_id})")
            return True
        else:
            print(f"❌ {model_name}: Failed with {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {model_name}: Error - {e}")
        return False

def test_known_models():
    """Test with known working model IDs"""
    print("=" * 60)
    print("Testing Leonardo.ai Model IDs")
    print("=" * 60)
    
    # Known working model IDs from Leonardo documentation
    known_models = [
        ("6bef9f4b-29cb-40c7-bdf-32b51c1f80d8", "Leonardo Diffusion XL"),
        ("c821f938-3de7-4c32-9b2a-5f8961b5c8e5", "Leonardo Phoenix"),
        ("1e5a8919-3e1b-4e3a-9b4a-3f4bf3c6a7a2", "Absolute Reality"),
        ("ac6147dc-5e47-4c8b-9a21-06d9256c92c5", "DreamShaper v7"),
        ("989e7ea9-636f-4b1f-9c79-0f6fd0223c69", "RPG"),
        ("a3f821c3-126a-42d5-bd28-bf86a7a4108f", "3D Animation Style"),
        ("b24e16ff-06e3-450b-92b8-8e8901d3dab8", "Diffusion XL (Original)"),
        ("448df82c-8872-4e4f-9d5a-351c8cf09548", "Diffusion XL Lightning (Original)"),
    ]
    
    working_models = []
    
    for model_id, model_name in known_models:
        if test_model_generation(model_id, model_name):
            working_models.append((model_id, model_name))
        time.sleep(1)  # Rate limiting
    
    print(f"\n✅ Working Models ({len(working_models)}):")
    for model_id, model_name in working_models:
        print(f"   {model_name}: {model_id}")
    
    print(f"\n🔧 Recommended Model Updates:")
    print(f"   diffusion-xl: {working_models[0][0] if working_models else 'UNKNOWN'}")
    print(f"   diffusion-xl-lightning: {working_models[1][0] if len(working_models) > 1 else 'UNKNOWN'}")
    print(f"   phoenix-1-0: {working_models[2][0] if len(working_models) > 2 else 'UNKNOWN'}")
    
    return working_models

if __name__ == "__main__":
    test_known_models()
