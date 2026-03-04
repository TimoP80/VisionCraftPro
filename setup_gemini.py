#!/usr/bin/env python3
"""
Setup Gemini API key for AI prompt enhancement
"""

import os
import sys

def setup_gemini_key():
    gemini_key = "AIzaSyCsGf1WwZu20G9pHcf1mWFaCP1SCnAgjec"
    
    # Set environment variable for current session
    os.environ["GEMINI_API_KEY"] = gemini_key
    
    print("✅ Gemini API key set for current session")
    print("🔑 Key: AIzaSyCsGf1WwZu20G9pHcf1mWFaCP1SCnAgjec")
    print()
    
    # Test if it works
    try:
        from prompt_enhancer import PromptEnhancer
        import asyncio
        
        async def test_ai():
            enhancer = PromptEnhancer()
            print(f"AI Available: {enhancer.ai_available}")
            print(f"Gemini Key Set: {bool(enhancer.gemini_key)}")
            
            if enhancer.ai_available:
                print("🚀 Testing AI enhancement...")
                result = await enhancer.enhance_prompt("a beautiful sunset", "cinematic", "medium")
                print(f"✅ AI Enhanced: {result.get('ai_enhanced', False)}")
                print(f"📝 Enhanced prompt: {result.get('prompt', 'No prompt')[:100]}...")
            else:
                print("❌ AI not available")
        
        asyncio.run(test_ai())
        
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
    
    print()
    print("📝 To make this permanent, add to your environment:")
    print("   Windows: set GEMINI_API_KEY=AIzaSyCsGf1WwZu20G9pHcf1mWFaCP1SCnAgjec")
    print("   Linux/Mac: export GEMINI_API_KEY=AIzaSyCsGf1WwZu20G9pHcf1mWFaCP1SCnAgjec")
    print()
    print("🔄 Restart the server with: python app.py")

if __name__ == "__main__":
    setup_gemini_key()
