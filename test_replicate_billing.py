"""
Test Replicate billing status and find working models

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

def test_replicate_billing():
    """Test Replicate billing and credits"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        print("❌ No Replicate API key found")
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Checking Replicate Billing Status")
    print("=" * 50)
    
    try:
        response = requests.get("https://api.replicate.com/v1/account", headers=headers, timeout=30)
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Account: {account.get('username', 'Unknown')}")
            print(f"💳 Payment Method: {'✅ Added' if account.get('has_payment_method', False) else '❌ Not added'}")
            
            # Check billing info
            billing = account.get('billing', {})
            if billing:
                print(f"💰 Billing:")
                print(f"   Status: {billing.get('status', 'Unknown')}")
                print(f"   Credits: {billing.get('credits', 'Unknown')}")
                
                # Check if we have enough credits
                credits = billing.get('credits', 0)
                if credits > 0:
                    print(f"✅ You have {credits} credits available")
                    return True
                else:
                    print(f"❌ No credits available")
                    return False
            else:
                print(f"❌ No billing info available")
                return False
        else:
            print(f"❌ Account check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cheap_model():
    """Test with a cheaper model"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        return False
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🧪 Testing Cheaper Model")
    print("=" * 50)
    
    # Try with a smaller, cheaper model
    payload = {
        "version": "be04601849d834e5e6d8e2b0e3e0b6e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e",
        "input": {
            "prompt": "beautiful woman, high quality, detailed",
            "width": 256,  # Smaller size
            "height": 256,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 10  # Fewer steps
        }
    }
    
    try:
        print("📸 Starting cheap generation...")
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
            
            # Poll for completion
            get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
            
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
                        error = result_data.get('error', 'Unknown error')
                        print(f"❌ Generation failed: {error}")
                        return False
                    else:
                        if i % 5 == 0:
                            print(f"⏳ Status: {status} ({i+1}s)")
                else:
                    print(f"❌ Polling failed: {get_response.status_code}")
                    return False
            else:
                print(f"⏰ Timeout after 30 seconds")
                return False
        else:
            error_text = response.text
            print(f"❌ Failed: {error_text}")
            
            if "insufficient credit" in error_text.lower():
                print(f"💡 Need to purchase credits at: https://replicate.com/account/billing")
            elif "payment method" in error_text.lower():
                print(f"💡 Need to add payment method at: https://replicate.com/account/billing")
            
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_replicate_collections():
    """Get available model collections"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📋 Getting Model Collections")
    print("=" * 50)
    
    try:
        response = requests.get("https://api.replicate.com/v1/collections", headers=headers, timeout=30)
        
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections.get('results', []))} collections")
            
            # Look for text-to-image collections
            for collection in collections.get('results', []):
                if 'text-to-image' in collection.get('slug', '').lower():
                    print(f"\n📁 Collection: {collection.get('name', 'Unknown')}")
                    models = collection.get('models', [])
                    print(f"   🎨 Models: {len(models)}")
                    
                    # Show first few models
                    for model in models[:3]:
                        print(f"   📝 {model.get('name', 'Unknown')}")
                        print(f"      💰 Cost: {model.get('cost', 'Unknown')}")
        else:
            print(f"❌ Failed to get collections: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Replicate Billing and Credits Test")
    print("=" * 50)
    
    has_credits = test_replicate_billing()
    
    if not has_credits:
        print(f"\n💡 Next Steps:")
        print(f"   1. Purchase credits at: https://replicate.com/account/billing")
        print(f"   2. Wait a few minutes for credits to be processed")
        print(f"   3. Try testing again")
        print(f"   4. Or try fal.ai (no upfront credits required)")
    else:
        # Try a cheap test
        test_cheap_model()
    
    get_replicate_collections()
