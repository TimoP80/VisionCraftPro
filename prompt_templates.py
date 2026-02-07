"""
Prompt Templates Library with Auto-completion
Pre-built templates and intelligent prompt completion

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re

class TemplateCategory(Enum):
    """Template categories for organization"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    ABSTRACT = "abstract"
    FANTASY = "fantasy"
    ANIME = "anime"
    ARCHITECTURE = "architecture"
    ANIMALS = "animals"
    FOOD = "food"
    FASHION = "fashion"
    TECHNOLOGY = "technology"
    VEHICLES = "vehicles"
    ARTISTIC = "artistic"
    CINEMATIC = "cinematic"

@dataclass
class PromptTemplate:
    """Data class for prompt templates"""
    name: str
    template: str
    negative_template: str = ""
    category: TemplateCategory = TemplateCategory.ARTISTIC
    tags: List[str] = None
    description: str = ""
    variables: Dict[str, str] = None
    examples: List[str] = None
    rating: float = 0.0
    usage_count: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.variables is None:
            self.variables = {}
        if self.examples is None:
            self.examples = []

class PromptTemplateLibrary:
    """Comprehensive prompt template library with auto-completion"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """Load built-in prompt templates"""
        
        # Portrait Templates
        self.add_template(PromptTemplate(
            name="Professional Portrait",
            template="Professional portrait photography of {subject}, {lighting} lighting, {background} background, {expression} expression, sharp focus, high detail, 8k resolution",
            negative_template="blurry, out of focus, bad lighting, poor composition, amateur, low quality",
            category=TemplateCategory.PORTRAIT,
            tags=["portrait", "photography", "professional", "realistic"],
            description="Professional studio-style portrait with customizable elements",
            variables={
                "subject": "person description (e.g., 'beautiful woman with long hair')",
                "lighting": "lighting style (e.g., 'soft studio', 'dramatic side')",
                "background": "background type (e.g., 'neutral gray', 'nature')",
                "expression": "facial expression (e.g., 'warm smile', 'thoughtful')"
            },
            examples=[
                "Professional portrait photography of a young woman, soft studio lighting, neutral gray background, warm smile expression, sharp focus, high detail, 8k resolution",
                "Professional portrait photography of an elderly man, dramatic side lighting, dark background, thoughtful expression, sharp focus, high detail, 8k resolution"
            ]
        ))
        
        self.add_template(PromptTemplate(
            name="Character Concept Art",
            template="{character_type} character concept art, {style} style, {clothing} clothing, {accessories} accessories, {pose} pose, {background} background, detailed illustration",
            negative_template="photorealistic, photo, realistic, blurry, low quality",
            category=TemplateCategory.PORTRAIT,
            tags=["character", "concept art", "illustration", "fantasy"],
            description="Character design template for concept art",
            variables={
                "character_type": "character type (e.g., 'Fantasy warrior', 'Sci-fi pilot')",
                "style": "art style (e.g., 'anime', 'realistic', 'cartoon')",
                "clothing": "clothing description (e.g., 'ornate armor', 'flight suit')",
                "accessories": "accessories (e.g., 'magic sword', 'tech goggles')",
                "pose": "pose type (e.g., 'dynamic action', 'heroic stance')",
                "background": "background (e.g., 'castle ruins', 'space station')"
            }
        ))
        
        # Landscape Templates
        self.add_template(PromptTemplate(
            name="Epic Landscape",
            template="Epic {landscape_type} landscape, {time_of_day}, {weather} weather, {lighting} lighting, {composition} composition, {detail_level} detail, wide angle view",
            negative_template="urban, city, buildings, man-made, pollution, ugly",
            category=TemplateCategory.LANDSCAPE,
            tags=["landscape", "nature", "epic", "scenic"],
            description="Breathtaking natural landscape photography",
            variables={
                "landscape_type": "landscape type (e.g., 'mountain', 'ocean', 'forest')",
                "time_of_day": "time (e.g., 'golden hour', 'dawn', 'dusk')",
                "weather": "weather conditions (e.g., 'clear skies', 'misty', 'stormy')",
                "lighting": "lighting description (e.g., 'dramatic', 'soft', 'vibrant')",
                "composition": "composition style (e.g., 'leading lines', 'rule of thirds')",
                "detail_level": "detail level (e.g., 'highly detailed', 'minimalist')"
            }
        ))
        
        # Fantasy Templates
        self.add_template(PromptTemplate(
            name="Fantasy Scene",
            template="{fantasy_setting}, {magical_elements}, {characters}, {atmosphere} atmosphere, {art_style} art style, {color_palette} colors, epic fantasy illustration",
            negative_template="modern, contemporary, realistic, photo, mundane",
            category=TemplateCategory.FANTASY,
            tags=["fantasy", "magical", "illustration", "epic"],
            description="Fantasy art scene with magical elements",
            variables={
                "fantasy_setting": "setting (e.g., 'Enchanted forest', 'Dragon\'s lair', 'Wizard tower')",
                "magical_elements": "magic elements (e.g., 'glowing runes', 'floating islands', 'magical creatures')",
                "characters": "characters (e.g., 'brave knights', 'wise wizards', 'mythical beasts')",
                "atmosphere": "atmosphere (e.g., 'mysterious', 'whimsical', 'dark and foreboding')",
                "art_style": "art style (e.g., 'digital painting', 'oil painting', 'watercolor')",
                "color_palette": "colors (e.g., 'vibrant and warm', 'dark and moody', 'pastel and ethereal')"
            }
        ))
        
        # Anime Templates
        self.add_template(PromptTemplate(
            name="Anime Character",
            template="{anime_style} anime character, {character_description}, {clothing_style} clothing, {expression} expression, {background} background, {art_quality} quality, anime illustration",
            negative_template="realistic, photo, 3d, western style, realistic proportions",
            category=TemplateCategory.ANIME,
            tags=["anime", "manga", "character", "japanese"],
            description="Anime-style character illustration",
            variables={
                "anime_style": "anime style (e.g., 'Studio Ghibli', 'Shonen', 'Shojo')",
                "character_description": "character (e.g., 'magical girl with pink hair', 'cool ninja')",
                "clothing_style": "clothing (e.g., 'school uniform', 'fantasy armor', 'casual modern')",
                "expression": "expression (e.g., 'cheerful smile', 'determined look', 'shy blush')",
                "background": "background (e.g., 'cherry blossom garden', 'tokyo street', 'classroom')",
                "art_quality": "quality (e.g., 'high quality', 'detailed line art', 'vibrant colors')"
            }
        ))
        
        # Architecture Templates
        self.add_template(PromptTemplate(
            name="Architectural Photography",
            template="{building_type} architecture, {architectural_style} style, {time_period} period, {photography_style} photography, {lighting_condition} lighting, {composition_angle} angle",
            negative_template="ruined, abandoned, dilapidated, poor condition, ugly",
            category=TemplateCategory.ARCHITECTURE,
            tags=["architecture", "building", "photography", "design"],
            description="Professional architectural photography",
            variables={
                "building_type": "building type (e.g., 'Modern skyscraper', 'Gothic cathedral', 'Traditional house')",
                "architectural_style": "style (e.g., 'Brutalist', 'Art Deco', 'Victorian')",
                "time_period": "period (e.g., 'contemporary', 'historic', 'futuristic')",
                "photography_style": "photo style (e.g., 'professional', 'aerial', 'interior')",
                "lighting_condition": "lighting (e.g., 'golden hour', 'blue hour', 'dramatic shadows')",
                "composition_angle": "angle (e.g., 'low angle shot', 'symmetrical', 'wide angle')"
            }
        ))
        
        # Artistic Templates
        self.add_template(PromptTemplate(
            name="Abstract Art",
            template="{art_movement} abstract art, {color_scheme} colors, {shapes_and_forms}, {texture_style} texture, {composition_style} composition, {medium} medium",
            negative_template="realistic, representational, figurative, photographic",
            category=TemplateCategory.ABSTRACT,
            tags=["abstract", "modern art", "contemporary", "artistic"],
            description="Abstract art in various styles",
            variables={
                "art_movement": "art movement (e.g., 'Cubist', 'Surrealist', 'Expressionist')",
                "color_scheme": "colors (e.g., 'vibrant primary', 'monochromatic', 'pastel')",
                "shapes_and_forms": "shapes (e.g., 'geometric shapes', 'organic forms', 'flowing lines')",
                "texture_style": "texture (e.g., 'smooth', 'rough', 'layered')",
                "composition_style": "composition (e.g., 'balanced', 'dynamic', 'minimalist')",
                "medium": "medium (e.g., 'oil painting', 'digital art', 'watercolor')"
            }
        ))
        
        # Cinematic Templates
        self.add_template(PromptTemplate(
            name="Cinematic Scene",
            template="Cinematic scene from {genre}, {setting_description}, {mood_atmosphere} atmosphere, {camera_shot} shot, {lighting_style} lighting, {color_grading} color grading, movie still",
            negative_template="amateur, home video, low budget, poorly lit, shaky camera",
            category=TemplateCategory.CINEMATIC,
            tags=["cinematic", "movie", "film", "professional"],
            description="Professional movie-style scene",
            variables={
                "genre": "genre (e.g., 'sci-fi thriller', 'fantasy adventure', 'noir mystery')",
                "setting_description": "setting (e.g., 'futuristic city at night', 'medieval battlefield', '1950s diner')",
                "mood_atmosphere": "mood (e.g., 'tense and suspenseful', 'dreamy and ethereal', 'gritty and realistic')",
                "camera_shot": "shot type (e.g., 'wide establishing shot', 'close-up', 'tracking shot')",
                "lighting_style": "lighting (e.g., 'film noir lighting', 'golden hour', 'dramatic backlight')",
                "color_grading": "color grading (e.g., 'teal and orange', 'desaturated', 'vibrant saturated')"
            }
        ))
        
        # Technology Templates
        self.add_template(PromptTemplate(
            name="Tech Concept",
            template="{tech_concept} concept art, {design_style} design, {materials} materials, {environment} environment, {lighting_effects} lighting, futuristic technology illustration",
            negative_template="vintage, retro, outdated, low-tech, primitive",
            category=TemplateCategory.TECHNOLOGY,
            tags=["technology", "futuristic", "concept art", "sci-fi"],
            description="Futuristic technology and concept design",
            variables={
                "tech_concept": "concept (e.g., 'Quantum computer', 'AI interface', 'Spacecraft engine')",
                "design_style": "design style (e.g., 'sleek minimalist', 'industrial', 'organic')",
                "materials": "materials (e.g., 'carbon fiber', 'holographic displays', 'polished metal')",
                "environment": "environment (e.g., 'clean laboratory', 'space station', 'cyberpunk city')",
                "lighting_effects": "lighting (e.g., 'LED glow', 'energy pulses', 'ambient screen light')"
            }
        ))
    
    def add_template(self, template: PromptTemplate):
        """Add a template to the library"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[PromptTemplate]:
        """Get all templates in a category"""
        return [t for t in self.templates.values() if t.category == category]
    
    def search_templates(self, query: str, limit: int = 20) -> List[PromptTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            # Search in name
            if query_lower in template.name.lower():
                results.append(template)
                continue
            
            # Search in description
            if query_lower in template.description.lower():
                results.append(template)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in template.tags):
                results.append(template)
                continue
            
            # Search in template content
            if query_lower in template.template.lower():
                results.append(template)
        
        # Sort by rating and usage count
        results.sort(key=lambda t: (t.rating * 0.7 + t.usage_count * 0.3), reverse=True)
        
        return results[:limit]
    
    def complete_prompt(self, partial_prompt: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Auto-complete partial prompt with templates and suggestions"""
        suggestions = []
        partial_lower = partial_prompt.lower()
        
        # Find matching templates
        for template in self.templates.values():
            # Check if template starts with or contains partial prompt
            template_lower = template.template.lower()
            
            if template_lower.startswith(partial_lower):
                # Calculate completion
                completion = template.template[len(partial_prompt):]
                confidence = 0.9  # High confidence for prefix match
                
                suggestions.append({
                    "type": "template_completion",
                    "template_name": template.name,
                    "completion": completion,
                    "full_prompt": template.template,
                    "negative_prompt": template.negative_template,
                    "confidence": confidence,
                    "category": template.category.value,
                    "description": template.description,
                    "variables": template.variables
                })
            
            elif partial_lower in template_lower and len(suggestions) < limit:
                # Partial match
                completion = template.template
                confidence = 0.6  # Medium confidence for partial match
                
                suggestions.append({
                    "type": "template_suggestion",
                    "template_name": template.name,
                    "completion": completion,
                    "full_prompt": template.template,
                    "negative_prompt": template.negative_template,
                    "confidence": confidence,
                    "category": template.category.value,
                    "description": template.description,
                    "variables": template.variables
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions[:limit]
    
    def fill_template(self, template_name: str, variables: Dict[str, str]) -> Dict[str, str]:
        """Fill a template with provided variables"""
        template = self.get_template(template_name)
        if not template:
            return {"error": f"Template '{template_name}' not found"}
        
        # Fill prompt template
        filled_prompt = template.template
        missing_vars = []
        
        for var_name, var_description in template.variables.items():
            if var_name in variables:
                filled_prompt = filled_prompt.replace(f"{{{var_name}}}", variables[var_name])
            else:
                missing_vars.append(var_name)
                filled_prompt = filled_prompt.replace(f"{{{var_name}}}", f"[{var_name}]")
        
        # Fill negative prompt template
        filled_negative = template.negative_template
        for var_name in template.variables:
            filled_negative = filled_negative.replace(f"{{{var_name}}}", "")
        
        return {
            "prompt": filled_prompt,
            "negative_prompt": filled_negative,
            "missing_variables": missing_vars,
            "template_info": {
                "name": template.name,
                "category": template.category.value,
                "description": template.description,
                "tags": template.tags
            }
        }
    
    def get_variable_suggestions(self, template_name: str, variable_name: str) -> List[str]:
        """Get suggestions for template variables"""
        template = self.get_template(template_name)
        if not template or variable_name not in template.variables:
            return []
        
        # Predefined suggestions based on variable type
        suggestions = {
            "subject": ["beautiful woman", "handsome man", "elderly person", "child", "fantasy character"],
            "lighting": ["soft studio lighting", "dramatic side lighting", "natural daylight", "golden hour", "blue hour"],
            "background": ["neutral gray background", "nature background", "urban city", "minimalist white", "dark background"],
            "expression": ["warm smile", "thoughtful expression", "serious look", "joyful laughter", "pensive mood"],
            "character_type": ["fantasy warrior", "sci-fi pilot", "magical wizard", "stealthy rogue", "noble knight"],
            "style": ["anime style", "realistic style", "cartoon style", "oil painting", "digital art"],
            "landscape_type": ["mountain landscape", "ocean seascape", "forest scene", "desert dunes", "arctic tundra"],
            "time_of_day": ["golden hour", "dawn", "dusk", "midday", "blue hour", "night"],
            "weather": ["clear skies", "misty fog", "stormy clouds", "gentle rain", "snow falling"],
            "anime_style": ["Studio Ghibli style", "Shonen anime", "Shojo manga", "Seinen style", "Chibi cute"],
            "building_type": ["modern skyscraper", "gothic cathedral", "traditional house", "brutalist building", "futuristic structure"],
            "art_movement": ["Cubist style", "Surrealist art", "Impressionist", "Expressionist", "Abstract expressionism"],
            "genre": ["sci-fi thriller", "fantasy adventure", "noir mystery", "horror film", "romantic drama"],
            "tech_concept": ["quantum computer", "AI interface", "spacecraft engine", "cybernetic implant", "holographic display"]
        }
        
        return suggestions.get(variable_name, [])
    
    def get_popular_templates(self, limit: int = 10) -> List[PromptTemplate]:
        """Get most popular templates by usage count and rating"""
        return sorted(
            self.templates.values(),
            key=lambda t: (t.rating * 0.6 + t.usage_count * 0.4),
            reverse=True
        )[:limit]
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about template usage"""
        total_templates = len(self.templates)
        category_counts = {}
        total_usage = sum(t.usage_count for t in self.templates.values())
        avg_rating = sum(t.rating for t in self.templates.values()) / total_templates if total_templates > 0 else 0
        
        for template in self.templates.values():
            category = template.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_templates": total_templates,
            "total_usage": total_usage,
            "average_rating": round(avg_rating, 2),
            "category_distribution": category_counts,
            "most_used": max(self.templates.values(), key=lambda t: t.usage_count) if self.templates else None,
            "highest_rated": max(self.templates.values(), key=lambda t: t.rating) if self.templates else None
        }
    
    def export_templates(self, format: str = "json") -> str:
        """Export all templates"""
        data = []
        
        for template in self.templates.values():
            data.append({
                "name": template.name,
                "template": template.template,
                "negative_template": template.negative_template,
                "category": template.category.value,
                "tags": template.tags,
                "description": template.description,
                "variables": template.variables,
                "examples": template.examples,
                "rating": template.rating,
                "usage_count": template.usage_count
            })
        
        if format.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            # CSV format
            import csv
            import io
            
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return output.getvalue()

# Global instance
template_library = PromptTemplateLibrary()

# Convenience functions
def get_template_library() -> PromptTemplateLibrary:
    """Get the global template library instance"""
    return template_library

def autocomplete_prompt(partial_prompt: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Auto-complete a partial prompt"""
    return template_library.complete_prompt(partial_prompt, limit)

def fill_template(template_name: str, variables: Dict[str, str]) -> Dict[str, str]:
    """Fill a template with variables"""
    return template_library.fill_template(template_name, variables)

def search_templates(query: str, limit: int = 20) -> List[PromptTemplate]:
    """Search for templates"""
    return template_library.search_templates(query, limit)
