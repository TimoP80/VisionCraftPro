#!/usr/bin/env python3
"""
Check if AI packages are available for prompt enhancement
"""

def check_packages():
    print("🔍 Checking AI packages for prompt enhancement...")
    print()
    
    # Check OpenAI
    try:
        import openai
        print("✅ OpenAI package available")
    except ImportError:
        print("❌ OpenAI package not available")
    
    # Check Anthropic
    try:
        import anthropic
        print("✅ Anthropic package available")
    except ImportError:
        print("❌ Anthropic package not available")
    
    # Check Google Generative AI
    try:
        import google.generativeai
        print("✅ Google Generative AI package available")
    except ImportError:
        print("❌ Google Generative AI package not available")
    
    print()
    
    # Check environment variables
    import os
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("🔑 Checking API keys...")
    print(f"GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    
    print()
    
    if gemini_key and not any(pkg in globals() for pkg in ['google', 'google.generativeai']):
        print("⚠️  Gemini API key is set but google-generativeai package is missing!")
        print("   Install with: pip install google-generativeai")
        print("   Or activate your virtual environment and run: pip install -r requirements.txt")
    
    # Test PromptEnhancer
    try:
        from prompt_enhancer import PromptEnhancer
        enhancer = PromptEnhancer()
        print(f"🤖 AI Enhancement Available: {enhancer.ai_available}")
    except Exception as e:
        print(f"❌ Error with PromptEnhancer: {e}")

if __name__ == "__main__":
    check_packages()
