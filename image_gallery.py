"""
Image Gallery System for Persistent Storage
Handles saving, loading, and managing generated images
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any
from PIL import Image
import io

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
                  steps: int, guidance: float, resolution: tuple) -> str:
        """Add a new image to the gallery"""
        
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
            "model": model,
            "generation_time": generation_time,
            "vram_used": vram_used,
            "steps": steps,
            "guidance": guidance,
            "resolution": resolution,
            "timestamp": datetime.now().isoformat(),
            "size": len(image_bytes)
        }
        
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
