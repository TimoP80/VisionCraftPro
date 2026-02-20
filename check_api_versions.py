import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

endpoint = "https://azure-2026.openai.azure.com/openai/v1/images/generations"
versions = [
    None,  # try without api-version
    "2024-08-01-preview",
    "2024-07-01-preview",
    "2024-05-15-preview",
    "2024-02-15-preview",
    "2023-12-01-preview",
]
payload = {"model": "FLUX.2-pro", "prompt": "test image", "n": 1, "size": "1024x1024"}

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
access_token = token_provider()
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

for v in versions:
    url = f"{endpoint}?api-version={v}" if v else endpoint
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"{v}: {resp.status_code}")
        if resp.status_code != 200:
            print(resp.text[:400])
        else:
            print("SUCCESS")
            break
    except Exception as e:
        print(f"{v}: error {e}")
