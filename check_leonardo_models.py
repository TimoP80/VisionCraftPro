"""
Check Leonardo.ai API for available models and their correct IDs

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os

def load_api_key():
    """Load Leonardo API key"""
    try:
        with open('api_keys.json', 'r') as f:
            keys = json.load(f)
            return keys.get('leonardo-api')
    except:
        return None

def get_available_models():
    """Get available models from Leonardo.ai API"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 60)
    print("Leonardo.ai Available Models Check")
    print("=" * 60)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try to get platform models
    try:
        print("\n🔍 Getting platform models...")
        response = requests.get("https://cloud.leonardo.ai/api/rest/v1/platform/models", headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Successfully retrieved {len(models.get('data', []))} models")
            
            print(f"\n📋 Available Models:")
            for model in models.get('data', []):
                model_id = model.get('id', 'Unknown')
                model_name = model.get('name', 'Unknown')
                model_type = model.get('type', 'Unknown')
                description = model.get('description', 'No description')
                
                print(f"\n🎨 {model_name}")
                print(f"   ID: {model_id}")
                print(f"   Type: {model_type}")
                print(f"   Description: {description}")
                
                # Check if this is an SDXL model
                if 'xl' in model_name.lower() or 'sdxl' in model_name.lower():
                    print(f"   ⭐ SDXL Model!")
                
                # Check if this is a lightning model
                if 'lightning' in model_name.lower():
                    print(f"   ⚡ Lightning Model!")
                    
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting models: {e}")
    
    # Try to get user models
    try:
        print(f"\n🔍 Getting user models...")
        response = requests.get("https://cloud.leonardo.ai/api/rest/v1/models", headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            user_models = models.get('data', [])
            print(f"✅ Successfully retrieved {len(user_models)} user models")
            
            if user_models:
                print(f"\n👤 User Models:")
                for model in user_models:
                    model_id = model.get('id', 'Unknown')
                    model_name = model.get('name', 'Unknown')
                    print(f"\n🎨 {model_name}")
                    print(f"   ID: {model_id}")
            else:
                print(f"ℹ️ No user models found")
                
        else:
            print(f"❌ Failed to get user models: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting user models: {e}")
    
    # Test current model IDs
    print(f"\n🧪 Testing Current Model IDs...")
    current_ids = {
        "diffusion-xl": "b24e16ff-06e3-450b-92b8-8e8901d3dab8",
        "diffusion-xl-lightning": "448df82c-8872-4e4f-9d5a-351c8cf09548",
        "phoenix-1-0": "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8",
        "phoenix-0-9": "c821f938-3de7-4c32-9b2a-5f8961b5c8e5",
        "universal": "6bef9f4b-29cb-40c7-bdf-32b51c1f80d8"
    }
    
    for model_name, model_id in current_ids.items():
        try:
            # Try to get model info
            response = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/models/{model_id}", headers=headers)
            
            if response.status_code == 200:
                model_info = response.json()
                print(f"✅ {model_name}: {model_info.get('name', 'Unknown')} (Valid)")
            else:
                print(f"❌ {model_name}: {model_id} (Invalid - {response.status_code})")
                
        except Exception as e:
            print(f"❌ {model_name}: {model_id} (Error - {e})")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    get_available_models()
