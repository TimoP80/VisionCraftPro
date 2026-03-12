#!/usr/bin/env python3
"""
Test performance of prompt enhancement
"""

import asyncio
import sys
import os
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from prompt_enhancer import PromptEnhancer

async def test_performance():
    """Test performance of prompt enhancement"""
    enhancer = PromptEnhancer()
    
    test_prompts = [
        "a beautiful sunset",
        "a cat sitting on a windowsill",
        "a futuristic cityscape with flying cars",
        "a portrait of a woman with flowing hair",
        "a landscape with mountains and a lake",
        "a still life with fruits and flowers",
        "an abstract painting with geometric shapes",
        "a vintage photograph of a street scene",
        "a macro shot of a dewdrop on a leaf",
        "a wide angle view of a canyon at sunset"
    ]
    
    print("Testing performance...")
    print("=" * 50)
    
    # Test synchronous version
    print("\nTesting synchronous enhancement:")
    start_time = time.time()
    for i, prompt in enumerate(test_prompts):
        prompt_start = time.time()
        result = enhancer.enhance_prompt_sync(prompt, "cinematic", "medium")
        prompt_end = time.time()
        print(f"  Prompt {i+1}: {prompt_end - prompt_start:.3f}s - {prompt[:30]}...")
    sync_end = time.time()
    print(f"  Total synchronous time: {sync_end - start_time:.3f}s")
    print(f"  Average per prompt: {(sync_end - start_time) / len(test_prompts):.3f}s")
    
    # Test asynchronous version
    print("\nTesting asynchronous enhancement:")
    start_time = time.time()
    tasks = []
    for i, prompt in enumerate(test_prompts):
        task_start = time.time()
        task = enhancer.enhance_prompt(prompt, "cinematic", "medium")
        tasks.append((task, prompt, i+1, task_start))
    
    results = await asyncio.gather(*[task for task, _, _, _ in tasks])
    end_time = time.time()
    
    for i, (_, prompt, prompt_num, task_start) in enumerate(tasks):
        task_end = time.time()
        print(f"  Prompt {prompt_num}: {task_end - task_start:.3f}s - {prompt[:30]}...")
    
    print(f"  Total asynchronous time: {end_time - start_time:.3f}s")
    print(f"  Average per prompt: {(end_time - start_time) / len(test_prompts):.3f}s")
    
    # Test with different detail levels
    print("\nTesting different detail levels:")
    detail_levels = ["basic", "medium", "high", "ultra"]
    for level in detail_levels:
        start_time = time.time()
        for prompt in test_prompts[:3]:  # Test with first 3 prompts
            result = enhancer.enhance_prompt_sync(prompt, "cinematic", level)
        level_end = time.time()
        print(f"  {level:>6}: {(level_end - start_time) / 3:.3f}s per prompt")
    
    # Test with different styles
    print("\nTesting different styles:")
    styles = ["cinematic", "artistic", "realistic", "fantasy", "scifi", "anime"]
    for style in styles:
        start_time = time.time()
        for prompt in test_prompts[:3]:  # Test with first 3 prompts
            result = enhancer.enhance_prompt_sync(prompt, style, "medium")
        style_end = time.time()
        print(f"  {style:>12}: {(style_end - start_time) / 3:.3f}s per prompt")

if __name__ == "__main__":
    asyncio.run(test_performance())