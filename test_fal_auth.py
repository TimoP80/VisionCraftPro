"""
Test fal.ai authentication and API key format

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json

def load_api_keys():
    """Load API keys from file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def test_fal_auth():
    """Test fal.ai authentication"""
    api_keys = load_api_keys()
    fal_key = api_keys.get('fal-api')
    
    if not fal_key:
        print("❌ No fal.ai API key found")
        return False
    
    print("🔍 fal.ai Authentication Test")
    print("=" * 40)
    print(f"🔑 API Key: {'*' * 10}{fal_key[-4:] if len(fal_key) > 4 else 'Too short'}")
    print(f"📏 Length: {len(fal_key)} characters")
    print(f"🔤 Format: {fal_key[:10]}...")
    
    # Check key format
    if not fal_key.startswith('fal-'):
        print("❌ API key should start with 'fal-'")
        print("💡 fal.ai keys format: fal-xxxxxxxxxxxxxxxx")
        return False
    
    if len(fal_key) < 20:
        print("❌ API key seems too short")
        print("💡 fal.ai keys are usually 30+ characters")
        return False
    
    # Test different authentication methods
    auth_methods = [
        {"Authorization": f"Bearer {fal_key}"},
        {"Authorization": f"Token {fal_key}"},
        {"X-API-Key": fal_key},
        {"fal-api-key": fal_key}
    ]
    
    print(f"\n🧪 Testing Authentication Methods")
    print("=" * 40)
    
    for i, headers in enumerate(auth_methods):
        print(f"\n📡 Method {i+1}: {list(headers.keys())[0]}")
        
        try:
            # Test with a simple endpoint
            response = requests.get(
                "https://fal.run/fal-ai/flux.1-schnell/status",
                headers=headers,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Authentication successful!")
                return True
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed")
            elif response.status_code == 404:
                print(f"   ⚠️  Endpoint not found (but auth might work)")
            else:
                print(f"   📋 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Try a simple generation test
    print(f"\n🧪 Testing Simple Generation")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {fal_key}"}
    
    payload = {
        "prompt": "test image",
        "image_size": "square_hd",
        "num_inference_steps": 1,
        "guidance_scale": 1.0,
        "num_images": 1
    }
    
    try:
        response = requests.post(
            "https://fal.run/fal-ai/fast-sdxl",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📡 Generation Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Generation successful!")
            return True
        else:
            print(f"❌ Generation failed: {response.text}")
            
            if "Invalid token" in response.text:
                print(f"💡 API key is invalid or expired")
            elif "insufficient credit" in response.text:
                print(f"💡 Insufficient credits")
            elif "rate limit" in response.text.lower():
                print(f"💡 Rate limited")
            
            return False
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

def show_fal_key_help():
    """Show help for getting fal.ai API key"""
    print(f"\n💡 fal.ai API Key Help")
    print("=" * 40)
    print("1. Go to: https://fal.ai/dashboard")
    print("2. Sign up or log in")
    print("3. Click on 'API Keys' in the sidebar")
    print("4. Click 'Create New Key'")
    print("5. Give it a name (e.g., 'VisionCraft Pro')")
    print("6. Copy the key (it should start with 'fal-')")
    print("7. Add it to api_keys.json")
    print("")
    print("📝 Correct format:")
    print('{"fal-api": "fal-xxxxxxxxxxxxxxxxxxxxxxxx"}')
    print("")
    print("⚠️  Common issues:")
    print("- Key doesn't start with 'fal-'")
    print("- Key is expired or revoked")
    print("- Key has insufficient permissions")
    print("- Account needs to be verified")

if __name__ == "__main__":
    success = test_fal_auth()
    
    if not success:
        show_fal_key_help()
    else:
        print(f"\n✅ fal.ai authentication working!")
