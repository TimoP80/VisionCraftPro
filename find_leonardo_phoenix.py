"""
Find and restore the actual Leonardo Phoenix model

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

def test_leonardo_phoenix_models():
    """Test various ways to access Leonardo Phoenix model"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Finding Leonardo Phoenix Model")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test different approaches to get Leonardo Phoenix
    test_approaches = [
        {
            "name": "Phoenix with modelId (old way)",
            "payload": {
                "prompt": "beautiful woman, high quality",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "modelId": "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8"  # Phoenix ID
            }
        },
        {
            "name": "Phoenix with modelId (alternative)",
            "payload": {
                "prompt": "beautiful woman, high quality",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "modelId": "c821f938-3de7-4c32-9b2a-5f8961b5c8e5"  # Alternative Phoenix ID
            }
        },
        {
            "name": "Phoenix with model parameter",
            "payload": {
                "prompt": "beautiful woman, high quality",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "model": "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8"  # Try model instead of modelId
            }
        },
        {
            "name": "Leonardo Diffusion XL",
            "payload": {
                "prompt": "beautiful woman, high quality",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "modelId": "b24e16ff-06e3-450b-92b8-8e8901d3dab8"  # Diffusion XL
            }
        },
        {
            "name": "With presetStyle Leonardo",
            "payload": {
                "prompt": "beautiful woman, high quality",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "presetStyle": "LEONARDO"  # Try Leonardo preset style
            }
        }
    ]
    
    working_approaches = []
    
    for approach in test_approaches:
        print(f"\n🧪 Testing: {approach['name']}")
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=approach['payload'],
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
                    print(f"   📋 Actual Model ID: {actual_model_id}")
                    print(f"   📋 SD Version: {sd_version}")
                    
                    if status == 'COMPLETE':
                        print(f"   ✅ SUCCESS: {approach['name']} works!")
                        working_approaches.append({
                            'name': approach['name'],
                            'payload': approach['payload'],
                            'actual_model_id': actual_model_id,
                            'sd_version': sd_version
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
    
    return working_approaches

def check_leonardo_model_endpoint():
    """Check if there's a way to list available models"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Checking Leonardo model endpoints...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try different endpoints
    endpoints = [
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/platform/models"),
        ("POST", "https://cloud.leonardo.ai/api/rest/v1/platform/models"),
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/models"),
        ("POST", "https://cloud.leonardo.ai/api/rest/v1/models"),
    ]
    
    for method, endpoint in endpoints:
        print(f"\n🔍 Trying {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(endpoint, headers=headers, timeout=10)
            else:
                response = requests.post(endpoint, headers=headers, json={}, timeout=10)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {len(data) if isinstance(data, list) else 'data'} items")
                    if isinstance(data, list) and data:
                        print(f"   Sample: {data[0]}")
                    elif isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    # Check model endpoints
    check_leonardo_model_endpoint()
    
    # Test Phoenix approaches
    working_approaches = test_leonardo_phoenix_models()
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if working_approaches:
        print(f"✅ Found {len(working_approaches)} working approaches:")
        for approach in working_approaches:
            print(f"\n🎯 {approach['name']}:")
            print(f"   Model ID: {approach['actual_model_id']}")
            print(f"   SD Version: {approach['sd_version']}")
            print(f"   Payload: {json.dumps(approach['payload'], indent=6)}")
    else:
        print(f"❌ No working approaches found for Leonardo Phoenix")
        print(f"💡 Recommendation: Stick with enhanced SD 1.5 approach")
