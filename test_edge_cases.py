#!/usr/bin/env python3
"""
Test edge cases for prompt enhancement
"""

import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from prompt_enhancer import PromptEnhancer

async def test_edge_cases():
    """Test various edge cases for prompt enhancement"""
    enhancer = PromptEnhancer()
    
    test_cases = [
        # Empty prompt
        ("", "cinematic", "medium"),
        # Very short prompt
        ("a", "cinematic", "medium"),
        # Very long prompt
        ("a " * 1000, "cinematic", "medium"),
        # Prompt with special characters
        ("a beautiful sunset! @#$%^&*()", "cinematic", "medium"),
        # Prompt with numbers
        ("a beautiful sunset 2023", "cinematic", "medium"),
        # Prompt with newlines and tabs
        ("a beautiful\nsunset\tscene", "cinematic", "medium"),
        # Prompt with only spaces
        ("   ", "cinematic", "medium"),
        # Prompt with unicode (using ASCII representation to avoid encoding issues)
        ("a beautiful sunset [unicode]", "cinematic", "medium"),
        # Different styles
        ("a cat", "artistic", "medium"),
        ("a cat", "realistic", "medium"),
        ("a cat", "fantasy", "medium"),
        ("a cat", "scifi", "medium"),
        ("a cat", "anime", "medium"),
        # Different detail levels
        ("a cat", "cinematic", "basic"),
        ("a cat", "cinematic", "high"),
        ("a cat", "cinematic", "ultra"),
        # Invalid style (should default to cinematic)
        ("a cat", "invalid_style", "medium"),
        # Invalid detail level (should default to medium)
        ("a cat", "cinematic", "invalid_level"),
    ]
    
    print("Testing edge cases...")
    print("=" * 50)
    
    for i, (prompt, style, detail_level) in enumerate(test_cases):
         safe_prompt = repr(prompt[:50])[1:-1]  # Remove quotes from repr
         if len(prompt) > 50:
             safe_prompt += "..."
         print(f"\nTest {i+1}: {safe_prompt} | Style: {style} | Detail: {detail_level}")
         try:
             result = await enhancer.enhance_prompt(prompt, style, detail_level)
             print(f"  SUCCESS: {result['prompt'][:100]}{'...' if len(result['prompt']) > 100 else ''}")
             print(f"  AI Enhanced: {result.get('ai_enhanced', False)}")
         except Exception as e:
             print(f"  ERROR: {e}")
    
    # Test synchronous version
    print("\n\nTesting synchronous version...")
    print("=" * 50)
    try:
        result = enhancer.enhance_prompt_sync("a beautiful sunset", "cinematic", "medium")
        print(f"SUCCESS: {result['prompt'][:100]}{'...' if len(result['prompt']) > 100 else ''}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

if __name__ == "__main__":
    asyncio.run(test_edge_cases())