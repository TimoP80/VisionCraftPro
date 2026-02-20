import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Check what resource we're actually accessing
try:
    # Get token
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    access_token = token_provider()
    auth_header = f"Bearer {access_token}"
    print(f"Got access token: {access_token[:20]}...")
    
    # Decode the token to see what resource it's for
    import base64
    import json
    
    # JWT tokens have 3 parts: header.payload.signature
    token_parts = access_token.split('.')
    if len(token_parts) >= 2:
        try:
            # Decode the payload (middle part)
            payload = base64.b64decode(token_parts[1] + '==')
            payload_data = json.loads(payload)
            print(f"Token payload:")
            print(f"  Issuer: {payload_data.get('iss', 'Unknown')}")
            print(f"  Audience: {payload_data.get('aud', 'Unknown')}")
            print(f"  Resource: {payload_data.get('resource', 'Unknown')}")
            print(f"  Scope: {payload_data.get('scp', 'Unknown')}")
            print(f"  Expires: {payload_data.get('exp', 'Unknown')}")
        except Exception as e:
            print(f"Failed to decode token: {e}")
    else:
        print("Token format is not as expected")
    
    # Try to access the base resource
    base_url = "https://timbor-instance.openai.azure.com"
    print(f"\nTesting base resource access: {base_url}")
    
    try:
        response = requests.get(base_url, headers={'Authorization': auth_header})
        print(f"Base resource status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS! Can access base resource")
        else:
            print(f"Base resource error: {response.text}")
    except Exception as e:
        print(f"Base resource exception: {e}")
    
    # Try to get account info
    print(f"\nTrying to get account info...")
    try:
        response = requests.get(f"{base_url}/openai/account", headers={'Authorization': auth_header})
        print(f"Account info status: {response.status_code}")
        if response.status_code == 200:
            account_info = response.json()
            print(f"Account info: {account_info}")
        else:
            print(f"Account info error: {response.text}")
    except Exception as e:
        print(f"Account info exception: {e}")

except Exception as e:
    print(f"Failed to get token or check resource: {e}")
