"""
Check Hugging Face account permissions and suggest alternatives

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os

def load_api_keys():
    """Load API keys from file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def check_hf_permissions():
    """Check Hugging Face account permissions"""
    hf_token = load_api_keys().get('huggingface-api')
    
    if not hf_token:
        print("❌ No Hugging Face API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Checking Hugging Face Account")
    print("=" * 50)
    
    # Check user info
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=30)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User: {user_info.get('name', 'Unknown')}")
            print(f"📧 Email: {user_info.get('email', 'Unknown')}")
            print(f"👤 Username: {user_info.get('name', 'Unknown')}")
            print(f"🆓 Pro Account: {user_info.get('isPro', False)}")
            print(f"💎 Enterprise: {user_info.get('isEnterprise', False)}")
            
            # Check subscription
            if 'subscription' in user_info:
                sub = user_info['subscription']
                print(f"💳 Subscription: {sub.get('planName', 'Free')}")
                print(f"📊 Credits: {sub.get('credits', 'N/A')}")
            
            return user_info
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_inference_providers():
    """Check if user has access to Inference Providers"""
    hf_token = load_api_keys().get('huggingface-api')
    
    if not hf_token:
        return
    
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 Checking Inference Providers Access")
    print("=" * 50)
    
    # Test a simple request to check permissions
    try:
        response = requests.get(
            "https://router.huggingface.co/v1/models",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Inference Providers: Available")
            models = response.json()
            print(f"📊 Available models: {len(models)}")
            
            # Show some models
            if models and len(models) > 0:
                print(f"📋 Sample models:")
                for i, model in enumerate(models[:5]):
                    print(f"   {i+1}. {model.get('id', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Inference Providers: Not available")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking providers: {e}")
        return False

def suggest_alternatives():
    """Suggest alternatives based on account type"""
    print(f"\n💡 Recommendations")
    print("=" * 50)
    
    print("🔑 For Hugging Face Inference Providers:")
    print("   1. Upgrade to Pro account ($9/month)")
    print("   2. Get Enterprise account for unlimited access")
    print("   3. Use free tier with limited models")
    print("")
    print("🚀 Alternative APIs to Consider:")
    print("   1. Replicate - 1000+ models, $0.01-0.10/image")
    print("   2. fal.ai - Latest FLUX models, $0.015-0.04/image")
    print("   3. OpenAI DALL-E 3 - Best quality, $0.04/image")
    print("   4. Stability AI - Official SD models")
    print("")
    print("💰 Cost Comparison:")
    print("   Hugging Face Pro: $9/month + usage")
    print("   Replicate: Pay-per-use")
    print("   fal.ai: Pay-per-use")
    print("   OpenAI: Pay-per-use")

if __name__ == "__main__":
    print("🧪 Hugging Face Permissions Check")
    print("=" * 50)
    
    user_info = check_hf_permissions()
    has_providers = check_inference_providers()
    
    if user_info and not has_providers:
        print(f"\n❌ Your Hugging Face account lacks Inference Providers access")
        print(f"💡 This is common with free accounts")
        
        if not user_info.get('isPro', False):
            print(f"💳 Consider upgrading to Pro for Inference Providers")
    
    suggest_alternatives()
