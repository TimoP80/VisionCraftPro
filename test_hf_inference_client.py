"""
Test Hugging Face InferenceClient for image generation

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import json
import os

def test_hf_inference_client():
    """Test Hugging Face InferenceClient"""
    try:
        from huggingface_hub import InferenceClient
        print("✅ huggingface_hub library is available")
    except ImportError:
        print("❌ huggingface_hub library not installed")
        print("💡 Install with: pip install huggingface_hub")
        return False
    
    # Load API key
    try:
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)
            hf_token = api_keys.get('huggingface-api')
    except:
        hf_token = os.environ.get('HF_TOKEN')
    
    if not hf_token:
        print("❌ No Hugging Face API key found")
        print("💡 Add to api_keys.json or set HF_TOKEN environment variable")
        return False
    
    print(f"🔑 API key found: {'*' * 10}{hf_token[-4:]}")
    
    # Create client
    try:
        client = InferenceClient(api_key=hf_token)
        print("✅ InferenceClient created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # Test image generation
    print("\n🧪 Testing image generation...")
    
    # Test with FLUX.1-dev (latest model)
    try:
        print("📸 Generating with FLUX.1-dev...")
        image = client.text_to_image(
            prompt="beautiful woman, high quality, detailed, photorealistic",
            model="black-forest-labs/FLUX.1-dev"
        )
        
        # Save the image
        image.save("hf_test_image.png")
        print("✅ Image generated successfully!")
        print(f"🖼️  Saved as: hf_test_image.png")
        print(f"📏 Image size: {image.size}")
        return True
        
    except Exception as e:
        print(f"❌ FLUX.1-dev failed: {e}")
        
        # Try with Stable Diffusion XL as fallback
        try:
            print("\n📸 Trying Stable Diffusion XL...")
            image = client.text_to_image(
                prompt="beautiful woman, high quality, detailed, photorealistic",
                model="stabilityai/stable-diffusion-xl-base-1.0"
            )
            
            image.save("hf_test_image_sdxl.png")
            print("✅ SDXL image generated successfully!")
            print(f"🖼️  Saved as: hf_test_image_sdxl.png")
            print(f"📏 Image size: {image.size}")
            return True
            
        except Exception as e2:
            print(f"❌ SDXL also failed: {e2}")
            return False

def test_available_models():
    """Test what models are available"""
    try:
        from huggingface_hub import InferenceClient
        import json
        
        # Load API key
        try:
            with open('api_keys.json', 'r') as f:
                api_keys = json.load(f)
                hf_token = api_keys.get('huggingface-api')
        except:
            hf_token = os.environ.get('HF_TOKEN')
        
        if not hf_token:
            return
        
        client = InferenceClient(api_key=hf_token)
        
        # Test some popular models
        test_models = [
            "black-forest-labs/FLUX.1-dev",
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-2-1"
        ]
        
        print("\n🔍 Testing model availability:")
        
        for model in test_models:
            try:
                # Try a minimal generation to test availability
                image = client.text_to_image(
                    prompt="test",
                    model=model,
                    num_inference_steps=1,  # Fast test
                    width=64,
                    height=64
                )
                print(f"   ✅ {model}: Available")
                image.close()  # Don't save test images
            except Exception as e:
                print(f"   ❌ {model}: {str(e)[:50]}...")
                
    except Exception as e:
        print(f"❌ Error testing models: {e}")

if __name__ == "__main__":
    print("🧪 Hugging Face InferenceClient Test")
    print("=" * 50)
    
    # Test basic functionality
    success = test_hf_inference_client()
    
    # Test model availability
    test_available_models()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Hugging Face InferenceClient is working!")
        print("💡 Ready for integration into VisionCraft Pro")
    else:
        print("❌ Hugging Face InferenceClient failed")
        print("💡 Check API key and library installation")
