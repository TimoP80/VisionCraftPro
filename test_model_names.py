import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

endpoint = "https://timbor-azure-resource.openai.azure.com/openai/v1/images/generations"
model_candidates = [
    "flux.2-pro",
    "FLUX.2-pro",
    "flux-2-pro",
    "FLUX-2-pro",
    "flux-2-pro",
    "flux.2-Pro",
    "FLUX.2-Pro",
]

try:
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    token = token_provider()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print(f"Token prefix: {token[:20]}...")

    for name in model_candidates:
        print(f"\nTesting model: {name}")
        resp = requests.post(endpoint, headers=headers, json={
            "model": name,
            "prompt": "test image",
            "n": 1,
            "size": "1024x1024"
        })
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS! Model works")
            break
        elif resp.status_code == 429:
            print("Rate limited - but model works")
            break
        else:
            print(f"Error: {resp.text}")
except Exception as e:
    print(f"Error during testing: {e}")
