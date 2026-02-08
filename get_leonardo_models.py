"""
Get Leonardo models using the correct API endpoint parameters

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

def get_leonardo_models():
    """Get Leonardo models using the correct API endpoint"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 70)
    print("Getting Leonardo Models from API")
    print("=" * 70)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try different approaches to get models
    approaches = [
        {
            "name": "POST /models with empty body",
            "method": "POST",
            "url": "https://cloud.leonardo.ai/api/rest/v1/models",
            "payload": {}
        },
        {
            "name": "POST /models with name parameter",
            "method": "POST", 
            "url": "https://cloud.leonardo.ai/api/rest/v1/models",
            "payload": {"name": "get"}
        },
        {
            "name": "POST /models with instance_prompt",
            "method": "POST",
            "url": "https://cloud.leonardo.ai/api/rest/v1/models", 
            "payload": {"instance_prompt": "test"}
        },
        {
            "name": "GET /platform/models",
            "method": "GET",
            "url": "https://cloud.leonardo.ai/api/rest/v1/platform/models",
            "payload": None
        },
        {
            "name": "POST /platform/models",
            "method": "POST",
            "url": "https://cloud.leonardo.ai/api/rest/v1/platform/models",
            "payload": {}
        }
    ]
    
    for approach in approaches:
        print(f"\n🔍 Trying: {approach['name']}")
        
        try:
            if approach['method'] == "GET":
                response = requests.get(approach['url'], headers=headers, timeout=30)
            else:
                response = requests.post(approach['url'], headers=headers, json=approach['payload'], timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success!")
                    
                    # Parse the response
                    if isinstance(data, dict):
                        if 'data' in data:
                            models = data['data']
                        else:
                            models = data
                    elif isinstance(data, list):
                        models = data
                    else:
                        models = [data]
                    
                    print(f"   Found {len(models)} model(s)")
                    
                    # Look for Phoenix models
                    phoenix_models = []
                    for model in models:
                        if isinstance(model, dict):
                            name = model.get('name', '').lower()
                            if 'phoenix' in name:
                                phoenix_models.append(model)
                    
                    if phoenix_models:
                        print(f"\n🌟 Found {len(phoenix_models)} Phoenix models:")
                        for model in phoenix_models:
                            model_id = model.get('id', 'Unknown')
                            model_name = model.get('name', 'Unknown')
                            print(f"   {model_name}: {model_id}")
                    else:
                        print(f"   No Phoenix models found")
                        print(f"   Available models:")
                        for model in models[:5]:  # Show first 5
                            if isinstance(model, dict):
                                name = model.get('name', 'Unknown')
                                model_id = model.get('id', 'Unknown')
                                print(f"   {name}: {model_id}")
                    
                    return models
                    
                except Exception as e:
                    print(f"   Error parsing response: {e}")
                    print(f"   Raw response: {response.text[:200]}...")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def check_user_subscription():
    """Check user subscription details to understand model access"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Checking user subscription...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    try:
        response = requests.get("https://cloud.leonardo.ai/api/rest/v1/me", headers=headers, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info retrieved:")
            
            if 'user_details' in user_data and user_data['user_details']:
                user = user_data['user_details'][0]['user']
                print(f"   User ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
                
            # Check subscription tokens
            if 'user_details' in user_data and user_data['user_details']:
                details = user_data['user_details'][0]
                print(f"   Subscription Tokens: {details.get('subscriptionTokens', 0)}")
                print(f"   Subscription Model Tokens: {details.get('subscriptionModelTokens', 0)}")
                print(f"   API Subscription Tokens: {details.get('apiSubscriptionTokens', 'None')}")
                print(f"   API Paid Tokens: {details.get('apiPaidTokens', 0)}")
                
                # Check if they have model tokens
                model_tokens = details.get('subscriptionModelTokens', 0)
                if model_tokens > 0:
                    print(f"   🌟 HAS MODEL TOKENS: {model_tokens}")
                else:
                    print(f"   ❌ NO MODEL TOKENS - This explains why Phoenix models don't work")
        else:
            print(f"❌ Failed to get user info: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check user subscription first
    check_user_subscription()
    
    # Try to get models
    models = get_leonardo_models()
    
    print(f"\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    
    if models:
        print(f"✅ Successfully retrieved Leonardo models")
    else:
        print(f"❌ Could not retrieve Leonardo models")
        print(f"💡 This suggests the user has a basic plan without model access")
        print(f"💡 The 'Leonardo Phoenix' mentioned in docs may require a higher tier plan")
