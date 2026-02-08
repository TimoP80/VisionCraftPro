"""
Test Replicate API with correct model versions from their website

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

def test_replicate_simple():
    """Test Replicate with a simple, working model"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        print("❌ No Replicate API key found")
        return False
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Replicate with Simple Model")
    print("=" * 50)
    
    # Use a known working model from Replicate
    # This is the correct version for FLUX.1-schnell
    payload = {
        "version": "5599ed30703defd1d160a25a63326b5c3687e7eda6d971825cb8ec9185570756",
        "input": {
            "prompt": "beautiful woman, high quality, detailed",
            "width": 512,
            "height": 512,
            "num_outputs": 1,
            "guidance_scale": 3.5,
            "num_inference_steps": 4,
            "max_sequence_length": 512
        }
    }
    
    try:
        print("📸 Starting generation...")
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            prediction_id = result['id']
            print(f"✅ Generation started: {prediction_id}")
            print(f"📋 Status: {result['status']}")
            
            # Poll for completion
            get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            
            for i in range(60):  # Poll for 60 seconds
                time.sleep(1)
                get_response = requests.get(get_url, headers=headers)
                
                if get_response.status_code == 200:
                    result_data = get_response.json()
                    status = result_data.get('status')
                    
                    if status == 'succeeded':
                        print(f"✅ Generation completed!")
                        outputs = result_data.get('output', [])
                        if outputs:
                            print(f"🖼️  Image URL: {outputs[0]}")
                            return True
                        else:
                            print(f"❌ No image in output")
                            return False
                    elif status == 'failed':
                        error = result_data.get('error', 'Unknown error')
                        print(f"❌ Generation failed: {error}")
                        return False
                    elif status == 'processing':
                        if i % 10 == 0:  # Print every 10 seconds
                            print(f"⏳ Processing... ({i+1}s)")
                    else:
                        print(f"⏳ Status: {status}")
                else:
                    print(f"❌ Polling failed: {get_response.status_code}")
                    return False
            else:
                print(f"⏰ Timeout after 60 seconds")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_replicate_alternative():
    """Test with an alternative model"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        return False
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Testing Alternative Model")
    print("=" * 50)
    
    # Try with Stable Diffusion XL (known working version)
    payload = {
        "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
        "input": {
            "prompt": "beautiful woman, high quality, detailed",
            "width": 512,
            "height": 512,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 20
        }
    }
    
    try:
        print("📸 Starting SDXL generation...")
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            prediction_id = result['id']
            print(f"✅ Generation started: {prediction_id}")
            
            # Poll for completion (shorter for this test)
            get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            
            for i in range(30):  # Poll for 30 seconds
                time.sleep(1)
                get_response = requests.get(get_url, headers=headers)
                
                if get_response.status_code == 200:
                    result_data = get_response.json()
                    status = result_data.get('status')
                    
                    if status == 'succeeded':
                        print(f"✅ SDXL Generation completed!")
                        outputs = result_data.get('output', [])
                        if outputs:
                            print(f"🖼️  Image URL: {outputs[0]}")
                            return True
                    elif status == 'failed':
                        error = result_data.get('error', 'Unknown error')
                        print(f"❌ SDXL failed: {error}")
                        return False
                    else:
                        if i % 5 == 0:  # Print every 5 seconds
                            print(f"⏳ SDXL Status: {status} ({i+1}s)")
                else:
                    print(f"❌ SDXL polling failed: {get_response.status_code}")
                    return False
            else:
                print(f"⏰ SDXL timeout after 30 seconds")
                return False
        else:
            print(f"❌ SDXL failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SDXL error: {e}")
        return False

def get_replicate_models():
    """Get list of available models from Replicate"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📋 Getting Available Models")
    print("=" * 50)
    
    try:
        response = requests.get("https://api.replicate.com/v1/collections/text-to-image", headers=headers, timeout=30)
        
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections.get('results', []))} collections")
            
            for collection in collections.get('results', [])[:3]:  # Show first 3
                print(f"\n📁 Collection: {collection.get('name', 'Unknown')}")
                models = collection.get('models', [])
                for model in models[:3]:  # Show first 3 models
                    print(f"   🎨 {model.get('name', 'Unknown')}")
                    print(f"      📝 {model.get('description', 'No description')[:80]}...")
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Replicate API Test (Correct Versions)")
    print("=" * 50)
    
    # Test simple model first
    success1 = test_replicate_simple()
    
    # Wait a bit to avoid rate limiting
    if not success1:
        time.sleep(2)
        success2 = test_replicate_alternative()
    
    # Get available models
    get_replicate_models()
    
    print(f"\n" + "=" * 50)
    if success1:
        print("✅ Replicate is working! Ready for integration")
    else:
        print("❌ Replicate test failed")
        print("💡 Check rate limits or try different models")
