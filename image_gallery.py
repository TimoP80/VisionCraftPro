"""
Image Gallery System for Persistent Storage
Handles saving, loading, and managing generated images
Enhanced with tagging and categorization support
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from PIL import Image
import io
from enhanced_gallery import EnhancedImageGallery

class ImageGallery:
    """Manages persistent storage of generated images"""
    
    def __init__(self, gallery_dir: str = "generated_images"):
        self.gallery_dir = gallery_dir
        self.metadata_file = os.path.join(gallery_dir, "metadata.json")
        self.images_dir = os.path.join(gallery_dir, "images")
        
        # Create directories if they don't exist
        os.makedirs(self.gallery_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Load existing metadata
        self.metadata = self._load_metadata()
        
        # Initialize enhanced gallery
        self.enhanced_gallery = EnhancedImageGallery(gallery_dir)
    
    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Load metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                return []
        return []
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def add_image(self, image_data: str, prompt: str, model: str, 
                  generation_time: float, vram_used: float, 
                  steps: int, guidance: float, resolution: tuple,
                  negative_prompt: str = "", category: str = "other", 
                  tags: List[str] = None) -> str:
        """Add a new image to the gallery with enhanced metadata"""
        
        # Generate unique ID
        image_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.metadata)}"
        
        # Save image file
        image_bytes = base64.b64decode(image_data)
        image_path = os.path.join(self.images_dir, f"{image_id}.png")
        
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Create metadata entry
        metadata_entry = {
            "id": image_id,
            "filename": f"{image_id}.png",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "model": model,
            "generation_time": generation_time,
            "vram_used": vram_used,
            "steps": steps,
            "guidance": guidance,
            "resolution": resolution,
            "timestamp": datetime.now().isoformat(),
            "size": len(image_bytes),
            "category": category,
            "tags": tags or []
        }
        
        # Add to enhanced gallery
        generation_params = {
            "generation_time": generation_time,
            "vram_used": vram_used,
            "steps": steps,
            "guidance": guidance,
            "resolution": resolution
        }
        
        try:
            self.enhanced_gallery.add_image(
                image_path=image_path,
                prompt=prompt,
                negative_prompt=negative_prompt,
                model_used=model,
                generation_params=generation_params,
                category=category,
                tags=tags or []
            )
        except Exception as e:
            print(f"[Gallery] Enhanced gallery error: {e}")
        
        # Add to metadata (newest first)
        self.metadata.insert(0, metadata_entry)
        
        # Keep only last 100 images to prevent storage bloat
        if len(self.metadata) > 100:
            # Remove oldest image file
            oldest = self.metadata.pop()
            oldest_path = os.path.join(self.images_dir, oldest["filename"])
            if os.path.exists(oldest_path):
                os.remove(oldest_path)
        
        # Save metadata
        self._save_metadata()
        
        return image_id
    
    def get_image_data(self, image_id: str) -> str:
        """Get image data as base64 string"""
        for entry in self.metadata:
            if entry["id"] == image_id:
                image_path = os.path.join(self.images_dir, entry["filename"])
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        image_bytes = f.read()
                    return base64.b64encode(image_bytes).decode()
        return None
    
    def get_recent_images(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent images with metadata"""
        return self.metadata[:limit]
    
    def get_image_by_id(self, image_id: str) -> Dict[str, Any]:
        """Get specific image metadata by ID"""
        for entry in self.metadata:
            if entry["id"] == image_id:
                return entry
        return None
    
    def search_images(self, query: str = "", model: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Search images by prompt or model"""
        results = []
        query_lower = query.lower()
        
        for entry in self.metadata:
            # Filter by query
            if query and query_lower not in entry["prompt"].lower():
                continue
            
            # Filter by model
            if model and model != entry["model"]:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gallery statistics"""
        total_images = len(self.metadata)
        if total_images == 0:
            return {
                "total_images": 0,
                "total_size_mb": 0,
                "models_used": [],
                "avg_generation_time": 0,
                "oldest_image": None,
                "newest_image": None
            }
        
        # Calculate stats
        total_size = sum(entry["size"] for entry in self.metadata)
        models_used = list(set(entry["model"] for entry in self.metadata))
        avg_time = sum(entry["generation_time"] for entry in self.metadata) / total_images
        
        return {
            "total_images": total_images,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "models_used": models_used,
            "avg_generation_time": round(avg_time, 2),
            "oldest_image": self.metadata[-1]["timestamp"] if self.metadata else None,
            "newest_image": self.metadata[0]["timestamp"] if self.metadata else None
        }
    
    def delete_image(self, image_id: str) -> bool:
        """Delete an image from the gallery"""
        for i, entry in enumerate(self.metadata):
            if entry["id"] == image_id:
                # Remove file
                image_path = os.path.join(self.images_dir, entry["filename"])
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # Remove from metadata
                self.metadata.pop(i)
                self._save_metadata()
                return True
        return False
    
    def clear_gallery(self):
        """Clear all images from gallery"""
        # Remove all image files
        for entry in self.metadata:
            image_path = os.path.join(self.images_dir, entry["filename"])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Clear metadata
        self.metadata = []
        self._save_metadata()
    
    # Enhanced Gallery Methods
    
    def get_enhanced_images(self, category: str = None, tags: List[str] = None, 
                           favorite_only: bool = False, search_term: str = None,
                           sort_by: str = "created_at", order: str = "DESC",
                           limit: int = None, offset: int = 0) -> List[Dict]:
        """Get images with enhanced filtering and sorting"""
        return self.enhanced_gallery.get_images(
            category=category, tags=tags, favorite_only=favorite_only,
            search_term=search_term, sort_by=sort_by, order=order,
            limit=limit, offset=offset
        )
    
    def get_categories(self) -> List[Dict]:
        """Get all categories with image counts"""
        return self.enhanced_gallery.get_categories()
    
    def get_tags(self, tag_type: str = None, limit: int = 50) -> List[Dict]:
        """Get popular tags"""
        return self.enhanced_gallery.get_tags(tag_type=tag_type, limit=limit)
    
    def update_image_tags(self, image_id: str, tags: List[str]) -> bool:
        """Update tags for an image"""
        # Find the image in enhanced gallery
        images = self.enhanced_gallery.get_images(search_term=image_id)
        if images:
            return self.enhanced_gallery.update_image_tags(images[0]['id'], tags)
        return False
    
    def update_image_category(self, image_id: str, category: str) -> bool:
        """Update image category"""
        # Find the image in enhanced gallery
        images = self.enhanced_gallery.get_images(search_term=image_id)
        if images:
            return self.enhanced_gallery.update_image_category(images[0]['id'], category)
        return False
    
    def toggle_favorite(self, image_id: str) -> bool:
        """Toggle favorite status of an image"""
        # Find the image in enhanced gallery
        images = self.enhanced_gallery.get_images(search_term=image_id)
        if images:
            return self.enhanced_gallery.toggle_favorite(images[0]['id'])
        return False
    
    def rate_image(self, image_id: str, rating: int) -> bool:
        """Rate an image (1-5 stars)"""
        # Find the image in enhanced gallery
        images = self.enhanced_gallery.get_images(search_term=image_id)
        if images:
            return self.enhanced_gallery.rate_image(images[0]['id'], rating)
        return False
    
    def get_enhanced_stats(self) -> Dict:
        """Get enhanced gallery statistics"""
        return self.enhanced_gallery.get_statistics()
    
    def search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions for autocomplete"""
        return self.enhanced_gallery.search_suggestions(query, limit)
    
    def export_metadata(self, format: str = "json") -> str:
        """Export all gallery metadata"""
        return self.enhanced_gallery.export_metadata(format)
    
    def auto_categorize_image(self, prompt: str, tags: List[str] = None) -> str:
        """Automatically categorize an image based on prompt and tags"""
        prompt_lower = prompt.lower()
        tags_lower = [tag.lower() for tag in tags] if tags else []
        
        # Category keywords
        category_keywords = {
            "portrait": ["portrait", "face", "person", "woman", "man", "people", "headshot"],
            "landscape": ["landscape", "nature", "mountain", "forest", "ocean", "sky", "sunset", "sunrise"],
            "abstract": ["abstract", "geometric", "pattern", "shapes", "colors", "artistic"],
            "fantasy": ["fantasy", "dragon", "magic", "wizard", "fairy", "mythical", "sword"],
            "anime": ["anime", "manga", "cartoon", "character", "studio ghibli"],
            "architecture": ["building", "architecture", "house", "city", "street", "bridge"],
            "animals": ["animal", "dog", "cat", "bird", "horse", "wildlife", "pet"],
            "food": ["food", "pizza", "burger", "cake", "coffee", "meal", "cooking"],
            "fashion": ["fashion", "clothing", "dress", "outfit", "style", "model"],
            "technology": ["technology", "computer", "robot", "futuristic", "tech", "digital"],
            "vehicles": ["car", "truck", "plane", "boat", "vehicle", "motorcycle"]
        }
        
        # Check prompt and tags for category matches
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower or keyword in tags_lower:
                    return category
        
        return "other"
    
    def extract_tags_from_prompt(self, prompt: str) -> List[str]:
        """Extract relevant tags from prompt"""
        prompt_lower = prompt.lower()
        extracted_tags = []
        
        # Style tags
        style_keywords = {
            "photorealistic": ["photorealistic", "realistic", "photo", "photography"],
            "artistic": ["artistic", "art", "painting", "creative"],
            "cinematic": ["cinematic", "movie", "film", "dramatic"],
            "cartoon": ["cartoon", "animated", "toon"],
            "anime": ["anime", "manga", "japanese"],
            "3d-render": ["3d", "render", "cgi", "computer graphics"],
            "oil-painting": ["oil painting", "oil", "canvas"],
            "watercolor": ["watercolor", "water", "paint"]
        }
        
        # Quality tags
        quality_keywords = {
            "high-quality": ["high quality", "detailed", "sharp", "masterpiece"],
            "detailed": ["detailed", "intricate", "fine details"],
            "vibrant": ["vibrant", "colorful", "bright colors"]
        }
        
        # Combine all keywords
        all_keywords = {**style_keywords, **quality_keywords}
        
        for tag, keywords in all_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    extracted_tags.append(tag)
                    break
        
        return list(set(extracted_tags))  # Remove duplicates
