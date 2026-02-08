"""
Check Replicate account status and requirements

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

def check_replicate_status():
    """Check Replicate account status and requirements"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        print("❌ No Replicate API key found")
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Replicate Account Status")
    print("=" * 50)
    
    # Check account info
    try:
        response = requests.get("https://api.replicate.com/v1/account", headers=headers, timeout=30)
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Account: {account.get('username', 'Unknown')}")
            
            # Check payment method
            has_payment = account.get('has_payment_method', False)
            print(f"💳 Payment Method: {'✅ Added' if has_payment else '❌ Not added'}")
            
            # Check plan
            plan = account.get('plan', 'Unknown')
            print(f"📋 Plan: {plan}")
            
            # Check usage
            usage = account.get('usage', {})
            if usage:
                print(f"📊 Usage:")
                print(f"   Predictions: {usage.get('predictions', 'Unknown')}")
                print(f"   Storage: {usage.get('storage', 'Unknown')}")
            
            return has_payment
        else:
            print(f"❌ Account check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_replicate_limits():
    """Check Replicate rate limits"""
    api_keys = load_api_keys()
    replicate_key = api_keys.get('replicate-api')
    
    if not replicate_key:
        return
    
    headers = {
        "Authorization": f"Token {replicate_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📊 Replicate Rate Limits")
    print("=" * 50)
    
    # Try a simple request to see rate limits
    try:
        payload = {
            "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            "input": {
                "prompt": "test",
                "width": 64,
                "height": 64,
                "num_outputs": 1,
                "num_inference_steps": 1
            }
        }
        
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 429:
            error = response.json()
            detail = error.get('detail', '')
            print(f"⏱️  Rate Limited: {detail}")
            
            # Extract rate limit info
            if 'per minute' in detail:
                print(f"📊 Limit: 6 requests per minute")
            if 'burst of' in detail:
                print(f"📊 Burst: 1 request")
            if 'retry after' in detail:
                print(f"⏰ Retry after: ~8 seconds")
        else:
            print(f"📊 Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def suggest_alternatives():
    """Suggest alternatives based on Replicate status"""
    print(f"\n💡 Recommendations")
    print("=" * 50)
    
    print("🔑 Replicate Requirements:")
    print("   1. Add payment method for full access")
    print("   2. Rate limits: 6 requests/minute without payment")
    print("   3. Some models require payment method")
    print("")
    print("🚀 Alternative APIs:")
    print("   1. fal.ai - Latest FLUX models, no payment required")
    print("   2. OpenAI DALL-E 3 - Best quality, pay-per-use")
    print("   3. Stability AI - Official SD models")
    print("")
    print("💰 Cost Comparison:")
    print("   Replicate: Free tier + pay-per-use (requires payment method)")
    print("   fal.ai: Pay-per-use (~$0.015-0.04/image)")
    print("   OpenAI: Pay-per-use ($0.04/image)")
    print("")
    print("🎯 Next Steps:")
    print("   1. Add payment method to Replicate account")
    print("   2. Or try fal.ai (no payment method required)")
    print("   3. Or test other APIs")

if __name__ == "__main__":
    has_payment = check_replicate_status()
    check_replicate_limits()
    suggest_alternatives()
    
    print(f"\n" + "=" * 50)
    if has_payment:
        print("✅ Replicate ready for full use")
    else:
        print("❌ Replicate requires payment method for full access")
        print("💡 Add payment method or try alternative APIs")
