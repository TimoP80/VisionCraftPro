"""
Update Leonardo.ai model configuration with correct model IDs

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

def test_preset_styles():
    """Test different preset styles to see what models they use"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 60)
    print("Testing Leonardo.ai Preset Styles")
    print("=" * 60)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test different preset styles
    preset_styles = [
        "CREATIVE",
        "DYNAMIC", 
        "ARTISTIC",
        "PHOTOGRAPHIC",
        "CINEMATIC",
        "FANTASY_ART",
        "STEAMPUNK",
        "ANIME",
        "COMIC_BOOK",
        "3D_RENDER"
    ]
    
    for style in preset_styles:
        print(f"\n🎨 Testing style: {style}")
        
        payload = {
            "prompt": "beautiful woman",
            "width": 512,
            "height": 512,
            "num_images": 1,
            "presetStyle": style,
            "negative_prompt": ""
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
                
                # Wait a moment and check the generation details
                time.sleep(2)
                gen_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    gen_info = gen_data.get('generations_by_pk', {})
                    model_id = gen_info.get('modelId')
                    sd_version = gen_info.get('sdVersion')
                    preset_style = gen_info.get('presetStyle')
                    
                    print(f"   📋 Model ID: {model_id}")
                    print(f"   📋 SD Version: {sd_version}")
                    print(f"   📋 Preset Style: {preset_style}")
                    
                    if model_id:
                        print(f"   ✅ Found working model ID!")
                        
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_sd_versions():
    """Test different SD versions"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Testing SD versions...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test different SD versions
    sd_versions = ["v1_5", "v2", "sd_xl_base", "sd_xl_lightning"]
    
    for version in sd_versions:
        print(f"\n🧪 Testing SD version: {version}")
        
        payload = {
            "prompt": "beautiful woman",
            "width": 512,
            "height": 512,
            "num_images": 1,
            "sdVersion": version
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
                
                # Check generation details
                time.sleep(2)
                gen_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    gen_info = gen_data.get('generations_by_pk', {})
                    actual_model_id = gen_info.get('modelId')
                    actual_sd_version = gen_info.get('sdVersion')
                    
                    print(f"   📋 Actual Model ID: {actual_model_id}")
                    print(f"   📋 Actual SD Version: {actual_sd_version}")
                    
                    if actual_model_id:
                        print(f"   ✅ Found working model ID!")
                        
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)

def generate_updated_model_config():
    """Generate updated model configuration"""
    print(f"\n🔧 Generating updated model configuration...")
    
    # Based on testing, here are the working configurations
    updated_config = {
        "phoenix-1-0": {
            "id": None,  # Don't specify model ID, let Leonardo choose
            "name": "Leonardo Phoenix (Default)",
            "description": "Default Leonardo model with SD 1.5",
            "max_resolution": (1024, 1024),
            "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"]
        },
        "phoenix-0-9": {
            "id": None,  # Use default
            "name": "Leonardo Legacy",
            "description": "Legacy Leonardo model",
            "max_resolution": (1024, 1024),
            "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"]
        },
        "universal": {
            "id": None,  # Use default
            "name": "Universal",
            "description": "Universal model for all image types",
            "max_resolution": (1024, 1024),
            "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"]
        },
        # Remove the problematic XL models for now
    }
    
    print(f"✅ Updated configuration:")
    for key, model in updated_config.items():
        print(f"   {key}: {model['name']} (ID: {model['id']})")
    
    return updated_config

if __name__ == "__main__":
    test_preset_styles()
    test_sd_versions()
    generate_updated_model_config()
