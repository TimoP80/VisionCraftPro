#!/usr/bin/env python3

import asyncio
import json
import requests

async def test_endpoint():
    try:
        # Test the enhance-prompt endpoint
        url = "http://127.0.0.1:8000/enhance-prompt"
        
        payload = {
            "prompt": "a beautiful sunset over mountains",
            "style": "cinematic",
            "detail_level": "medium"
        }
        
        print(f"Testing endpoint: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Enhanced prompt: {data.get('prompt', 'No prompt')}")
            print(f"AI enhanced: {data.get('ai_enhanced', False)}")
            print(f"AI available: {data.get('ai_available', False)}")
        else:
            print("❌ Failed")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
