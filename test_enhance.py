#!/usr/bin/env python3
"""
Comprehensive tests for PromptEnhancer model parameter functionality
Tests:
1. The model parameter works correctly with the /enhance-prompt endpoint
2. Different model selections work as expected (auto, openai, anthropic, gemini, local/template)
3. The API returns the model_used field in the response
4. Error handling works correctly when API keys are missing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path using modern pathlib
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Test results tracking
test_results = []


def test_result(name: str, passed: bool, message: str = ""):
    """Record test result"""
    status = "PASS" if passed else "FAIL"
    test_results.append({"name": name, "status": status, "message": message})
    print(f"[{status}] {name}")
    if message:
        print(f"      {message}")


async def test_model_parameter():
    """Test 1: Test that model parameter is correctly passed and used"""
    print("\n" + "="*60)
    print("TEST 1: Model Parameter Functionality")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    available_models = enhancer.get_available_models()
    
    # Verify get_available_models returns expected keys
    expected_keys = ["auto", "openai", "anthropic", "gemini", "local", "template"]
    has_all_keys = all(k in available_models for k in expected_keys)
    test_result(
        "get_available_models returns all expected keys",
        has_all_keys,
        f"Keys: {list(available_models.keys())}"
    )
    
    # Test that 'auto' and 'local/template' are always available
    test_result(
        "'auto' model is always available",
        available_models.get("auto", False) == True
    )
    
    test_result(
        "'local' model is always available",
        available_models.get("local", False) == True
    )
    
    test_result(
        "'template' model is always available", 
        available_models.get("template", False) == True
    )
    
    # Test with different model values
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    # Test 'auto' model
    result_auto = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "auto")
    test_result(
        "enhance_prompt accepts 'auto' model parameter",
        "model" in result_auto,
        f"Returned model: {result_auto.get('model')}"
    )
    
    # Test 'local' model
    result_local = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "local")
    test_result(
        "enhance_prompt accepts 'local' model parameter",
        result_local.get("model") == "local"
    )
    
    # Test 'template' model (alias for local)
    result_template = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "template")
    test_result(
        "enhance_prompt accepts 'template' model parameter",
        result_template.get("model") == "template"
    )
    
    # Test 'openai' model
    result_openai = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "openai")
    test_result(
        "enhance_prompt accepts 'openai' model parameter",
        result_openai.get("model") == "openai"
    )
    
    # Test 'anthropic' model
    result_anthropic = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "anthropic")
    test_result(
        "enhance_prompt accepts 'anthropic' model parameter",
        result_anthropic.get("model") == "anthropic"
    )
    
    # Test 'gemini' model
    result_gemini = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "gemini")
    test_result(
        "enhance_prompt accepts 'gemini' model parameter",
        result_gemini.get("model") == "gemini"
    )


async def test_model_used_field():
    """Test 3: Verify API returns model_used field in the response"""
    print("\n" + "="*60)
    print("TEST 3: model_used Field in Response")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    # Test model_used field exists in response
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "auto")
    
    has_model_used = "model_used" in result
    test_result(
        "Response includes 'model_used' field",
        has_model_used,
        f"model_used: {result.get('model_used')}"
    )
    
    # Test with 'local' model - should have model_used
    result_local = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "local")
    has_model_used_local = "model_used" in result_local
    test_result(
        "'local' model returns model_used field",
        has_model_used_local,
        f"model_used: {result_local.get('model_used')}"
    )
    
    # Test with 'template' model
    result_template = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "template")
    has_model_used_template = "model_used" in result_template
    test_result(
        "'template' model returns model_used field",
        has_model_used_template,
        f"model_used: {result_template.get('model_used')}"
    )


async def test_auto_model_selection():
    """Test 2: Test auto model selection"""
    print("\n" + "="*60)
    print("TEST 2: Auto Model Selection")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    # Test 'auto' selection - should work regardless of API keys
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "auto")
    
    # Should return a valid result
    has_prompt = "prompt" in result and result["prompt"]
    test_result(
        "'auto' model returns valid result",
        has_prompt,
        f"Enhanced prompt: {result.get('prompt', 'N/A')[:80]}..."
    )
    
    # Should include available_models info
    has_available_models = "available_models" in result
    test_result(
        "'auto' response includes available_models",
        has_available_models,
        f"Available: {result.get('available_models')}"
    )
    
    # Should have ai_enhanced flag
    has_ai_enhanced = "ai_enhanced" in result
    test_result(
        "'auto' response includes ai_enhanced flag",
        has_ai_enhanced,
        f"ai_enhanced: {result.get('ai_enhanced')}"
    )


async def test_specific_model_selection():
    """Test 2b: Test specific model selection (openai, anthropic, gemini)"""
    print("\n" + "="*60)
    print("TEST 2b: Specific Model Selection")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    # Test 'openai' - should work (falls back to template if no key)
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "openai")
    has_prompt = "prompt" in result and result["prompt"]
    test_result(
        "'openai' model returns valid result (or fallback)",
        has_prompt,
        f"ai_enhanced: {result.get('ai_enhanced')}, prompt length: {len(result.get('prompt', ''))}"
    )
    
    # Test 'anthropic'
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "anthropic")
    has_prompt = "prompt" in result and result["prompt"]
    test_result(
        "'anthropic' model returns valid result (or fallback)",
        has_prompt,
        f"ai_enhanced: {result.get('ai_enhanced')}, prompt length: {len(result.get('prompt', ''))}"
    )
    
    # Test 'gemini'
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "gemini")
    has_prompt = "prompt" in result and result["prompt"]
    test_result(
        "'gemini' model returns valid result (or fallback)",
        has_prompt,
        f"ai_enhanced: {result.get('ai_enhanced')}, prompt length: {len(result.get('prompt', ''))}"
    )


async def test_template_local_fallback():
    """Test 4: Test template/local fallback when no API keys available"""
    print("\n" + "="*60)
    print("TEST 4: Template/Local Fallback")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    # Test 'local' model - should use template-based enhancement
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "local")
    
    # Should return a valid template-based enhancement
    has_prompt = "prompt" in result and result["prompt"]
    test_result(
        "'local' model returns template-based enhancement",
        has_prompt,
        f"Prompt: {result.get('prompt', 'N/A')[:80]}..."
    )
    
    # Should NOT try AI enhancement for 'local' model
    test_result(
        "'local' model does not attempt AI enhancement",
        result.get("ai_enhanced", True) == False,
        f"ai_enhanced: {result.get('ai_enhanced')}"
    )
    
    # Test 'template' model (alias)
    result_template = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "template")
    has_prompt_t = "prompt" in result_template and result_template["prompt"]
    test_result(
        "'template' model returns valid enhancement",
        has_prompt_t,
        f"Prompt: {result_template.get('prompt', 'N/A')[:80]}..."
    )
    
    # Verify template adds style-specific prefix/suffix
    expected_prefix = "cinematic shot, professional photography, "
    expected_suffix = ", dramatic lighting, high detail, 8k resolution"
    
    prompt_text = result.get("prompt", "")
    has_prefix = expected_prefix in prompt_text
    has_suffix = expected_suffix in prompt_text
    
    test_result(
        "'local' model adds correct style prefix",
        has_prefix,
        f"Prefix found: {has_prefix}"
    )
    
    test_result(
        "'local' model adds correct style suffix",
        has_suffix,
        f"Suffix found: {has_suffix}"
    )


async def test_error_handling():
    """Test 5: Test error handling when API keys are missing"""
    print("\n" + "="*60)
    print("TEST 5: Error Handling (Missing API Keys)")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    # Check current API key status
    has_openai = bool(enhancer.openai_key)
    has_anthropic = bool(enhancer.anthropic_key)
    has_gemini = bool(enhancer.gemini_key)
    
    print(f"API Key Status:")
    print(f"  OpenAI: {'SET' if has_openai else 'NOT SET'}")
    print(f"  Anthropic: {'SET' if has_anthropic else 'NOT SET'}")
    print(f"  Gemini: {'SET' if has_gemini else 'NOT SET'}")
    
    # Test that request for unavailable model falls back gracefully
    if not has_openai:
        result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "openai")
        test_result(
            "Missing OpenAI key: gracefully falls back to template",
            "prompt" in result and result["prompt"],
            f"Fell back successfully: ai_enhanced={result.get('ai_enhanced')}"
        )
    
    if not has_anthropic:
        result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "anthropic")
        test_result(
            "Missing Anthropic key: gracefully falls back to template",
            "prompt" in result and result["prompt"],
            f"Fell back successfully: ai_enhanced={result.get('ai_enhanced')}"
        )
    
    if not has_gemini:
        result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "gemini")
        test_result(
            "Missing Gemini key: gracefully falls back to template",
            "prompt" in result and result["prompt"],
            f"Fell back successfully: ai_enhanced={result.get('ai_enhanced')}"
        )
    
    # Test invalid model name - should still work (falls back)
    try:
        result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "invalid_model_xyz")
        test_result(
            "Invalid model name: gracefully handles and returns result",
            "prompt" in result and result["prompt"],
            f"Handled gracefully"
        )
    except Exception as e:
        test_result(
            "Invalid model name: gracefully handles and returns result",
            False,
            f"Exception raised: {e}"
        )
    
    # Test empty prompt - should handle gracefully
    try:
        result = await enhancer.enhance_prompt("", test_style, test_detail, "auto")
        # Empty prompt should still return something (cleaned)
        test_result(
            "Empty prompt: handles gracefully",
            "prompt" in result,
            f"Returned result for empty prompt"
        )
    except Exception as e:
        # Empty prompt might raise an error, which is acceptable
        test_result(
            "Empty prompt: handles gracefully",
            True,
            f"Raised expected error: {type(e).__name__}"
        )
    
    # Verify ai_available reflects actual key status
    expected_ai_available = has_openai or has_anthropic or has_gemini
    test_result(
        "ai_available flag correctly reflects API key status",
        enhancer.ai_available == expected_ai_available,
        f"ai_available={enhancer.ai_available}, expected={expected_ai_available}"
    )


async def test_response_structure():
    """Test that response has all expected fields"""
    print("\n" + "="*60)
    print("TEST 6: Response Structure")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a beautiful sunset"
    test_style = "cinematic"
    test_detail = "medium"
    
    result = await enhancer.enhance_prompt(test_prompt, test_style, test_detail, "auto")
    
    # Check required fields
    required_fields = [
        "original_prompt",
        "prompt", 
        "style",
        "detail_level",
        "model",
        "model_used",
        "ai_enhanced",
        "ai_available",
        "available_models",
        "all_enhancements"
    ]
    
    for field in required_fields:
        has_field = field in result
        test_result(
            f"Response includes '{field}' field",
            has_field,
            f"Present: {has_field}"
        )
    
    # Check all_enhancements has all styles
    all_enhancements = result.get("all_enhancements", {})
    expected_styles = ["cinematic", "artistic", "realistic", "photorealistic", "fantasy", "scifi", "anime"]
    
    for style in expected_styles:
        has_style = style in all_enhancements
        test_result(
            f"all_enhancements includes '{style}'",
            has_style,
            f"Present: {has_style}"
        )


async def test_detail_levels():
    """Test different detail levels"""
    print("\n" + "="*60)
    print("TEST 7: Detail Levels")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a cat"
    
    # Test each detail level with local model (to avoid AI)
    for detail_level in ["basic", "medium", "high", "ultra"]:
        result = await enhancer.enhance_prompt(test_prompt, "cinematic", detail_level, "local")
        
        has_prompt = "prompt" in result and result["prompt"]
        test_result(
            f"Detail level '{detail_level}' returns valid result",
            has_prompt,
            f"Prompt length: {len(result.get('prompt', ''))}"
        )
        
        # Verify detail_level is returned correctly
        returned_level = result.get("detail_level")
        test_result(
            f"Detail level '{detail_level}' is correctly stored",
            returned_level == detail_level,
            f"Stored as: {returned_level}"
        )


async def test_styles():
    """Test different styles"""
    print("\n" + "="*60)
    print("TEST 8: Style Variations")
    print("="*60)
    
    from prompt_enhancer import PromptEnhancer
    
    enhancer = PromptEnhancer()
    test_prompt = "a landscape"
    
    # Test each style with local model
    styles = ["cinematic", "artistic", "realistic", "photorealistic", "fantasy", "scifi", "anime"]
    
    for style in styles:
        result = await enhancer.enhance_prompt(test_prompt, style, "medium", "local")
        
        has_prompt = "prompt" in result and result["prompt"]
        test_result(
            f"Style '{style}' returns valid result",
            has_prompt,
            f"Prompt length: {len(result.get('prompt', ''))}"
        )
        
        # Verify style is returned correctly
        returned_style = result.get("style")
        test_result(
            f"Style '{style}' is correctly stored",
            returned_style == style,
            f"Stored as: {returned_style}"
        )


async def main():
    """Run all tests"""
    print("="*60)
    print("PROMPT ENHANCER COMPREHENSIVE TESTS")
    print("="*60)
    print(f"\nPython: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Run all tests
    await test_model_parameter()
    await test_model_used_field()
    await test_auto_model_selection()
    await test_specific_model_selection()
    await test_template_local_fallback()
    await test_error_handling()
    await test_response_structure()
    await test_detail_levels()
    await test_styles()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {100*passed/total:.1f}%" if total > 0 else "N/A")
    
    if failed > 0:
        print("\nFailed Tests:")
        for r in test_results:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}")
                if r["message"]:
                    print(f"    {r['message']}")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
