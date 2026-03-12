"""
Prompt Enhancer for VisionCraft Pro
AI-powered prompt enhancement and improvement
"""

import re
import asyncio
from typing import Dict, List, Optional
import json
import os
import random

class PromptEnhancer:
    """Enhance prompts with different styles and detail levels"""
    
    def __init__(self):
        self.style_templates = {
            "cinematic": {
                "prefix": "cinematic shot, professional photography, ",
                "suffix": ", dramatic lighting, high detail, 8k resolution",
                "quality_terms": ["masterpiece", "award-winning", "professional", "cinematic"]
            },
            "artistic": {
                "prefix": "artistic masterpiece, fine art, ",
                "suffix": ", expressive, creative, unique style, detailed brushwork",
                "quality_terms": ["artistic", "creative", "expressive", "masterpiece"]
            },
            "realistic": {
                "prefix": "photorealistic, realistic, ",
                "suffix": ", highly detailed, accurate, lifelike, professional photography",
                "quality_terms": ["realistic", "photorealistic", "lifelike", "detailed"]
            },
            "photorealistic": {
                "prefix": "photorealistic, high resolution, professional photography, ",
                "suffix": ", sharp focus, 8k, highly detailed, realistic textures",
                "quality_terms": ["photorealistic", "realistic", "professional", "8k"]
            },
            "fantasy": {
                "prefix": "fantasy art, magical, ethereal, ",
                "suffix": ", enchanting, mystical, detailed fantasy elements",
                "quality_terms": ["magical", "ethereal", "fantasy", "enchanting"]
            },
            "scifi": {
                "prefix": "sci-fi, futuristic, high-tech, ",
                "suffix": ", advanced technology, sleek design, detailed sci-fi elements",
                "quality_terms": ["futuristic", "high-tech", "advanced", "sleek"]
            },
            "anime": {
                "prefix": "anime style, vibrant colors, clean lines, ",
                "suffix": ", detailed background, expressive characters, high quality anime art",
                "quality_terms": ["anime", "manga", "vibrant", "expressive"]
            }
        }
        
        self.detail_levels = {
            "basic": {
                "multiplier": 1.0,
                "add_lighting": False,
                "add_composition": False,
                "add_technical": False
            },
            "medium": {
                "multiplier": 1.5,
                "add_lighting": True,
                "add_composition": False,
                "add_technical": False
            },
            "high": {
                "multiplier": 2.0,
                "add_lighting": True,
                "add_composition": True,
                "add_technical": False
            },
            "ultra": {
                "multiplier": 2.5,
                "add_lighting": True,
                "add_composition": True,
                "add_technical": True
            }
        }
        
        self.enhancement_words = [
            "highly detailed", "intricate", "professional", "masterpiece",
            "stunning", "beautiful", "amazing", "incredible", "breathtaking",
            "magnificent", "extraordinary", "remarkable", "spectacular"
        ]
        
        self.lighting_terms = [
            "dramatic lighting", "soft lighting", "golden hour", "blue hour",
            "rim lighting", "backlighting", "studio lighting", "natural light",
            "volumetric lighting", "cinematic lighting", "ambient light"
        ]
        
        self.composition_terms = [
            "rule of thirds", "leading lines", "symmetrical composition",
            "dynamic composition", "balanced composition", "depth of field",
            "foreground, middle ground, background", "wide angle", "close-up"
        ]
        
        self.technical_terms = [
            "8k resolution", "ultra high definition", "sharp focus", "detailed texture",
            "professional photography", "dslr", "shot on professional camera",
            "high quality", "ultra detailed", "sharp details", "crisp details"
        ]
        
        # Check for AI API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        self.ai_available = bool(self.openai_key or self.anthropic_key or self.gemini_key)
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get available AI models based on configured API keys"""
        return {
            "auto": True,  # Always available - tries all available models
            "openai": bool(self.openai_key),
            "anthropic": bool(self.anthropic_key),
            "gemini": bool(self.gemini_key),
            "local": True,  # Template-based is always available
            "template": True  # Alias for local
        }
    
    async def enhance_with_ai(self, prompt: str, style: str = "cinematic", model: str = "auto") -> Dict:
        """Try to enhance prompt using real AI LLM
        
        Args:
            prompt: The original prompt to enhance
            style: The enhancement style (cinematic, artistic, etc.)
            model: The AI model to use ("auto", "openai", "anthropic", "gemini", "local", "template")
        
        Returns:
            Dict with keys:
                - "enhanced_prompt": The enhanced prompt string
                - "fallback_occurred": Boolean indicating if fallback to template occurred
                - "fallback_reason": Reason for fallback (None if no fallback)
                - "model_used": The model that was actually used
        """
        # Normalize model name
        model = model.lower() if model else "auto"
        
        if model in ("local", "template"):
            # Template-based is always available
            print(f"[AI] Using template-based enhancement (model={model})")
            return {
                "enhanced_prompt": self.add_style_enhancement(prompt, style),
                "fallback_occurred": True,
                "fallback_reason": "template_mode",
                "model_used": model
            }
        
        if not self.ai_available and model != "auto":
            # No AI available, but specific model requested
            # Fall back to template-based
            print(f"[AI] No AI API keys available, using template-based enhancement")
            return {
                "enhanced_prompt": self.add_style_enhancement(prompt, style),
                "fallback_occurred": True,
                "fallback_reason": "no_api_keys",
                "model_used": "template"
            }
        
        # Determine which model(s) to try based on the request
        models_to_try = []
        
        if model == "auto":
            # Try all available AI models in priority order
            if self.openai_key:
                models_to_try.append("openai")
            if self.anthropic_key:
                models_to_try.append("anthropic")
            if self.gemini_key:
                models_to_try.append("gemini")
        else:
            # Try specific requested model
            if model == "openai" and self.openai_key:
                models_to_try.append("openai")
            elif model == "anthropic" and self.anthropic_key:
                models_to_try.append("anthropic")
            elif model == "gemini" and self.gemini_key:
                models_to_try.append("gemini")
            else:
                # Requested model not available
                print(f"[AI] Requested model '{model}' is not available (no API key)")
                # Fall back to template-based
                return {
                    "enhanced_prompt": self.add_style_enhancement(prompt, style),
                    "fallback_occurred": True,
                    "fallback_reason": f"model_unavailable:{model}",
                    "model_used": "template"
                }
        
        if not models_to_try:
            print(f"[AI] No AI models available, using template-based enhancement")
            return {
                "enhanced_prompt": self.add_style_enhancement(prompt, style),
                "fallback_occurred": True,
                "fallback_reason": "no_ai_models_available",
                "model_used": "template"
            }
        
        print(f"[AI] Trying AI models in order: {models_to_try}")
        
        # Try each model in order until one succeeds
        for model_name in models_to_try:
            try:
                if model_name == "openai":
                    result = await self._enhance_with_openai(prompt, style)
                    if result:
                        print(f"[AI] OpenAI enhancement succeeded")
                        return {
                            "enhanced_prompt": result,
                            "fallback_occurred": False,
                            "fallback_reason": None,
                            "model_used": "openai"
                        }
                elif model_name == "anthropic":
                    result = await self._enhance_with_anthropic(prompt, style)
                    if result:
                        print(f"[AI] Anthropic enhancement succeeded")
                        return {
                            "enhanced_prompt": result,
                            "fallback_occurred": False,
                            "fallback_reason": None,
                            "model_used": "anthropic"
                        }
                elif model_name == "gemini":
                    result = await self._enhance_with_gemini(prompt, style)
                    if result:
                        print(f"[AI] Gemini enhancement succeeded")
                        return {
                            "enhanced_prompt": result,
                            "fallback_occurred": False,
                            "fallback_reason": None,
                            "model_used": "gemini"
                        }
            except Exception as e:
                print(f"[AI] {model_name} enhancement failed: {e}, trying next model...")
        
        # All AI models failed, fall back to template-based
        print(f"[AI] All AI models failed, using template-based enhancement")
        return {
            "enhanced_prompt": self.add_style_enhancement(prompt, style),
            "fallback_occurred": True,
            "fallback_reason": "all_ai_models_failed",
            "model_used": "template"
        }
    
    async def _enhance_with_openai(self, prompt: str, style: str) -> str:
        """Enhance prompt using OpenAI"""
        if not self.openai_key:
            return None
            
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            system_prompt = f"""You are an expert prompt engineer for AI image generation. 
            Your task is to expand simple user prompts into detailed, descriptive prompts that will generate better images.
            
            Focus on {style} style with these characteristics:
            {self._get_style_description(style)}
            
            Rules:
            - Keep the core concept intact
            - Add descriptive details and artistic elements
            - Include lighting, composition, and technical terms
            - Make it 2-3 times more descriptive
            - Return ONLY the enhanced prompt, no explanations
            """
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Enhance this prompt for image generation: {prompt}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[AI] OpenAI enhancement failed: {e}")
            return None
    
    async def _enhance_with_anthropic(self, prompt: str, style: str) -> str:
        """Enhance prompt using Anthropic Claude"""
        if not self.anthropic_key:
            return None
            
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            system_prompt = f"""You are an expert prompt engineer for AI image generation. 
            Your task is to expand simple user prompts into detailed, descriptive prompts that will generate better images.
            
            Focus on {style} style with these characteristics:
            {self._get_style_description(style)}
            
            Rules:
            - Keep the core concept intact
            - Add descriptive details and artistic elements
            - Include lighting, composition, and technical terms
            - Make it 2-3 times more descriptive
            - Return ONLY the enhanced prompt, no explanations
            """
            
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=200,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Enhance this prompt for image generation: {prompt}"}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"[AI] Claude enhancement failed: {e}")
            return None
    
    async def _enhance_with_gemini(self, prompt: str, style: str) -> str:
        """Enhance prompt using Google Gemini"""
        if not self.gemini_key:
            return None
            
        # Consistent default model for both API versions
        default_model = "gemini-2.5-flash"
        model_name = os.getenv("GEMINI_MODEL", default_model)
        # Timeout for Gemini API calls (in seconds)
        timeout_seconds = 30
        
        try:
            # Try new google.genai first, fallback to old google.generativeai
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                
                prompt_text = f"""You are an expert prompt engineer for AI image generation. 
                Your task is to expand simple user prompts into detailed, descriptive prompts that will generate better images.
                
                Focus on {style} style with these characteristics:
                {self._get_style_description(style)}
                
                Rules:
                - Keep the core concept intact
                - Add descriptive details and artistic elements
                - Include lighting, composition, and technical terms
                - Make it 2-3 times more descriptive
                - Return ONLY the enhanced prompt, no explanations
                
                Enhance this prompt for image generation: {prompt}"""
                
                # Use asyncio timeout for the Gemini API call
                try:
                    async def call_gemini_genai():
                        return await asyncio.wait_for(
                            asyncio.to_thread(
                                client.models.generate_content,
                                model=model_name,
                                contents=prompt_text
                            ),
                            timeout=timeout_seconds
                        )
                    
                    response = await call_gemini_genai()
                    return response.text.strip()
                    
                except asyncio.TimeoutError:
                    print(f"[AI] Gemini (genai) request timed out after {timeout_seconds} seconds")
                    return None
                except ImportError:
                    raise  # Re-raise ImportError to try old package
                except Exception as e:
                    # Specific error handling for genai client errors
                    error_msg = str(e).lower()
                    if "api" in error_msg or "key" in error_msg or "permission" in error_msg:
                        print(f"[AI] Gemini (genai) API error: {e}")
                        return None
                    elif "timeout" in error_msg or "deadline" in error_msg:
                        print(f"[AI] Gemini (genai) timeout error: {e}")
                        return None
                    else:
                        print(f"[AI] Gemini (genai) error: {e}")
                        return None
                    
            except ImportError as ie:
                # Fallback to old package
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.gemini_key)
                    model = genai.GenerativeModel(model_name)
                    
                    prompt_text = f"""You are an expert prompt engineer for AI image generation. 
                    Your task is to expand simple user prompts into detailed, descriptive prompts that will generate better images.
                    
                    Focus on {style} style with these characteristics:
                    {self._get_style_description(style)}
                    
                    Rules:
                    - Keep the core concept intact
                    - Add descriptive details and artistic elements
                    - Include lighting, composition, and technical terms
                    - Make it 2-3 times more descriptive
                    - Return ONLY the enhanced prompt, no explanations
                    
                    Enhance this prompt for image generation: {prompt}"""
                    
                    # Use asyncio timeout for the Gemini API call
                    try:
                        async def call_gemini_old():
                            return await asyncio.wait_for(
                                asyncio.to_thread(model.generate_content, prompt_text),
                                timeout=timeout_seconds
                            )
                        
                        response = await call_gemini_old()
                        return response.text.strip()
                        
                    except asyncio.TimeoutError:
                        print(f"[AI] Gemini (old API) request timed out after {timeout_seconds} seconds")
                        return None
                    except Exception as e:
                        # Specific error handling for old API errors
                        error_msg = str(e).lower()
                        if "api" in error_msg or "key" in error_msg or "permission" in error_msg:
                            print(f"[AI] Gemini (old API) API error: {e}")
                            return None
                        elif "timeout" in error_msg or "deadline" in error_msg:
                            print(f"[AI] Gemini (old API) timeout error: {e}")
                            return None
                        elif "429" in error_msg or "quota" in error_msg or "exceeded" in error_msg:
                            print(f"[AI] Gemini (old API) quota exceeded: {error_msg}")
                            return None
                        else:
                            print(f"[AI] Gemini (old API) error: {e}")
                            return None
                            
                except ImportError as ie2:
                    print(f"[AI] Gemini import failed: {ie2}")
                    return None
        
        except Exception as e:
            # Catch-all for any other errors
            print(f"[AI] Gemini enhancement failed: {e}")
            return None
    
    def _get_style_description(self, style: str) -> str:
        """Get description for a specific style"""
        descriptions = {
            "cinematic": "dramatic lighting, professional photography, movie-like composition, high detail",
            "artistic": "creative expression, unique style, artistic interpretation, vibrant colors",
            "photorealistic": "realistic details, accurate textures, professional photography, lifelike appearance",
            "realistic": "natural appearance, accurate representation, detailed textures",
            "fantasy": "magical elements, ethereal atmosphere, enchanting details",
            "scifi": "futuristic technology, advanced elements, sleek design",
            "anime": "Japanese animation style, clean lines, vibrant colors, expressive characters"
        }
        return descriptions.get(style, "detailed and high quality")
    
    def clean_prompt(self, prompt: str) -> str:
        """Clean and normalize the prompt"""
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt.strip())
        
        # Remove common negative terms
        negative_terms = ["nsfw", "nude", "naked", "inappropriate"]
        for term in negative_terms:
            prompt = re.sub(rf'\b{term}\b', '', prompt, flags=re.IGNORECASE)
        
        return prompt.strip()
    
    def add_style_enhancement(self, prompt: str, style: str) -> str:
        """Add style-specific enhancements"""
        if style not in self.style_templates:
            style = "cinematic"  # Default style
        
        template = self.style_templates[style]
        enhanced = f"{template['prefix']}{prompt}{template['suffix']}"
        
        return enhanced
    
    def add_detail_enhancement(self, prompt: str, detail_level: str) -> str:
        """Add detail-level specific enhancements"""
        if detail_level not in self.detail_levels:
            detail_level = "medium"  # Default detail level
        
        level_config = self.detail_levels[detail_level]
        enhanced = prompt
        
        # Add enhancement words based on multiplier
        num_enhancements = max(1, int(len(self.enhancement_words) * (level_config['multiplier'] - 1)))
        # Select random words instead of always taking the first ones
        selected_words = random.sample(self.enhancement_words, min(num_enhancements, len(self.enhancement_words)))
        
        if selected_words:
            enhanced += f", {', '.join(selected_words)}"
        
        # Add lighting terms - select randomly
        if level_config['add_lighting']:
            lighting = random.choice(self.lighting_terms)
            enhanced += f", {lighting}"
        
        # Add composition terms - select randomly
        if level_config['add_composition']:
            composition = random.choice(self.composition_terms)
            enhanced += f", {composition}"
        
        # Add technical terms - select randomly
        if level_config['add_technical']:
            technical = random.choice(self.technical_terms)
            enhanced += f", {technical}"
        
        return enhanced
    
    async def enhance_prompt(self, prompt: str, style: str = "cinematic", detail_level: str = "medium", model: str = "auto") -> Dict:
        """Main enhancement function with AI support
        
        Args:
            prompt: The prompt to enhance
            style: The enhancement style
            detail_level: The detail level (low, medium, high)
            model: The AI model to use ("auto", "openai", "anthropic", "gemini", "local", "template")
        """
        # Clean the original prompt
        cleaned_prompt = self.clean_prompt(prompt)
        
        # Try AI enhancement first if available
        ai_enhanced = None
        model_used = None
        fallback_occurred = False
        fallback_reason = None
        
        # Determine if AI should be tried based on model parameter
        try_ai = True
        if model in ("local", "template"):
            try_ai = False
        
        if try_ai and (self.ai_available or model != "auto"):
            try:
                ai_result = await self.enhance_with_ai(cleaned_prompt, style, model)
                if ai_result and isinstance(ai_result, dict):
                    # Extract enhanced prompt and fallback info from dict response
                    ai_enhanced = ai_result.get("enhanced_prompt")
                    fallback_occurred = ai_result.get("fallback_occurred", False)
                    fallback_reason = ai_result.get("fallback_reason")
                    model_used = ai_result.get("model_used")
                    
                    # Determine which model was used for logging
                    if model == "auto":
                        model_used = "auto (best available)"
                    elif fallback_occurred:
                        model_used = f"{model} (fell back to {model_used})"
                    else:
                        model_used = model
                        
                    if fallback_occurred:
                        print(f"[AI] Warning: Fell back to template-based enhancement (reason: {fallback_reason})")
                    print(f"[AI] Successfully enhanced prompt using AI LLM (model: {model_used})")
                elif ai_result:
                    # Legacy string return for backward compatibility
                    ai_enhanced = ai_result
            except Exception as e:
                print(f"[AI] AI enhancement failed: {e}")
        
        # Generate enhancements for all styles
        all_enhancements = {}
        
        for style_name in self.style_templates.keys():
            if style_name == style and ai_enhanced:
                # Use AI-enhanced version for the primary style
                all_enhancements[style_name] = ai_enhanced
            else:
                # Use template-based enhancement for other styles
                style_enhanced = self.add_style_enhancement(cleaned_prompt, style_name)
                detail_enhanced = self.add_detail_enhancement(style_enhanced, detail_level)
                all_enhancements[style_name] = detail_enhanced
        
        # Return the requested style as primary, plus all options
        primary_enhancement = all_enhancements.get(style, all_enhancements["cinematic"])
        
        result = {
            "original_prompt": cleaned_prompt,
            "prompt": primary_enhancement,
            "style": style,
            "detail_level": detail_level,
            "model": model,
            "model_used": model_used,
            "fallback_occurred": fallback_occurred,
            "fallback_reason": fallback_reason,
            "all_enhancements": all_enhancements,
            "ai_enhanced": ai_enhanced is not None,
            "ai_available": self.ai_available,
            "available_models": self.get_available_models()
        }
        
        print(f"[ENHANCE] Returning result with {len(all_enhancements)} enhancements")
        return result
    
    def enhance_prompt_sync(self, prompt: str, style: str = "cinematic", detail_level: str = "medium") -> Dict:
        """Synchronous version of enhance_prompt for compatibility"""
        # Clean the original prompt
        cleaned_prompt = self.clean_prompt(prompt)
        
        # Generate template-based enhancements (no AI in sync version)
        all_enhancements = {}
        
        for style_name in self.style_templates.keys():
            style_enhanced = self.add_style_enhancement(cleaned_prompt, style_name)
            detail_enhanced = self.add_detail_enhancement(style_enhanced, detail_level)
            all_enhancements[style_name] = detail_enhanced
        
        # Return the requested style as primary, plus all options
        primary_enhancement = all_enhancements.get(style, all_enhancements["cinematic"])
        
        return {
            "original_prompt": cleaned_prompt,
            "prompt": primary_enhancement,
            "style": style,
            "detail_level": detail_level,
            "all_enhancements": all_enhancements,
            "ai_enhanced": False,
            "ai_available": self.ai_available
        }
    
    def get_available_styles(self) -> List[str]:
        """Get list of available enhancement styles"""
        return list(self.style_templates.keys())
    
    def get_available_detail_levels(self) -> List[str]:
        """Get list of available detail levels"""
        return list(self.detail_levels.keys())
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """Analyze a prompt for characteristics"""
        cleaned = self.clean_prompt(prompt)
        words = cleaned.split()
        
        analysis = {
            "word_count": len(words),
            "character_count": len(cleaned),
            "has_lighting_terms": any(term.lower() in cleaned.lower() for term in self.lighting_terms),
            "has_composition_terms": any(term.lower() in cleaned.lower() for term in self.composition_terms),
            "has_technical_terms": any(term.lower() in cleaned.lower() for term in self.technical_terms),
            "has_quality_terms": any(term.lower() in cleaned.lower() for term in self.enhancement_words),
            "complexity": "simple" if len(words) < 10 else "medium" if len(words) < 20 else "complex"
        }
        
        return analysis

# Example usage and testing
if __name__ == "__main__":
    enhancer = PromptEnhancer()
    
    # Test enhancement
    test_prompt = "a beautiful sunset over mountains"
    
    async def test():
        result = await enhancer.enhance_prompt(test_prompt, "cinematic", "high")
        
        print("Original:", test_prompt)
        print("Enhanced:", result["prompt"])
        print("AI Enhanced:", result.get("ai_enhanced", False))
        print("AI Available:", result.get("ai_available", False))
        print("\nAll enhancements:")
        for style, enhanced in result["all_enhancements"].items():
            print(f"{style}: {enhanced}")
        
        # Test analysis
        analysis = enhancer.analyze_prompt(test_prompt)
        print(f"\nAnalysis: {analysis}")
    
    asyncio.run(test())
