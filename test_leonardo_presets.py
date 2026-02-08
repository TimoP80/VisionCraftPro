"""
Test all Leonardo preset styles to find the best quality ones

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

def test_all_preset_styles():
    """Test all available preset styles to find the best quality"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Testing All Leonardo Preset Styles")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test all possible preset styles
    preset_styles = [
        "LEONARDO",
        "CREATIVE", 
        "DYNAMIC",
        "CINEMATIC",
        "FANTASY_ART",
        "ANIME",
        "COMIC_BOOK",
        "PHOTOGRAPHIC",
        "ARTISTIC",
        "STEAMPUNK",
        "3D_RENDER",
        "ILLUSTRATION",
        "OIL_PAINTING",
        "WATERCOLOR",
        "PENCIL_SKETCH",
        "CONCEPT_ART",
        "HYPERREALISTIC",
        "VINTAGE",
        "MODERN",
        "CLASSIC"
    ]
    
    working_styles = []
    
    for style in preset_styles:
        print(f"\n🧪 Testing preset style: {style}")
        
        payload = {
            "prompt": "beautiful woman, high quality, detailed",
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "presetStyle": style,
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
                    preset_style_used = gen_info.get('presetStyle')
                    
                    print(f"   📋 Status: {status}")
                    print(f"   📋 Model ID: {actual_model_id}")
                    print(f"   📋 SD Version: {sd_version}")
                    print(f"   📋 Preset Style: {preset_style_used}")
                    
                    if status == 'COMPLETE':
                        print(f"   ✅ SUCCESS: {style} works!")
                        working_styles.append({
                            'style': style,
                            'model_id': actual_model_id,
                            'sd_version': sd_version,
                            'preset_style': preset_style_used
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
    
    return working_styles

def test_leonardo_models_endpoint():
    """Try to access the models endpoint with proper parameters"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Testing models endpoint with parameters...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try with name parameter
    try:
        payload = {"name": "test"}
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/models",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Models: {json.dumps(models, indent=2)}")
            return models
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    # Test models endpoint
    models = test_leonardo_models_endpoint()
    
    # Test all preset styles
    working_styles = test_all_preset_styles()
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if working_styles:
        print(f"✅ Found {len(working_styles)} working preset styles:")
        for style in working_styles:
            print(f"\n🎯 {style['style']}:")
            print(f"   Model ID: {style['model_id']}")
            print(f"   SD Version: {style['sd_version']}")
            print(f"   Preset Style: {style['preset_style']}")
        
        # Find the best styles (those that might use different models)
        unique_models = set(s['model_id'] for s in working_styles)
        if len(unique_models) > 1:
            print(f"\n🌟 Found multiple model types!")
        else:
            print(f"\n📝 All styles use the same model type")
    else:
        print(f"❌ No working preset styles found")
    
    if models:
        print(f"\n📋 Available Models:")
        print(json.dumps(models, indent=2))
