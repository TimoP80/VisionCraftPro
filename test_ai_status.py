#!/usr/bin/env python3
"""
Test current AI enhancement status and fix issues
"""

import os
import sys
from pathlib import Path

def test_ai_status():
    print("🔍 Checking AI Enhancement Status")
    print("=" * 40)
    print()

    # Check environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    print("🔑 Environment Variables:")
    print(f"   GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print()

    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading .env file...")
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
                        print(f"   ✅ Loaded {key.strip()}")

            # Re-check after loading
            gemini_key = os.getenv("GEMINI_API_KEY")
            print(f"   🔄 GEMINI_API_KEY after loading: {'✅ Set' if gemini_key else '❌ Not set'}")

        except Exception as e:
            print(f"   ❌ Error loading .env: {e}")
    else:
        print("❌ .env file not found")
    print()

    # Check packages
    print("📦 Checking AI Packages:")
    packages_ok = True

    try:
        import google.generativeai
        print("   ✅ google-generativeai available")
    except ImportError:
        print("   ❌ google-generativeai not available")
        packages_ok = False

    try:
        import openai
        print("   ✅ openai available")
    except ImportError:
        print("   ❌ openai not available")

    try:
        import anthropic
        print("   ✅ anthropic available")
    except ImportError:
        print("   ❌ anthropic not available")

    print()

    # Test PromptEnhancer
    print("🤖 Testing PromptEnhancer:")
    try:
        from prompt_enhancer import PromptEnhancer

        enhancer = PromptEnhancer()
        print(f"   AI Available: {enhancer.ai_available}")
        print(f"   Gemini Key: {bool(enhancer.gemini_key)}")
        print(f"   OpenAI Key: {bool(enhancer.openai_key)}")
        print(f"   Anthropic Key: {bool(enhancer.anthropic_key)}")

        # Test synchronous enhancement
        print("   🔄 Testing template enhancement...")
        result = enhancer.enhance_prompt_sync("a beautiful woman", "photorealistic", "medium")

        print("   ✅ Template enhancement works")
        print(f"   📝 Prompt: {result.get('prompt', 'No prompt')[:80]}...")
        print(f"   🎯 AI Enhanced: {result.get('ai_enhanced', False)}")

        # Test async enhancement if packages are available
        if packages_ok and gemini_key:
            print("   🔄 Testing AI enhancement...")
            import asyncio

            async def test_ai():
                try:
                    result = await enhancer.enhance_prompt("a beautiful woman", "photorealistic", "medium")
                    print("   ✅ AI enhancement works")
                    print(f"   🤖 AI Enhanced: {result.get('ai_enhanced', False)}")
                    print(f"   📝 AI Prompt: {result.get('prompt', 'No prompt')[:80]}...")
                except Exception as e:
                    print(f"   ❌ AI enhancement failed: {e}")

            asyncio.run(test_ai())

    except Exception as e:
        print(f"   ❌ PromptEnhancer error: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Provide solutions
    print("🔧 Solutions:")
    if not gemini_key:
        print("1. ✅ Run: python configure_gemini_env.py")
        print("2. 🔄 Restart server: python app.py")

    if not packages_ok:
        print("1. 📦 Install packages:")
        print("   pip install google-generativeai openai anthropic")

    print("3. 🧪 Test enhancement in web interface")

if __name__ == "__main__":
    test_ai_status()
