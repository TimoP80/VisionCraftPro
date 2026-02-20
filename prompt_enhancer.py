"""
Prompt Enhancer for VisionCraft Pro
AI-powered prompt enhancement and improvement
"""

import re
from typing import Dict, List, Optional
import json

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
            "fantasy": {
                "prefix": "fantasy art, magical, ethereal, ",
                "suffix": ", enchanting, mystical, detailed fantasy elements",
                "quality_terms": ["magical", "ethereal", "fantasy", "enchanting"]
            },
            "scifi": {
                "prefix": "sci-fi, futuristic, high-tech, ",
                "suffix": ", advanced technology, sleek design, detailed sci-fi elements",
                "quality_terms": ["futuristic", "high-tech", "advanced", "sleek"]
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
    
    def enhance_prompt(self, prompt: str, style: str = "cinematic", detail_level: str = "medium") -> Dict:
        """Main enhancement function"""
        # Clean the original prompt
        cleaned_prompt = self.clean_prompt(prompt)
        
        # Generate enhancements for all styles
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
            "all_enhancements": all_enhancements
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
    result = enhancer.enhance_prompt(test_prompt, "cinematic", "high")
    
    print("Original:", test_prompt)
    print("Enhanced:", result["prompt"])
    print("\nAll enhancements:")
    for style, enhanced in result["all_enhancements"].items():
        print(f"{style}: {enhanced}")
    
    # Test analysis
    analysis = enhancer.analyze_prompt(test_prompt)
    print(f"\nAnalysis: {analysis}")
