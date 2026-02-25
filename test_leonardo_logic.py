import asyncio
import json
from modern_generators import ModernGeneratorManager

async def test_leonardo_payloads():
    manager = ModernGeneratorManager()
    
    # Mock API key to avoid initialization error
    manager.api_keys['leonardo-api'] = "test_key_1234567890"
    
    test_cases = [
        "phoenix-1-0",
        "phoenix-0-9",
        "universal",
        "gemini-image-2"
    ]
    
    print("Testing Leonardo.ai Payload Generation Logic:")
    print("-" * 50)
    
    for model_key in test_cases:
        print(f"\nModel: {model_key}")
        config = manager._leonardo_model_config(model_key)
        print(f"Config Name: {config['name']}")
        print(f"Config ID: {config['id']}")
        print(f"API Version: {config['api_version']}")
        
        prompt = "A tests image"
        if config['api_version'] == 'v2':
            payload = manager._build_leonardo_payload_v2(model_key, config, prompt)
            model_sent = payload.get("model")
        else:
            payload = manager._build_leonardo_payload_v1(model_key, config, prompt)
            model_sent = payload.get("modelId")
            
        print(f"Model ID sent in payload: {model_sent}")
        
        # Verify it's not the placeholder name unless it was the original key and not mapped
        if model_sent == model_key and model_key in ["phoenix-1-0", "phoenix-0-9", "universal"]:
            print(f"Verification FAILED: Placeholder name {model_sent} would be sent!")
        else:
            print("Verification PASSED: Valid ID mapping found.")

if __name__ == "__main__":
    asyncio.run(test_leonardo_payloads())
