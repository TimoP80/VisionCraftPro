"""
Test Replicate API to check available models and find working ones

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import time

def load_api_keys():
    """Load API keys from file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def test_replicate_models():
    """Test various Replicate models to find working ones"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        print("❌ No Replicate API key found")
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Replicate Models")
    print("=" * 50)
    
    # Popular models with their correct versions
    models_to_test = [
        {
            "name": "FLUX.1-schnell",
            "version": "5599ed30703defd1d160a25a63326b5c3687e7eda6d971825cb8ec9185570756",
            "params": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 3.5,
                "num_inference_steps": 4,
                "max_sequence_length": 512
            }
        },
        {
            "name": "FLUX.1-dev",
            "version": "d8ae2ddc05e5a8e7ed6522a5f8793a775a3b4178c4c4e0a3e6f8f2a3b4c5d6e",
            "params": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 3.5,
                "num_inference_steps": 4,
                "max_sequence_length": 512
            }
        },
        {
            "name": "Stable Diffusion XL",
            "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            "params": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 20
            }
        },
        {
            "name": "DreamShaper",
            "version": "c221b2a8bf51958b5abde89201d3cfbebc3bc8ff8869ad864fedd8034945e5f",
            "params": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 25
            }
        },
        {
            "name": "Absolute Reality",
            "version": "b132a827a3a6535f3d2e0e8c2a6e3078758b620e6e6e6e6e6e6e6e6e6e6e6e6e6e6e",
            "params": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 25
            }
        },
        {
            "name": "Stable Diffusion 2.1",
            "version": "43606fa6b977c151e18e32c27dd6fd3690a5b3a5ab9bcf727d8a4fa1d07704e",
            "params": {
                "prompt": "beautiful woman, high quality, detailed",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 25
            }
        }
    ]
    
    working_models = []
    
    for model in models_to_test:
        print(f"\n🔍 Testing: {model['name']}")
        
        payload = {
            "version": model["version"],
            "input": model["params"]
        }
        
        try:
            # Start generation
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                prediction_id = result['id']
                print(f"   ✅ Generation started: {prediction_id}")
                print(f"   📋 Status: {result['status']}")
                
                # Poll for completion
                get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                
                for i in range(30):  # Poll for 30 seconds
                    time.sleep(1)
                    get_response = requests.get(get_url, headers=headers)
                    
                    if get_response.status_code == 200:
                        result_data = get_response.json()
                        status = result_data.get('status')
                        
                        if status == 'succeeded':
                            print(f"   ✅ Generation completed!")
                            outputs = result_data.get('output', [])
                            if outputs:
                                print(f"   🖼️  Image URL: {outputs[0]}")
                                working_models.append(model['name'])
                                break
                        elif status == 'failed':
                            error = result_data.get('error', 'Unknown error')
                            print(f"   ❌ Generation failed: {error}")
                            break
                        else:
                            print(f"   ⏳ Status: {status}")
                    else:
                        print(f"   ❌ Polling failed: {get_response.status_code}")
                        break
                else:
                    print(f"   ⏰ Timeout after 30 seconds")
            else:
                error_text = response.text
                print(f"   ❌ Failed: {error_text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    if working_models:
        print(f"✅ Working models: {', '.join(working_models)}")
        print(f"💡 Ready to integrate these models into VisionCraft Pro")
    else:
        print(f"❌ No working models found")
        print(f"💡 Check API key permissions or try different models")

def test_replicate_account():
    """Test Replicate account info"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        print("❌ No Replicate API key found")
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing Replicate Account")
    print("=" * 50)
    
    try:
        response = requests.get("https://api.replicate.com/v1/account", headers=headers, timeout=30)
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Account: {account.get('username', 'Unknown')}")
            print(f"💳 Plan: {account.get('plan', 'Unknown')}")
            print(f"📊 Usage: {account.get('usage', 'Unknown')}")
        else:
            print(f"❌ Account check failed: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_replicate_account()
    test_replicate_models()
