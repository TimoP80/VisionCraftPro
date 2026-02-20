import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

endpoint = "https://azure-2026.openai.azure.com"
api_version = "2024-02-15-preview"

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
access_token = token_provider()
headers = {"Authorization": f"Bearer {access_token}"}

url = f"{endpoint}/openai/deployments?api-version={api_version}"
resp = requests.get(url, headers=headers, timeout=30)
print("Status:", resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)
