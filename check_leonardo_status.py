#!/usr/bin/env python3
"""
Check Leonardo.ai API status and provide troubleshooting info
"""

import requests
import json
import time

def check_leonardo_status():
    print("🔍 Checking Leonardo.ai API status...")
    print()
    
    # Test basic API connectivity
    try:
        response = requests.get("https://cloud.leonardo.ai/api/rest/v1/platform", timeout=10)
        
        if response.status_code == 200:
            print("✅ Leonardo.ai API is reachable")
            data = response.json()
            
            # Check platform status
            if "status" in data:
                print(f"📊 Platform Status: {data.get('status', 'Unknown')}")
            
            # Check available models
            if "models" in data:
                models = data.get("models", [])
                print(f"🎨 Available Models: {len(models)}")
                
                # Show some popular models
                popular_models = [m for m in models if m.get("name", "").lower() in ["flux", "leonardo", "stable diffusion", "dall-e"]]
                if popular_models:
                    print("🔥 Popular Models:")
                    for model in popular_models[:5]:
                        print(f"   - {model.get('name', 'Unknown')}")
            
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰️ Request timed out - Leonardo.ai may be slow")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection failed - Check your internet connection")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    print()
    print("📋 Troubleshooting Tips:")
    print("1. If Leonardo.ai shows server issues, try again in a few minutes")
    print("2. Switch to a different model (Modal, local models, etc.)")
    print("3. Check your API key configuration")
    print("4. Monitor Leonardo.ai status at: https://status.leonardo.ai/")
    print()
    
    # Test generation endpoint (this might fail with 500)
    print("🧪 Testing generation endpoint...")
    try:
        test_payload = {
            "prompt": "test image",
            "modelId": "6bef79f1-4c30-4f2d-b29f-4f5a8b5ec48f",  # Leonardo Diffusion
            "width": 512,
            "height": 512,
            "num_images": 1
        }
        
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Generation endpoint working")
        elif response.status_code == 500:
            print("⚠️  Generation endpoint returning 500 (server issues)")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   Response: {response.text}")
        else:
            print(f"❌ Generation endpoint returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")

if __name__ == "__main__":
    check_leonardo_status()
