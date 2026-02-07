"""
Check Leonardo.ai API endpoints and find correct model IDs

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import requests
import json
import os
import time

def load_api_key():
    """Load Leonardo API key"""
    try:
        with open('api_keys.json', 'r') as f:
            keys = json.load(f)
            return keys.get('leonardo-api')
    except:
        return None

def test_api_endpoints():
    """Test different Leonardo.ai API endpoints"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print("=" * 60)
    print("Testing Leonardo.ai API Endpoints")
    print("=" * 60)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Test different endpoints
    endpoints = [
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/models", "Get Models"),
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/platform/models", "Get Platform Models"),
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/generations", "Get Generations"),
        ("POST", "https://cloud.leonardo.ai/api/rest/v1/generations", "Create Generation"),
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/init/image", "Init Image"),
        ("GET", "https://cloud.leonardo.ai/api/rest/v1/model", "Model Info"),
    ]
    
    for method, url, description in endpoints:
        print(f"\n🔍 Testing {description}: {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                # Test with minimal payload
                payload = {"prompt": "test"}
                response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'data' in data:
                            print(f"   ✅ Success - Found {len(data['data'])} items")
                            if data['data']:
                                print(f"   Sample: {data['data'][0]}")
                        else:
                            print(f"   ✅ Success - {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   ✅ Success - Found {len(data)} items")
                        if data:
                            print(f"   Sample: {data[0]}")
                except:
                    print(f"   ✅ Success - {response.text[:100]}...")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def get_user_info():
    """Get user information to understand API limits and available models"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🔍 Getting user information...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    try:
        response = requests.get("https://cloud.leonardo.ai/api/rest/v1/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User Info:")
            print(f"   User ID: {user_data.get('id', 'Unknown')}")
            print(f"   Username: {user_data.get('username', 'Unknown')}")
            print(f"   Plan: {user_data.get('plan', 'Unknown')}")
            print(f"   Credits: {user_data.get('credits', 'Unknown')}")
            
            # Check if there are any model restrictions
            if 'subscriptions' in user_data:
                print(f"   Subscriptions: {user_data['subscriptions']}")
                
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting user info: {e}")

def test_simple_generation():
    """Test generation with the most basic parameters"""
    api_key = load_api_key()
    if not api_key:
        print("❌ No Leonardo API key found")
        return
    
    print(f"\n🧪 Testing simple generation...")
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }
    
    # Try with no model ID (should use default)
    payload = {
        "prompt": "beautiful woman",
        "width": 512,
        "height": 512,
        "num_images": 1
    }
    
    try:
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generation_id = result.get('sdGenerationJob', {}).get('generationId')
            print(f"✅ Generation started: {generation_id}")
            
            # Try to get the generation details
            if generation_id:
                time.sleep(2)
                gen_response = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                )
                print(f"Generation status: {gen_response.status_code}")
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    print(f"Generation details: {gen_data}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    get_user_info()
    test_simple_generation()
