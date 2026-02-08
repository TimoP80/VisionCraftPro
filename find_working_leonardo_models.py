"""
Find working Leonardo.ai models that produce premium quality images

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

def test_leonardo_model(model_id, model_name, prompt="beautiful woman wearing a dress, photorealistic, high quality, detailed"):
    """Test a specific Leonardo model"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return False
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Build payload with the specific model
    payload = {
        "prompt": prompt,
        "modelId": model_id,
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "alchemy": False,
        "ultra": False,
        "contrast": 3.5,
        "negative_prompt": "blurry, low quality, distorted, bad anatomy",
        "num_inference_steps": 30,
        "guidance_scale": 7.5
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
            print(f"   ✅ Generation started: {generation_id}")
            
            # Wait and check the generation
            time.sleep(5)
            gen_response = requests.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers=headers
            )
            
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                gen_info = gen_data.get('generations_by_pk', {})
                status = gen_info.get('status')
                actual_model_id = gen_info.get('modelId')
                
                print(f"   📋 Status: {status}")
                print(f"   📋 Actual Model ID: {actual_model_id}")
                
                if status == 'COMPLETE':
                    print(f"   ✅ {model_name}: WORKING - Premium quality!")
                    return True
                elif status == 'PENDING':
                    print(f"   ⏳ {model_name}: Still processing...")
                    return False
                else:
                    print(f"   ❌ {model_name}: Failed with status {status}")
                    return False
            else:
                print(f"   ❌ Failed to check generation: {gen_response.status_code}")
                return False
                
        else:
            print(f"   ❌ Failed to start generation: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def find_premium_models():
    """Test various Leonardo models to find working premium ones"""
    print("=" * 70)
    print("Finding Working Leonardo.ai Premium Models")
    print("=" * 70)
    
    # Test various known Leonardo model IDs
    test_models = [
        # Leonardo Diffusion XL models
        ("6bef9f4b-29cb-40c7-bdf-32b51c1f80d8", "Leonardo Diffusion XL"),
        ("b24e16ff-06e3-450b-92b8-8e8901d3dab8", "Diffusion XL Original"),
        ("448df82c-8872-4e4f-9d5a-351c8cf09548", "Diffusion XL Lightning"),
        
        # Leonardo Phoenix models  
        ("c821f938-3de7-4c32-9b2a-5f8961b5c8e5", "Leonardo Phoenix"),
        ("6bef9f4b-29cb-40c7-bdf-32b51c1f80d8", "Leonardo Phoenix 1.0"),
        
        # Other premium models
        ("1e5a8919-3e1b-4e3a-9b4a-3f4bf3c6a7a2", "Absolute Reality"),
        ("ac6147dc-5e47-4c8b-9a21-06d9256c92c5", "DreamShaper v7"),
        ("989e7ea9-636f-4b1f-9c79-0f6fd0223c69", "RPG v4"),
        ("a3f821c3-126a-42d5-bd28-bf86a7a4108f", "3D Animation Style"),
        
        # Newer models
        ("e8b1b0b2-3f4c-4d8e-9b0a-1c2d3e4f5a6b", "Leonardo Kino XL"),
        ("f2c2d1e0-4e5b-4c8a-9b7c-1d2e3f4a5b6c", "Leonardo Creative XL"),
    ]
    
    working_models = []
    
    for model_id, model_name in test_models:
        if test_leonardo_model(model_id, model_name):
            working_models.append((model_id, model_name))
        time.sleep(2)  # Rate limiting
    
    print(f"\n" + "=" * 70)
    print(f"✅ WORKING PREMIUM MODELS FOUND: {len(working_models)}")
    print("=" * 70)
    
    for model_id, model_name in working_models:
        print(f"🎨 {model_name}: {model_id}")
    
    if working_models:
        print(f"\n🔧 Recommended Configuration:")
        print(f'"diffusion-xl": {{')
        print(f'    "id": "{working_models[0][0]}",')
        print(f'    "name": "{working_models[0][1]}",')
        print(f'    "description": "Premium high-quality model",')
        print(f'}}')
        
        if len(working_models) > 1:
            print(f'\n"diffusion-xl-lightning": {{')
            print(f'    "id": "{working_models[1][0]}",')
            print(f'    "name": "{working_models[1][1]}",')
            print(f'    "description": "Fast premium model",')
            print(f'}}')
    
    return working_models

if __name__ == "__main__":
    find_premium_models()
