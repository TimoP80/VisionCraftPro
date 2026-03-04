#!/usr/bin/env python3
"""
Test Gemini AI enhancement after fixes
"""

import asyncio
import os

# Set the API key
os.environ["GEMINI_API_KEY"] = "AIzaSyCsGf1WwZu20G9pHcf1mWFaCP1SCnAgjec"

async def test_gemini():
    try:
        from prompt_enhancer import PromptEnhancer
        
        enhancer = PromptEnhancer()
        print(f"AI Available: {enhancer.ai_available}")
        print(f"Gemini Key Set: {bool(enhancer.gemini_key)}")
        
        if enhancer.ai_available:
            print("🚀 Testing Gemini AI enhancement...")
            result = await enhancer.enhance_prompt("a beautiful woman", "photorealistic", "medium")
            
            print(f"✅ AI Enhanced: {result.get('ai_enhanced', False)}")
            print(f"📝 Enhanced prompt: {result.get('prompt', 'No prompt')}")
            print(f"🎯 Style: {result.get('style')}")
            print(f"🔧 Detail Level: {result.get('detail_level')}")
            
            # Show the difference
            original = result.get('original_prompt', '')
            enhanced = result.get('prompt', '')
            
            print(f"\n📊 Comparison:")
            print(f"Original: '{original}'")
            print(f"Enhanced: '{enhanced}'")
            print(f"Length increase: {len(enhanced) - len(original)} characters")
            
        else:
            print("❌ AI not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
