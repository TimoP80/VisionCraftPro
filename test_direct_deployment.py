import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Test direct deployment access
endpoint = "https://timbor-instance.openai.azure.com"

try:
    # Get token
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    access_token = token_provider()
    auth_header = f"Bearer {access_token}"
    print(f"Got access token: {access_token[:20]}...")
    
    # Try different deployment access methods
    print("\nTesting direct deployment access...")
    
    # Method 1: Try direct deployment endpoint
    deployment_url = f"{endpoint}/openai/deployments/FLUX.2-pro"
    print(f"\nTrying direct deployment URL: {deployment_url}")
    try:
        response = requests.get(deployment_url, headers={'Authorization': auth_header})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            deployment_info = response.json()
            print(f"SUCCESS! Deployment info: {deployment_info}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Method 2: Try with API version
    deployment_url_with_version = f"{endpoint}/openai/deployments/FLUX.2-pro?api-version=2024-02-15-preview"
    print(f"\nTrying with API version: {deployment_url_with_version}")
    try:
        response = requests.get(deployment_url_with_version, headers={'Authorization': auth_header})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            deployment_info = response.json()
            print(f"SUCCESS! Deployment info: {deployment_info}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Method 3: Try different API versions for deployment access
    api_versions = ["2023-12-01-preview", "2024-03-01-preview", "2024-06-01-preview"]
    for api_version in api_versions:
        deployment_url = f"{endpoint}/openai/deployments/FLUX.2-pro?api-version={api_version}"
        print(f"\nTrying API version {api_version}: {deployment_url}")
        try:
            response = requests.get(deployment_url, headers={'Authorization': auth_header})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                deployment_info = response.json()
                print(f"SUCCESS! Deployment info with {api_version}: {deployment_info}")
                break
            else:
                print(f"Error with {api_version}: {response.text}")
        except Exception as e:
            print(f"Exception with {api_version}: {e}")
    
    # Method 4: Try to use the model directly (some Azure AI resources allow this)
    print(f"\nTrying to use model directly...")
    model_url = f"{endpoint}/openai/v1/chat/completions"
    try:
        response = requests.post(model_url, headers={'Authorization': auth_header, 'Content-Type': 'application/json'}, 
                               json={"model": "FLUX.2-pro", "messages": [{"role": "user", "content": "test"}]})
        print(f"Chat completions status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS! Model is accessible via chat completions")
        else:
            print(f"Chat completions error: {response.text}")
    except Exception as e:
        print(f"Chat completions exception: {e}")
    
    # Method 5: Try images generation with model name (not deployment name)
    print(f"\nTrying images generation with model name...")
    images_url = f"{endpoint}/openai/v1/images/generations"
    try:
        response = requests.post(images_url, headers={'Authorization': auth_header, 'Content-Type': 'application/json'}, 
                               json={"model": "FLUX.2-pro", "prompt": "test", "n": 1, "size": "1024x1024"})
        print(f"Images generation status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS! Images generation works with model name")
        else:
            print(f"Images generation error: {response.text}")
    except Exception as e:
        print(f"Images generation exception: {e}")

except Exception as e:
    print(f"Failed to get token or test deployment: {e}")
