#!/usr/bin/env python3
"""
Setup Leonardo.ai API key for VisionCraft Pro
"""

import os
import json
from modern_generators import ModernGeneratorManager

def setup_leonardo_key():
    print("🔑 Setting up Leonardo.ai API key...")
    print()
    
    # Get API key from user
    api_key = input("Enter your Leonardo.ai API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    print(f"✅ API key received: {api_key[:10]}...")
    
    # Initialize modern manager
    try:
        manager = ModernGeneratorManager()
        
        # Set the API key
        manager.set_api_key("leonardo-api", api_key)
        
        print("✅ API key saved to modern generator")
        
        # Test the API key
        print("🧪 Testing API key...")
        
        try:
            # Test platform endpoint
            import requests
            response = requests.get(
                "https://cloud.leonardo.ai/api/rest/v1/platform",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API key is valid!")
                
                # Show available models
                data = response.json()
                models = data.get("models", [])
                print(f"🎨 Available models: {len(models)}")
                
                # Show some popular models
                popular_models = [m for m in models if any(keyword in m.get("name", "").lower() for keyword in ["flux", "leonardo", "stable diffusion"])]
                if popular_models:
                    print("🔥 Popular models you can use:")
                    for model in popular_models[:5]:
                        model_id = model.get("id", "")
                        model_name = model.get("name", "Unknown")
                        print(f"   - {model_name} (ID: {model_id})")
                
                print()
                print("🚀 Leonardo.ai is now configured and ready to use!")
                print("📝 Try generating an image with a Leonardo.ai model")
                
                return True
            else:
                print(f"❌ API key validation failed: {response.status_code}")
                if response.status_code == 401:
                    print("   The API key appears to be invalid")
                elif response.status_code == 403:
                    print("   The API key may not have the right permissions")
                
        except Exception as e:
            print(f"❌ Error testing API key: {e}")
            
    except Exception as e:
        print(f"❌ Error setting up API key: {e}")
    
    return False

def show_current_status():
    """Show current Leonardo.ai configuration status"""
    try:
        manager = ModernGeneratorManager()
        
        # Load API keys
        manager.load_api_keys()
        
        api_keys = manager.api_keys
        leonardo_key = api_keys.get("leonardo-api")
        
        print("📊 Current Leonardo.ai Status:")
        print(f"   API Key Set: {'✅ Yes' if leonardo_key else '❌ No'}")
        
        if leonardo_key:
            print(f"   Key Length: {len(leonardo_key)} characters")
            print(f"   Key Preview: {leonardo_key[:8]}...{leonardo_key[-4:]}")
        
        # Test API connectivity
        if leonardo_key:
            print("🧪 Testing API connectivity...")
            try:
                import requests
                response = requests.get(
                    "https://cloud.leonardo.ai/api/rest/v1/platform",
                    headers={"Authorization": f"Bearer {leonardo_key}"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("✅ API connection successful")
                else:
                    print(f"❌ API connection failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ API test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    print("🎨 Leonardo.ai API Key Setup for VisionCraft Pro")
    print("=" * 50)
    print()
    
    # Show current status first
    show_current_status()
    print()
    
    # Setup new key
    if not setup_leonardo_key():
        print("\n💡 To get a Leonardo.ai API key:")
        print("1. Go to https://leonardo.ai/")
        print("2. Sign up or log in to your account")
        print("3. Go to API section and generate an API key")
        print("4. Copy the API key and run this script again")
        print()
        print("🔑 Once you have the key, run: python setup_leonardo_key.py")
    else:
        print("\n🎉 Setup complete! Restart the server and try generating images.")
