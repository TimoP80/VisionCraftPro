"""
Test Leonardo.ai quality settings to achieve premium results

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

def test_quality_settings():
    """Test different quality settings to find premium configuration"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Testing Leonardo.ai Quality Settings")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test different quality configurations
    quality_configs = [
        {
            "name": "Standard Quality",
            "payload": {
                "prompt": "beautiful woman wearing a dress, photorealistic, high quality, detailed, 8k",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "alchemy": False,
                "ultra": False,
                "contrast": 3.5,
                "negative_prompt": "blurry, low quality, distorted, bad anatomy, jpeg artifacts",
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }
        },
        {
            "name": "High Quality",
            "payload": {
                "prompt": "beautiful woman wearing a dress, photorealistic, high quality, detailed, 8k, professional photography",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "alchemy": False,
                "ultra": True,  # Enable ultra quality
                "contrast": 4.0,  # Higher contrast
                "negative_prompt": "blurry, low quality, distorted, bad anatomy, jpeg artifacts, amateur",
                "num_inference_steps": 30,
                "guidance_scale": 8.0
            }
        },
        {
            "name": "Premium Quality",
            "payload": {
                "prompt": "beautiful woman wearing an elegant dress, photorealistic, ultra high quality, highly detailed, 8k resolution, professional photography, cinematic lighting",
                "width": 1344,  # Higher resolution
                "height": 1344,
                "num_images": 1,
                "alchemy": True,  # Enable alchemy
                "ultra": True,   # Enable ultra quality
                "contrast": 4.5,  # Maximum contrast
                "negative_prompt": "blurry, low quality, distorted, bad anatomy, jpeg artifacts, amateur, oversaturated",
                "num_inference_steps": 40,
                "guidance_scale": 10.0
            }
        },
        {
            "name": "Creative Style",
            "payload": {
                "prompt": "beautiful woman wearing a dress, photorealistic, high quality, detailed, 8k, professional photography, cinematic lighting",
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "alchemy": False,
                "ultra": True,
                "contrast": 3.5,
                "presetStyle": "CREATIVE",  # Add preset style
                "negative_prompt": "blurry, low quality, distorted, bad anatomy, jpeg artifacts",
                "num_inference_steps": 30,
                "guidance_scale": 8.0
            }
        },
        {
            "name": "Cinematic Style",
            "payload": {
                "prompt": "beautiful woman wearing an elegant dress, photorealistic, ultra high quality, highly detailed, 8k resolution, professional photography, cinematic lighting, film grain",
                "width": 1344,
                "height": 768,  # Widescreen
                "num_images": 1,
                "alchemy": False,
                "ultra": True,
                "contrast": 4.0,
                "presetStyle": "CINEMATIC",  # Cinematic preset
                "negative_prompt": "blurry, low quality, distorted, bad anatomy, jpeg artifacts, amateur, flat lighting",
                "num_inference_steps": 35,
                "guidance_scale": 9.0
            }
        }
    ]
    
    for config in quality_configs:
        print(f"\n🧪 Testing {config['name']}...")
        print(f"   Settings: ultra={config['payload'].get('ultra', False)}, alchemy={config['payload'].get('alchemy', False)}")
        print(f"   Steps: {config['payload'].get('num_inference_steps', 20)}, Guidance: {config['payload'].get('guidance_scale', 7.5)}")
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=config['payload'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generation_id = result.get('sdGenerationJob', {}).get('generationId')
                print(f"   ✅ Generation started: {generation_id}")
                
                # Wait and check the generation
                time.sleep(8)
                gen_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    gen_info = gen_data.get('generations_by_pk', {})
                    status = gen_info.get('status')
                    
                    if status == 'COMPLETE':
                        print(f"   ✅ {config['name']}: SUCCESS - Premium quality achieved!")
                        
                        # Check image details
                        images = gen_info.get('generated_images', [])
                        if images:
                            img_url = images[0].get('url', '')
                            print(f"   🖼️  Image URL: {img_url}")
                        
                        return config  # Return the first successful config
                    elif status == 'PENDING':
                        print(f"   ⏳ {config['name']}: Still processing...")
                    else:
                        print(f"   ❌ {config['name']}: Failed with status {status}")
                else:
                    print(f"   ❌ Failed to check generation: {gen_response.status_code}")
            else:
                print(f"   ❌ Failed to start generation: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(3)  # Rate limiting
    
    print(f"\n❌ No premium quality configuration found")
    return None

def get_current_generation_details():
    """Check details of current generation to understand what model is being used"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Checking current generation details...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Start a simple generation
    payload = {
        "prompt": "test image",
        "width": 512,
        "height": 512,
        "num_images": 1
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
            
            # Check the generation details
            time.sleep(3)
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
                
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_current_generation_details()
    best_config = test_quality_settings()
    
    if best_config:
        print(f"\n🎯 RECOMMENDED CONFIGURATION:")
        print(f"Name: {best_config['name']}")
        print(json.dumps(best_config['payload'], indent=2))
