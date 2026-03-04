#!/usr/bin/env python3
"""
Test the todos endpoint to debug the frontend error
"""

import asyncio
import requests
import json

def test_todos_endpoint():
    """Test the /todos endpoint to see what it returns"""
    print("🔍 Testing /todos endpoint...")
    print()

    try:
        response = requests.get("http://127.0.0.1:8000/todos", timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Response is valid JSON")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

                if isinstance(data, dict):
                    if 'todos' in data:
                        todos = data.get('todos')
                        print(f"✅ 'todos' key found: {type(todos)}")
                        if todos is not None:
                            print(f"   Length: {len(todos) if hasattr(todos, '__len__') else 'No length'}")
                        else:
                            print("   ❌ todos is None")
                    else:
                        print("❌ 'todos' key not found in response")

                    if 'count' in data:
                        print(f"✅ 'count' key found: {data.get('count')}")
                    else:
                        print("❌ 'count' key not found in response")

                print(f"Full response: {json.dumps(data, indent=2)[:500]}...")

            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text[:500]}...")

        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running?")
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_todos_endpoint()
