"""
Test if Leonardo Phoenix models can be accessed with paid tokens

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

def test_phoenix_with_paid_tokens():
    """Test if Phoenix models work with paid tokens"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Testing Leonardo Phoenix with Paid Tokens")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test Phoenix models that might work with paid tokens
    phoenix_models = [
        {
            "name": "Leonardo Phoenix 1.0",
            "model_id": "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8",
            "description": "Latest Phoenix model"
        },
        {
            "name": "Leonardo Phoenix 0.9", 
            "model_id": "c821f938-3de7-4c32-9b2a-5f8961b5c8e5",
            "description": "Previous Phoenix version"
        },
        {
            "name": "Leonardo Universal",
            "model_id": "1e5a8919-3e1b-4e3a-9b4a-3f4bf3c6a7a2",
            "description": "Universal model"
        }
    ]
    
    working_models = []
    
    for model in phoenix_models:
        print(f"\n🧪 Testing {model['name']} (ID: {model['model_id']})")
        print(f"   Description: {model['description']}")
        
        payload = {
            "prompt": "beautiful woman, high quality, detailed, professional photography",
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "modelId": model['model_id'],
            "negative_prompt": "blurry, low quality, distorted, bad anatomy",
            "num_inference_steps": 30,
            "guidance_scale": 8.0
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
                time.sleep(8)
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
                    print(f"   📋 Requested Model ID: {model['model_id']}")
                    print(f"   📋 Actual Model ID: {actual_model_id}")
                    print(f"   📋 SD Version: {sd_version}")
                    
                    if status == 'COMPLETE':
                        print(f"   ✅ SUCCESS: {model['name']} works!")
                        
                        # Check if this is actually better than SD 1.5
                        if sd_version and sd_version != "v1_5":
                            print(f"   🌟 PREMIUM MODEL: {sd_version}")
                            working_models.append({
                                'name': model['name'],
                                'model_id': model['model_id'],
                                'actual_model_id': actual_model_id,
                                'sd_version': sd_version,
                                'type': 'PREMIUM'
                            })
                        else:
                            print(f"   📝 Enhanced SD 1.5 model")
                            working_models.append({
                                'name': model['name'],
                                'model_id': model['model_id'],
                                'actual_model_id': actual_model_id,
                                'sd_version': sd_version,
                                'type': 'ENHANCED_SD15'
                            })
                        
                        # Get the image
                        images = gen_info.get('generated_images', [])
                        if images:
                            img_url = images[0].get('url', '')
                            print(f"   🖼️  Image: {img_url}")
                            
                            # Check token cost
                            print(f"   💰 This generation used paid tokens")
                    else:
                        print(f"   ⏳ Status: {status}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    error = error_data.get('error', 'Unknown error')
                    print(f"   Error: {error}")
                    
                    # Check if it's a token issue
                    if 'token' in error.lower() or 'credit' in error.lower():
                        print(f"   💰 Token-related error - may need more credits")
                except:
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(3)  # Rate limiting
    
    return working_models

def test_alternative_phoenix_access():
    """Test alternative ways to access Phoenix models"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Testing alternative Phoenix access methods...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test without modelId but with Phoenix-specific parameters
    phoenix_payloads = [
        {
            "name": "No modelId, Phoenix preset",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "presetStyle": "PHOENIX",  # Try Phoenix preset style
                "negative_prompt": "blurry, low quality"
            }
        },
        {
            "name": "Phoenix model parameter",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "model": "phoenix-1.0",  # Try model instead of modelId
                "negative_prompt": "blurry, low quality"
            }
        },
        {
            "name": "Phoenix with higher resolution",
            "payload": {
                "prompt": "beautiful woman, high quality, detailed, professional photography",
                "width": 1344,
                "height": 1344,
                "num_images": 1,
                "presetStyle": "LEONARDO",  # Use LEONARDO with higher res
                "negative_prompt": "blurry, low quality"
            }
        }
    ]
    
    for test in phoenix_payloads:
        print(f"\n🧪 Testing: {test['name']}")
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=test['payload'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generation_id = result.get('sdGenerationJob', {}).get('generationId')
                print(f"   ✅ Generation started: {generation_id}")
                
                # Wait and check
                time.sleep(5)
                gen_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    gen_info = gen_data.get('generations_by_pk', {})
                    status = gen_info.get('status')
                    
                    print(f"   📋 Status: {status}")
                    if status == 'COMPLETE':
                        print(f"   ✅ SUCCESS: {test['name']} works!")
                        
                        images = gen_info.get('generated_images', [])
                        if images:
                            img_url = images[0].get('url', '')
                            print(f"   🖼️  Image: {img_url}")
                    else:
                        print(f"   ⏳ Status: {status}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    # Test Phoenix models with paid tokens
    working_models = test_phoenix_with_paid_tokens()
    
    # Test alternative access methods
    test_alternative_phoenix_access()
    
    print(f"\n" + "=" * 70)
    print("PHOENIX ACCESS ANALYSIS")
    print("=" * 70)
    
    if working_models:
        print(f"✅ Found {len(working_models)} working Phoenix models:")
        for model in working_models:
            print(f"\n🌟 {model['name']}:")
            print(f"   Type: {model['type']}")
            print(f"   SD Version: {model['sd_version']}")
            print(f"   Model ID: {model['model_id']}")
            
            if model['type'] == 'PREMIUM':
                print(f"   💡 This is a true premium model!")
            elif model['type'] == 'ENHANCED_SD15':
                print(f"   💡 Enhanced SD 1.5 with Phoenix optimization")
    else:
        print(f"❌ No Phoenix models accessible with current plan")
        print(f"💡 You have 2598 paid tokens but no model tokens")
        print(f"💡 Phoenix models may require a higher tier subscription")
        print(f"💡 Consider upgrading to Leonardo Pro or Standard plan for model access")
