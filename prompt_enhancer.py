"""
Prompt Enhancer for VisionCraft Pro
AI-powered prompt enhancement and improvement
"""

import re
import asyncio
from typing import Dict, List, Optional
import json
import os

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
    
    async def enhance_with_ai(self, prompt: str, style: str = "cinematic") -> str:
        """Try to enhance prompt using real AI LLM"""
        if not self.ai_available:
            return None
            
        # Try OpenAI first
        if self.openai_key:
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
        
        # Try Claude
        if self.anthropic_key:
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
        
        # Try Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.5-flash')  # Use model with available quota
                
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
                
                response = await asyncio.to_thread(model.generate_content, prompt_text)
                return response.text.strip()
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                    print(f"[AI] Gemini quota exceeded: {error_msg}")
                    # Don't raise error - let it fall back to template enhancement
                    return None
                else:
                    print(f"[AI] Gemini enhancement failed: {e}")
                    # Note: New google.genai package has different API, keeping old one for now
        
        return None
        
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
        selected_words = self.enhancement_words[:num_enhancements]
        
        if selected_words:
            enhanced += f", {', '.join(selected_words)}"
        
        # Add lighting terms
        if level_config['add_lighting']:
            lighting = self.lighting_terms[0]  # Use first lighting term
            enhanced += f", {lighting}"
        
        # Add composition terms
        if level_config['add_composition']:
            composition = self.composition_terms[0]  # Use first composition term
            enhanced += f", {composition}"
        
        # Add technical terms
        if level_config['add_technical']:
            technical = self.technical_terms[0]  # Use first technical term
            enhanced += f", {technical}"
        
        return enhanced
    
    async def enhance_prompt(self, prompt: str, style: str = "cinematic", detail_level: str = "medium") -> Dict:
        """Main enhancement function with AI support"""
        # Clean the original prompt
        cleaned_prompt = self.clean_prompt(prompt)
        
        # Try AI enhancement first if available
        ai_enhanced = None
        if self.ai_available:
            try:
                ai_enhanced = await self.enhance_with_ai(cleaned_prompt, style)
                if ai_enhanced:
                    print(f"[AI] Successfully enhanced prompt using AI LLM")
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
            "all_enhancements": all_enhancements,
            "ai_enhanced": ai_enhanced is not None,
            "ai_available": self.ai_available
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
