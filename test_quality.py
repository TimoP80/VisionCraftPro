#!/usr/bin/env python3
"""
Test output quality and potential degradation scenarios
"""

import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from prompt_enhancer import PromptEnhancer

async def test_quality_degradation():
    """Test for potential quality degradation in prompt enhancement"""
    enhancer = PromptEnhancer()
    
    # Test cases that might cause quality issues
    test_scenarios = [
        # Very short prompts that might get over-enhanced
        ("a", "cinematic", "ultra"),
        ("cat", "artistic", "ultra"),
        ("sunset", "realistic", "ultra"),
        
        # Prompts that are already detailed
        ("a highly detailed, professional photograph of a beautiful sunset with dramatic lighting", "cinematic", "medium"),
        ("a masterpiece artwork with intricate details and vibrant colors", "artistic", "medium"),
        ("a photorealistic image with sharp focus and 8k resolution", "photorealistic", "medium"),
        
        # Prompts with conflicting styles
        ("a beautiful sunset", "cinematic", "medium"),  # Normal case
        ("a beautiful sunset", "anime", "medium"),      # Style change
        ("a beautiful sunset", "scifi", "medium"),      # Style change
        
        # Edge case prompts
        ("", "cinematic", "medium"),                    # Empty prompt
        (" ", "cinematic", "medium"),                   # Whitespace only
        ("a" * 100, "cinematic", "medium"),             # Very long prompt
        
        # Test consistency
        ("a beautiful sunset", "cinematic", "medium"),
        ("a beautiful sunset", "cinematic", "medium"),
        ("a beautiful sunset", "cinematic", "medium"),
    ]
    
    print("Testing output quality and consistency...")
    print("=" * 60)
    
    results = []
    for i, (prompt, style, detail_level) in enumerate(test_scenarios):
        print(f"\nTest {i+1}: '{prompt}' | Style: {style} | Detail: {detail_level}")
        try:
            result = await enhancer.enhance_prompt(prompt, style, detail_level)
            enhanced = result['prompt']
            original = result['original_prompt']
            
            # Calculate metrics
            length_increase = len(enhanced) - len(original)
            length_ratio = len(enhanced) / max(len(original), 1)
            
            print(f"  Original length: {len(original)}")
            print(f"  Enhanced length: {len(enhanced)}")
            print(f"  Length increase: {length_increase} (+{length_ratio:.1f}x)")
            print(f"  AI Enhanced: {result.get('ai_enhanced', False)}")
            print(f"  Enhanced: {enhanced[:100]}{'...' if len(enhanced) > 100 else ''}")
            
            # Check for potential quality issues
            if length_increase < 0:
                print(f"  WARNING: Enhanced prompt is shorter than original!")
            elif length_ratio > 10:
                print(f"  WARNING: Extreme length increase (>10x)!")
            elif length_ratio < 1.1 and len(original) > 10:
                print(f"  WARNING: Minimal enhancement for non-trivial prompt!")
                
            # Check for repetitive content
            if enhanced.count(", ") > 10:
                print(f"  WARNING: Potentially over-enhanced with too many terms!")
                
            results.append({
                'test': i+1,
                'prompt': prompt,
                'style': style,
                'detail': detail_level,
                'original': original,
                'enhanced': enhanced,
                'length_increase': length_increase,
                'length_ratio': length_ratio,
                'ai_enhanced': result.get('ai_enhanced', False)
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                'test': i+1,
                'prompt': prompt,
                'style': style,
                'detail': detail_level,
                'error': str(e)
            })
    
    # Summary
    print("\n\nSUMMARY")
    print("=" * 60)
    successful_tests = [r for r in results if 'error' not in r]
    if successful_tests:
        avg_length_increase = sum(r['length_increase'] for r in successful_tests) / len(successful_tests)
        avg_length_ratio = sum(r['length_ratio'] for r in successful_tests) / len(successful_tests)
        print(f"Successful tests: {len(successful_tests)}/{len(results)}")
        print(f"Average length increase: {avg_length_increase:.1f} characters")
        print(f"Average length ratio: {avg_length_ratio:.1f}x")
        
        # Find extreme cases
        max_increase = max(successful_tests, key=lambda x: x['length_increase'])
        min_increase = min(successful_tests, key=lambda x: x['length_increase'])
        print(f"Maximum increase: Test {max_increase['test']} (+{max_increase['length_increase']} chars)")
        print(f"Minimum increase: Test {min_increase['test']} (+{min_increase['length_increase']} chars)")

if __name__ == "__main__":
    asyncio.run(test_quality_degradation())