"""
Test Image Generation APIs for VisionCraft Pro
Tests Replicate, fal.ai, and Hugging Face APIs

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os
import time

def load_api_keys():
    """Load API keys from file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def test_replicate_api():
    """Test Replicate API"""
    print("=" * 60)
    print("Testing Replicate API")
    print("=" * 60)
    
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        print("❌ No Replicate API key found")
        print("💡 Add to api_keys.json: {\"replicate-api\": \"your_key_here\"}")
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    # Test with FLUX.1-schnell (fast, affordable)
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
        print("🧪 Testing FLUX.1-schnell generation...")
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Generation started: {result['id']}")
            print(f"📋 Status: {result['status']}")
            
            # Poll for completion
            get_url = f"https://api.replicate.com/v1/predictions/{result['id']}"
            
            for i in range(30):  # Poll for 30 seconds
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
                    elif status == 'failed':
                        print(f"❌ Generation failed: {result_data.get('error')}")
                        return False
                    else:
                        print(f"⏳ Status: {status}")
                else:
                    print(f"❌ Polling failed: {get_response.status_code}")
                    return False
            else:
                print(f"⏰ Timeout after 30 seconds")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fal_api():
    """Test fal.ai API"""
    print(f"\n" + "=" * 60)
    print("Testing fal.ai API")
    print("=" * 60)
    
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        print("💡 Add to api_keys.json: {\"fal-api\": \"your_key_here\"}")
        return
    
    headers = {
        "Authorization": f"Bearer {fal_key}",
        "Content-Type": "application/json"
    }
    
    # Test with FLUX.1-schnell
    payload = {
        "model_name": "fast-sdxl",
        "prompt": "beautiful woman, high quality, detailed",
        "image_size": "square_hd",
        "num_inference_steps": 4,
        "guidance_scale": 2.0
    }
    
    try:
        print("🧪 Testing fal.ai generation...")
        response = requests.post(
            "https://fal.run/fal-ai/fast-sdxl",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation completed!")
            
            if 'images' in result and result['images']:
                print(f"🖼️  Image URL: {result['images'][0]['url']}")
                return True
            else:
                print(f"❌ No image in response")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_huggingface_api():
    """Test Hugging Face Inference API"""
    print(f"\n" + "=" * 60)
    print("Testing Hugging Face Inference API")
    print("=" * 60)
    
    api_keys = load_api_keys()
    hf_key = api_keys.get('huggingface-api')
    
    if not hf_key:
        print("❌ No Hugging Face API key found")
        print("💡 Add to api_keys.json: {\"huggingface-api\": \"your_key_here\"}")
        return
    
    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json"
    }
    
    # Test with Stable Diffusion XL
    payload = {
        "inputs": "beautiful woman, high quality, detailed",
        "parameters": {
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }
    
    try:
        print("🧪 Testing Stable Diffusion XL...")
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if response is image data
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                print(f"✅ Generation completed!")
                print(f"🖼️  Image size: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ Unexpected response type: {content_type}")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_api_costs():
    """Check current API costs and limits"""
    print(f"\n" + "=" * 60)
    print("API Cost Comparison")
    print("=" * 60)
    
    print("📊 Approximate Costs per 512x512 image:")
    print("   Replicate FLUX.1-schnell: ~$0.015")
    print("   fal.ai SDXL: ~$0.01")
    print("   Hugging Face SDXL: ~$0.01-0.03")
    print("   OpenAI DALL-E 3: $0.04")
    print("")
    print("💡 Recommendations:")
    print("   🥇 Best value: fal.ai (fast, affordable)")
    print("   🥈 Most models: Replicate (huge variety)")
    print("   🥉 Free tier: Hugging Face (30k requests/month)")

if __name__ == "__main__":
    print("🧪 Image Generation API Test Suite")
    print("=" * 60)
    
    # Check costs first
    check_api_costs()
    
    # Test each API
    results = {}
    
    results['replicate'] = test_replicate_api()
    results['fal'] = test_fal_api()
    results['huggingface'] = test_huggingface_api()
    
    print(f"\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for api, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"   {api.capitalize()}: {status}")
    
    print(f"\n💡 Next Steps:")
    working_apis = [api for api, success in results.items() if success]
    if working_apis:
        print(f"   🎯 Integrate these APIs first: {', '.join(working_apis)}")
    else:
        print(f"   🔑 Add API keys to test integration")
        print(f"   📝 Update api_keys.json with your API keys")
