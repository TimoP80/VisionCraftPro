#!/usr/bin/env python3

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_enhancer():
    try:
        print("Testing PromptEnhancer import...")
        from prompt_enhancer import PromptEnhancer
        
        print("Creating enhancer instance...")
        enhancer = PromptEnhancer()
        
        print(f"AI Available: {enhancer.ai_available}")
        print(f"OpenAI Key: {bool(enhancer.openai_key)}")
        print(f"Anthropic Key: {bool(enhancer.anthropic_key)}")
        print(f"Gemini Key: {bool(enhancer.gemini_key)}")
        
        print("Testing enhancement...")
        result = await enhancer.enhance_prompt("a beautiful sunset", "cinematic", "medium")
        
        print("Success! Result keys:", list(result.keys()))
        print("Enhanced prompt:", result.get('prompt', 'No prompt'))
        print("AI enhanced:", result.get('ai_enhanced', False))
        print("AI available:", result.get('ai_available', False))
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhancer())
    if success:
        print("✅ PromptEnhancer test passed")
    else:
        print("❌ PromptEnhancer test failed")
