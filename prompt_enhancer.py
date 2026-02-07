"""
Advanced LLM-based Prompt Enhancement System
Inspired by Leonardo.ai for professional prompt engineering
"""

import re
from typing import Dict, List, Optional

class PromptEnhancer:
    """Advanced prompt enhancement using AI-like logic"""
    
    # Enhancement templates for different styles
    ENHANCEMENT_STYLES = {
        "photorealistic": {
            "prefix": "photorealistic, professional photography, ",
            "quality_terms": ["ultra detailed", "sharp focus", "high resolution", "8k", "masterpiece"],
            "lighting": ["cinematic lighting", "dramatic lighting", "soft natural light", "golden hour"],
            "composition": ["rule of thirds", "perfect composition", "artistic composition"],
            "camera": ["shot on Sony A7R IV", "85mm lens", "f/1.4 aperture", "professional camera"],
            "suffix": ", award-winning photography, trending on artstation"
        },
        "artistic": {
            "prefix": "digital art, masterpiece, ",
            "quality_terms": ["highly detailed", "intricate details", "professional digital art"],
            "style": ["trending on artstation", "concept art", "digital painting", "fantasy art"],
            "artist_styles": ["by greg rutkowski", "by artgerm", "by wlop", "by james gurney"],
            "medium": ["digital painting", "concept art", "matte painting", "digital illustration"],
            "suffix": ", award-winning, deviantart, 4k"
        },
        "cinematic": {
            "prefix": "cinematic shot, movie scene, ",
            "quality_terms": ["epic scale", "highly detailed", "movie quality"],
            "cinema_terms": ["widescreen", "cinematic lighting", "film grain", "color graded"],
            "camera_work": ["dolly shot", "crane shot", "tracking shot", "close-up"],
            "atmosphere": ["dramatic atmosphere", "tense mood", "emotional scene"],
            "suffix": ", hollywood blockbuster, oscar nominated cinematography"
        },
        "anime": {
            "prefix": "anime style, japanese animation, ",
            "quality_terms": ["high quality", "detailed", "vibrant colors"],
            "anime_styles": ["makoto shinkai style", "studio ghibli", "kyoani", "madhouse"],
            "character_details": ["detailed eyes", "expressive face", "beautiful character design"],
            "background": ["detailed background", "scenic", "beautiful scenery"],
            "suffix": ", anime screenshot, high quality anime, 1080p"
        }
    }
    
    # Subject-specific enhancements
    SUBJECT_ENHANCEMENTS = {
        "person": {
            "details": ["detailed face", "expressive eyes", "natural pose", "realistic skin texture"],
            "clothing": ["detailed clothing", "fabric texture", "fashionable outfit"],
            "emotion": ["emotional expression", "natural expression", "captivating gaze"]
        },
        "landscape": {
            "details": ["majestic mountains", "serene lake", "dramatic sky", "lush forest"],
            "atmosphere": ["peaceful atmosphere", "serene environment", "natural beauty"],
            "elements": ["intricate details", "textured terrain", "natural elements"]
        },
        "animal": {
            "details": ["detailed fur", "expressive eyes", "natural pose", "realistic texture"],
            "behavior": ["natural behavior", "wild animal", "majestic presence"],
            "habitat": ["natural habitat", "wildlife photography", "nature"]
        },
        "architecture": {
            "details": ["modern design", "intricate details", "structural beauty"],
            "materials": ["textured materials", "realistic surfaces", "architectural details"],
            "style": ["contemporary architecture", "innovative design", "masterpiece"]
        },
        "general": {
            "details": ["highly detailed", "intricate details", "fine details"],
            "quality": ["best quality", "high quality", "professional quality"],
            "style": ["artistic style", "creative design", "beautiful"]
        }
    }
    
    # Quality boosters
    QUALITY_BOOSTERS = [
        "masterpiece", "best quality", "ultra detailed", "high resolution", "8k",
        "sharp focus", "professional", "award winning", "trending", "perfect"
    ]
    
    @classmethod
    def enhance_prompt(cls, prompt: str, style: str = "photorealistic", detail_level: str = "medium") -> str:
        """
        Enhance prompt with AI-like intelligence
        
        Args:
            prompt: Original prompt
            style: Enhancement style (photorealistic, artistic, cinematic, anime)
            detail_level: Amount of detail to add (low, medium, high)
        """
        if not prompt or len(prompt.strip()) < 3:
            return prompt
        
        # Detect subject type
        subject_type = cls._detect_subject_type(prompt)
        
        # Get enhancement template
        template = cls.ENHANCEMENT_STYLES.get(style, cls.ENHANCEMENT_STYLES["photorealistic"])
        
        # Build enhanced prompt
        enhanced_parts = []
        
        # Add prefix
        enhanced_parts.append(template["prefix"])
        
        # Add quality terms based on detail level
        quality_count = {"low": 2, "medium": 4, "high": 6}[detail_level]
        quality_terms = template["quality_terms"][:quality_count]
        enhanced_parts.extend(quality_terms)
        
        # Add subject-specific enhancements
        if subject_type in cls.SUBJECT_ENHANCEMENTS:
            subject_enhancements = cls.SUBJECT_ENHANCEMENTS[subject_type]
            detail_count = {"low": 1, "medium": 2, "high": 3}[detail_level]
            # Safely get details with fallback
            details = subject_enhancements.get("details", [])
            enhanced_parts.extend(details[:detail_count])
        
        # Add style-specific elements
        if "lighting" in template and detail_level != "low":
            enhanced_parts.append(template["lighting"][0])
        
        if "composition" in template and detail_level == "high":
            enhanced_parts.append(template["composition"][0])
        
        # Add camera/technical details for high detail
        if detail_level == "high" and "camera" in template:
            enhanced_parts.append(template["camera"][0])
        
        # Add original prompt (cleaned)
        cleaned_prompt = cls._clean_prompt(prompt)
        enhanced_parts.append(cleaned_prompt)
        
        # Add additional style elements
        if detail_level == "high":
            if "style" in template:
                enhanced_parts.extend(template["style"][:2])
            if "artist_styles" in template:
                enhanced_parts.append(template["artist_styles"][0])
        
        # Add suffix
        enhanced_parts.append(template["suffix"])
        
        # Combine and clean
        enhanced_prompt = ", ".join(filter(None, enhanced_parts))
        
        # Final cleanup
        enhanced_prompt = cls._final_cleanup(enhanced_prompt)
        
        return enhanced_prompt
    
    @classmethod
    def _detect_subject_type(cls, prompt: str) -> str:
        """Detect the main subject type of the prompt"""
        prompt_lower = prompt.lower()
        
        # Check for people/portraits
        if any(word in prompt_lower for word in ["person", "woman", "man", "girl", "boy", "portrait", "face"]):
            return "person"
        
        # Check for landscapes
        if any(word in prompt_lower for word in ["landscape", "mountain", "forest", "lake", "ocean", "sky", "nature"]):
            return "landscape"
        
        # Check for animals
        if any(word in prompt_lower for word in ["animal", "dog", "cat", "bird", "horse", "wildlife"]):
            return "animal"
        
        # Check for architecture
        if any(word in prompt_lower for word in ["building", "house", "architecture", "city", "structure"]):
            return "architecture"
        
        return "general"
    
    @classmethod
    def _clean_prompt(cls, prompt: str) -> str:
        """Clean the original prompt"""
        # Remove existing quality terms to avoid duplication
        quality_terms = ["high quality", "detailed", "realistic", "photorealistic", "8k", "4k"]
        cleaned = prompt.lower()
        
        for term in quality_terms:
            cleaned = cleaned.replace(term, "")
        
        # Remove extra commas and spaces
        cleaned = re.sub(r',\s*,', ',', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    @classmethod
    def _final_cleanup(cls, prompt: str) -> str:
        """Final cleanup of the enhanced prompt"""
        # Remove duplicate commas
        prompt = re.sub(r',\s*,', ',', prompt)
        
        # Remove duplicate words (case insensitive)
        words = prompt.lower().split(', ')
        seen = set()
        unique_words = []
        
        for word in words:
            word_clean = word.strip()
            if word_clean not in seen and word_clean:
                seen.add(word_clean)
                unique_words.append(word_clean)
        
        # Rebuild with proper capitalization
        result = ", ".join(unique_words)
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
        
        return result
    
    @classmethod
    def get_enhancement_options(cls) -> Dict[str, str]:
        """Get available enhancement styles and their descriptions"""
        return {
            "photorealistic": "Professional photography with realistic details and lighting",
            "artistic": "Digital art style with creative and artistic elements",
            "cinematic": "Movie-like scenes with dramatic lighting and composition",
            "anime": "Japanese animation style with vibrant colors and detailed characters"
        }
    
    @classmethod
    def create_multiple_enhancements(cls, prompt: str) -> Dict[str, str]:
        """Create multiple enhanced versions of the same prompt"""
        enhancements = {}
        
        for style in cls.ENHANCEMENT_STYLES.keys():
            enhancements[style] = cls.enhance_prompt(prompt, style, "medium")
        
        return enhancements
