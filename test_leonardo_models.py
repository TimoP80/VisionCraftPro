"""
Test script to verify Leonardo Diffusion XL models are properly configured

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

from modern_generators import ModernGeneratorManager

def test_leonardo_models():
    """Test that Leonardo Diffusion XL models are available"""
    print("=" * 60)
    print("Testing Leonardo Diffusion XL Models")
    print("=" * 60)
    
    # Initialize modern generator manager
    manager = ModernGeneratorManager()
    
    # Get available generators
    generators = manager.get_available_generators()
    
    print(f"\n📋 Available Generators: {len(generators)}")
    
    # Check if Leonardo.ai is available
    if "leonardo-api" in generators:
        leonardo = generators["leonardo-api"]
        print(f"\n✅ Leonardo.ai API found!")
        print(f"   Name: {leonardo['name']}")
        print(f"   Type: {leonardo['type']}")
        print(f"   Description: {leonardo['description']}")
        
        # Check models
        models = leonardo.get("models", {})
        print(f"\n🎨 Available Models: {len(models)}")
        
        expected_models = [
            "phoenix-1-0",
            "phoenix-0-9", 
            "diffusion-xl",
            "diffusion-xl-lightning",
            "universal"
        ]
        
        for model_key in expected_models:
            if model_key in models:
                model = models[model_key]
                print(f"   ✅ {model_key}: {model['name']}")
                print(f"      Description: {model['description']}")
                print(f"      Max Resolution: {model['max_resolution']}")
                if 'features' in model:
                    print(f"      Features: {', '.join(model['features'])}")
                print()
            else:
                print(f"   ❌ {model_key}: NOT FOUND")
        
        # Check preset styles
        styles = leonardo.get("preset_styles", [])
        print(f"🎭 Preset Styles: {len(styles)}")
        for style in styles[:5]:  # Show first 5
            print(f"   - {style['name']}: {style['description']}")
        
        # Check quality levels
        quality_levels = leonardo.get("quality_levels", [])
        print(f"\n⭐ Quality Levels: {len(quality_levels)}")
        for level in quality_levels:
            print(f"   - {level['name']}: {level['description']}")
        
        # Check aspect ratios
        aspect_ratios = leonardo.get("aspect_ratios", [])
        print(f"\n📐 Aspect Ratios: {len(aspect_ratios)}")
        for ratio in aspect_ratios:
            print(f"   - {ratio['name']}: {ratio['resolution']}")
        
        # Check API keys
        api_keys = manager.api_keys
        print(f"\n🔑 API Keys Status:")
        if "leonardo-api" in api_keys:
            key = api_keys["leonardo-api"]
            print(f"   ✅ Leonardo API key configured: {'*' * 10}{key[-4:] if len(key) > 4 else '****'}")
        else:
            print(f"   ❌ Leonardo API key not configured")
        
        print(f"\n🎯 Leonardo Diffusion XL Status: {'✅ AVAILABLE' if 'diffusion-xl' in models else '❌ NOT FOUND'}")
        
    else:
        print(f"\n❌ Leonardo.ai API not found in available generators")
        print(f"   Available generators: {list(generators.keys())}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_leonardo_models()
