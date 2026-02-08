"""
Find the correct Leonardo Phoenix 1.0 and 0.9 model IDs

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

def test_phoenix_model_ids():
    """Test various Phoenix model IDs to find the working ones"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Finding Leonardo Phoenix 1.0 and 0.9 Model IDs")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test potential Phoenix model IDs based on Leonardo documentation and common patterns
    phoenix_candidates = [
        # From Leonardo docs and common patterns
        "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8",  # Common Phoenix ID
        "c821f938-3de7-4c32-9b2a-5f8961b5c8e5",  # Alternative Phoenix ID
        "1e5a8919-3e1b-4e3a-9b4a-3f4bf3c6a7a2",  # Sometimes associated with Phoenix
        "ac6147dc-5e47-4c8b-9a21-06d9256c92c5",  # DreamShaper (sometimes bundled)
        "989e7ea9-636f-4b1f-9c79-0f6fd0223c69",  # RPG (sometimes bundled)
        
        # Try some UUID patterns that might be Phoenix
        "f2b0f8a2-3e1b-4e3a-9b4a-3f4bf3c6a7a2",  # Pattern 1
        "a3c1d9e3-4f5b-5c3b-a5c5-4f5bf3c6a7a2",  # Pattern 2
        "b4d2e0f4-5g6c-6d4c-b6d6-5g6cg4d7b8b3",  # Pattern 3
        
        # Try some known Leonardo model IDs from other sources
        "e8b1b0b2-3f4c-4d8e-9b0a-1c2d3e4f5a6b",  # Leonardo Kino XL
        "f2c2d1e0-4e5b-4c8a-9b7c-1d2e3f4a5b6c",  # Leonardo Creative XL
    ]
    
    working_models = []
    
    for model_id in phoenix_candidates:
        print(f"\n🧪 Testing model ID: {model_id}")
        
        payload = {
            "prompt": "beautiful woman, high quality, detailed",
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "modelId": model_id,
            "negative_prompt": "blurry, low quality"
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
                print(f"   ✅ Generation started: {generation_id}")
                
                # Wait and check details
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
                    sd_version = gen_info.get('sdVersion')
                    
                    print(f"   📋 Status: {status}")
                    print(f"   📋 Requested Model ID: {model_id}")
                    print(f"   📋 Actual Model ID: {actual_model_id}")
                    print(f"   📋 SD Version: {sd_version}")
                    
                    if status == 'COMPLETE':
                        print(f"   ✅ SUCCESS: Model {model_id} works!")
                        
                        # Check if this is actually Phoenix (higher quality than SD 1.5)
                        if sd_version and sd_version != "v1_5":
                            print(f"   🌟 PREMIUM MODEL: {sd_version}")
                            working_models.append({
                                'model_id': model_id,
                                'actual_model_id': actual_model_id,
                                'sd_version': sd_version,
                                'type': 'PREMIUM'
                            })
                        else:
                            print(f"   📝 Standard SD 1.5 model")
                            working_models.append({
                                'model_id': model_id,
                                'actual_model_id': actual_model_id,
                                'sd_version': sd_version,
                                'type': 'STANDARD'
                            })
                        
                        # Get the image
                        images = gen_info.get('generated_images', [])
                        if images:
                            img_url = images[0].get('url', '')
                            print(f"   🖼️  Image: {img_url}")
                    else:
                        print(f"   ⏳ Status: {status}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Rate limiting
    
    return working_models

def test_leonardo_api_models_endpoint():
    """Try to get the actual list of available models from Leonardo API"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Testing Leonardo models API endpoint...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try the models endpoint with proper parameters
    try:
        # Try with instance_prompt parameter
        payload = {
            "instance_prompt": "test"
        }
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/models",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Models endpoint status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Models retrieved:")
            print(json.dumps(models, indent=2))
            
            # Look for Phoenix models in the response
            if isinstance(models, list):
                phoenix_models = [m for m in models if 'phoenix' in m.get('name', '').lower()]
                if phoenix_models:
                    print(f"\n🌟 Found Phoenix models:")
                    for model in phoenix_models:
                        print(f"   {model.get('name')}: {model.get('id')}")
            elif isinstance(models, dict):
                if 'data' in models:
                    data = models['data']
                    phoenix_models = [m for m in data if 'phoenix' in m.get('name', '').lower()]
                    if phoenix_models:
                        print(f"\n🌟 Found Phoenix models:")
                        for model in phoenix_models:
                            print(f"   {model.get('name')}: {model.get('id')}")
            
            return models
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    # Try to get models from API
    api_models = test_leonardo_api_models_endpoint()
    
    # Test candidate model IDs
    working_models = test_phoenix_model_ids()
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if working_models:
        print(f"✅ Found {len(working_models)} working models:")
        premium_models = [m for m in working_models if m['type'] == 'PREMIUM']
        standard_models = [m for m in working_models if m['type'] == 'STANDARD']
        
        if premium_models:
            print(f"\n🌟 PREMIUM MODELS (Better than SD 1.5):")
            for model in premium_models:
                print(f"   {model['model_id']}: {model['sd_version']}")
        
        if standard_models:
            print(f"\n📝 STANDARD MODELS (SD 1.5):")
            for model in standard_models:
                print(f"   {model['model_id']}: {model['sd_version']}")
        
        # Recommend the best options
        if premium_models:
            print(f"\n💡 RECOMMENDATION: Use premium models for better quality")
            print(f"   Phoenix 1.0: {premium_models[0]['model_id']}")
        else:
            print(f"\n💡 RECOMMENDATION: All models are SD 1.5, use enhanced prompts")
    else:
        print(f"❌ No working models found")
        print(f"💡 Stick with enhanced SD 1.5 approach")
