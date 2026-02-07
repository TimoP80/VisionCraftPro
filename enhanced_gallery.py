"""
Enhanced Image Gallery with Tagging and Categorization
Advanced gallery management for VisionCraft Pro

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import hashlib
from pathlib import Path

class EnhancedImageGallery:
    """Enhanced gallery with tagging, categorization, and search capabilities"""
    
    def __init__(self, gallery_dir: str = "generated_images"):
        self.gallery_dir = Path(gallery_dir)
        self.images_dir = self.gallery_dir / "images"
        self.db_path = self.gallery_dir / "gallery.db"
        self.thumbnails_dir = self.gallery_dir / "thumbnails"
        
        # Ensure directories exist
        self.gallery_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.thumbnails_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Predefined categories and tags
        self.categories = {
            "portrait": "Portrait Photography",
            "landscape": "Landscape & Nature", 
            "abstract": "Abstract Art",
            "fantasy": "Fantasy & Sci-Fi",
            "anime": "Anime & Cartoon",
            "architecture": "Architecture",
            "animals": "Animals & Wildlife",
            "food": "Food & Culinary",
            "fashion": "Fashion & Style",
            "technology": "Technology",
            "vehicles": "Vehicles & Transport",
            "other": "Other"
        }
        
        self.predefined_tags = {
            "style": ["photorealistic", "artistic", "cinematic", "cartoon", "anime", "3d-render", "oil-painting", "watercolor", "sketch"],
            "quality": ["high-quality", "detailed", "sharp", "blurry", "low-quality", "masterpiece"],
            "color": ["vibrant", "monochrome", "pastel", "dark", "bright", "warm-colors", "cool-colors"],
            "composition": ["close-up", "wide-angle", "macro", "portrait", "landscape", "action-shot"],
            "mood": ["happy", "sad", "dramatic", "peaceful", "mysterious", "energetic", "romantic"],
            "setting": ["indoor", "outdoor", "urban", "nature", "space", "underwater", "fantasy-world"],
            "technical": ["sdxl", "sd15", "leonardo-ai", "turbo", "high-resolution", "low-resolution"]
        }
    
    def _init_database(self):
        """Initialize SQLite database for gallery metadata"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                filepath TEXT NOT NULL,
                thumbnail_path TEXT,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                format TEXT,
                hash TEXT,
                prompt TEXT,
                negative_prompt TEXT,
                model_used TEXT,
                generation_params TEXT,
                category TEXT,
                tags TEXT,
                rating INTEGER DEFAULT 0,
                favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                image_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create image_tags junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_tags (
                image_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (image_id, tag_id),
                FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')
        
        # Insert predefined categories
        for cat_id, cat_name in self.categories.items():
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)
            ''', (cat_id, cat_name))
        
        # Insert predefined tags
        for tag_type, tags in self.predefined_tags.items():
            for tag in tags:
                cursor.execute('''
                    INSERT OR IGNORE INTO tags (name, type) VALUES (?, ?)
                ''', (tag, tag_type))
        
        conn.commit()
        conn.close()
    
    def add_image(self, image_path: str, prompt: str = "", negative_prompt: str = "", 
                  model_used: str = "", generation_params: Dict = None, 
                  category: str = "other", tags: List[str] = None) -> int:
        """Add an image to the gallery with metadata"""
        try:
            image_path = Path(image_path)
            
            # Generate image hash
            image_hash = self._generate_image_hash(image_path)
            
            # Get image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
                image_format = img.format
            
            # Create thumbnail
            thumbnail_path = self._create_thumbnail(image_path)
            
            # Get file size
            file_size = image_path.stat().st_size
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Insert image record
            cursor.execute('''
                INSERT OR REPLACE INTO images 
                (filename, filepath, thumbnail_path, file_size, width, height, format, hash,
                 prompt, negative_prompt, model_used, generation_params, category, favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_path.name,
                str(image_path),
                str(thumbnail_path) if thumbnail_path else None,
                file_size,
                width,
                height,
                image_format,
                image_hash,
                prompt,
                negative_prompt,
                model_used,
                json.dumps(generation_params) if generation_params else None,
                category,
                False
            ))
            
            image_id = cursor.lastrowid
            
            # Add tags
            if tags:
                self._add_image_tags(cursor, image_id, tags)
            
            # Update category count
            cursor.execute('''
                UPDATE categories SET image_count = image_count + 1 WHERE name = ?
            ''', (category,))
            
            conn.commit()
            conn.close()
            
            print(f"[Gallery] Added image: {image_path.name} (ID: {image_id})")
            return image_id
            
        except Exception as e:
            print(f"[Gallery] Error adding image: {e}")
            return -1
    
    def _generate_image_hash(self, image_path: Path) -> str:
        """Generate unique hash for image"""
        try:
            with Image.open(image_path) as img:
                # Use a small resized version for hashing
                img_resized = img.resize((8, 8))
                img_bytes = img_resized.tobytes()
                return hashlib.md5(img_bytes).hexdigest()
        except:
            # Fallback to file hash
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
    
    def _create_thumbnail(self, image_path: Path, size: Tuple[int, int] = (200, 200)) -> Optional[Path]:
        """Create thumbnail for image"""
        try:
            thumbnail_path = self.thumbnails_dir / f"thumb_{image_path.stem}.jpg"
            
            if not thumbnail_path.exists():
                with Image.open(image_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Create thumbnail
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, 'JPEG', quality=85)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"[Gallery] Error creating thumbnail: {e}")
            return None
    
    def _add_image_tags(self, cursor, image_id: int, tags: List[str]):
        """Add tags to an image"""
        for tag in tags:
            tag = tag.lower().strip()
            if not tag:
                continue
                
            # Insert tag if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO tags (name) VALUES (?)
            ''', (tag,))
            
            # Get tag ID
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]
            
            # Link image and tag
            cursor.execute('''
                INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)
            ''', (image_id, tag_id))
            
            # Update tag usage count
            cursor.execute('''
                UPDATE tags SET usage_count = usage_count + 1 WHERE id = ?
            ''', (tag_id,))
    
    def get_images(self, category: str = None, tags: List[str] = None, 
                   favorite_only: bool = False, search_term: str = None,
                   sort_by: str = "created_at", order: str = "DESC",
                   limit: int = None, offset: int = 0) -> List[Dict]:
        """Get images with filtering and sorting"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query
        query = '''
            SELECT i.*, 
                   GROUP_CONCAT(t.name, ',') as tags,
                   c.description as category_description
            FROM images i
            LEFT JOIN image_tags it ON i.id = it.image_id
            LEFT JOIN tags t ON it.tag_id = t.id
            LEFT JOIN categories c ON i.category = c.name
        '''
        
        conditions = []
        params = []
        
        if category:
            conditions.append("i.category = ?")
            params.append(category)
        
        if favorite_only:
            conditions.append("i.favorite = 1")
        
        if search_term:
            conditions.append("(i.prompt LIKE ? OR i.filename LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("EXISTS (SELECT 1 FROM image_tags it2 JOIN tags t2 ON it2.tag_id = t2.id WHERE it2.image_id = i.id AND t2.name = ?)")
                params.append(tag.lower())
            conditions.append(f"({' AND '.join(tag_conditions)})")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" GROUP BY i.id ORDER BY i.{sort_by} {order}"
        
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        images = []
        
        for row in cursor.fetchall():
            image_dict = dict(row)
            if image_dict['tags']:
                image_dict['tags'] = image_dict['tags'].split(',')
            else:
                image_dict['tags'] = []
            
            if image_dict['generation_params']:
                image_dict['generation_params'] = json.loads(image_dict['generation_params'])
            else:
                image_dict['generation_params'] = {}
            
            images.append(image_dict)
        
        conn.close()
        return images
    
    def get_categories(self) -> List[Dict]:
        """Get all categories with image counts"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, COUNT(i.id) as actual_count
            FROM categories c
            LEFT JOIN images i ON c.name = i.category
            GROUP BY c.id
            ORDER BY actual_count DESC
        ''')
        
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_tags(self, tag_type: str = None, limit: int = 50) -> List[Dict]:
        """Get popular tags"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT t.*, COUNT(it.image_id) as image_count
            FROM tags t
            LEFT JOIN image_tags it ON t.id = it.tag_id
        '''
        
        params = []
        if tag_type:
            query += " WHERE t.type = ?"
            params.append(tag_type)
        
        query += " GROUP BY t.id ORDER BY image_count DESC, usage_count DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        tags = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tags
    
    def update_image_tags(self, image_id: int, tags: List[str]) -> bool:
        """Update tags for an image"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Remove existing tags
            cursor.execute('DELETE FROM image_tags WHERE image_id = ?', (image_id,))
            
            # Add new tags
            self._add_image_tags(cursor, image_id, tags)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Gallery] Error updating tags: {e}")
            return False
    
    def update_image_category(self, image_id: int, category: str) -> bool:
        """Update image category"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get old category
            cursor.execute('SELECT category FROM images WHERE id = ?', (image_id,))
            old_category = cursor.fetchone()
            
            if old_category:
                old_category = old_category[0]
                
                # Update image category
                cursor.execute('UPDATE images SET category = ? WHERE id = ?', (category, image_id))
                
                # Update category counts
                cursor.execute('UPDATE categories SET image_count = image_count - 1 WHERE name = ?', (old_category,))
                cursor.execute('UPDATE categories SET image_count = image_count + 1 WHERE name = ?', (category,))
                
                conn.commit()
                conn.close()
                return True
            
        except Exception as e:
            print(f"[Gallery] Error updating category: {e}")
            return False
    
    def toggle_favorite(self, image_id: int) -> bool:
        """Toggle favorite status of an image"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('UPDATE images SET favorite = NOT favorite WHERE id = ?', (image_id,))
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Gallery] Error toggling favorite: {e}")
            return False
    
    def rate_image(self, image_id: int, rating: int) -> bool:
        """Rate an image (1-5 stars)"""
        try:
            if not 1 <= rating <= 5:
                return False
                
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('UPDATE images SET rating = ? WHERE id = ?', (rating, image_id))
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Gallery] Error rating image: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get gallery statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        
        # Total images
        cursor.execute('SELECT COUNT(*) FROM images')
        stats['total_images'] = cursor.fetchone()[0]
        
        # Total favorites
        cursor.execute('SELECT COUNT(*) FROM images WHERE favorite = 1')
        stats['total_favorites'] = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute('SELECT AVG(rating) FROM images WHERE rating > 0')
        avg_rating = cursor.fetchone()[0]
        stats['average_rating'] = round(avg_rating, 2) if avg_rating else 0
        
        # Most used tags
        cursor.execute('''
            SELECT t.name, COUNT(it.image_id) as count
            FROM tags t
            JOIN image_tags it ON t.id = it.tag_id
            GROUP BY t.id
            ORDER BY count DESC
            LIMIT 10
        ''')
        stats['popular_tags'] = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Category distribution
        cursor.execute('''
            SELECT c.name, c.description, COUNT(i.id) as count
            FROM categories c
            LEFT JOIN images i ON c.name = i.category
            GROUP BY c.id
            ORDER BY count DESC
        ''')
        stats['category_distribution'] = [
            {'name': row[0], 'description': row[1], 'count': row[2]} 
            for row in cursor.fetchall()
        ]
        
        # Storage usage
        cursor.execute('SELECT SUM(file_size) FROM images')
        total_size = cursor.fetchone()[0] or 0
        stats['total_storage_mb'] = round(total_size / (1024 * 1024), 2)
        
        conn.close()
        return stats
    
    def search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions for autocomplete"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        suggestions = []
        
        # Search in prompts
        cursor.execute('''
            SELECT DISTINCT prompt FROM images 
            WHERE prompt LIKE ? LIMIT ?
        ''', (f"%{query}%", limit))
        
        for row in cursor.fetchall():
            suggestions.append(row[0])
        
        # Search in tags
        cursor.execute('''
            SELECT DISTINCT name FROM tags 
            WHERE name LIKE ? LIMIT ?
        ''', (f"%{query}%", limit))
        
        for row in cursor.fetchall():
            suggestions.append(row[0])
        
        conn.close()
        return suggestions[:limit]
    
    def export_metadata(self, format: str = "json") -> str:
        """Export all gallery metadata"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM images')
        images = []
        
        for row in cursor.fetchall():
            image_dict = dict(row)
            if image_dict['generation_params']:
                image_dict['generation_params'] = json.loads(image_dict['generation_params'])
            images.append(image_dict)
        
        conn.close()
        
        if format.lower() == "json":
            return json.dumps(images, indent=2, default=str)
        else:
            # CSV format
            import csv
            import io
            
            output = io.StringIO()
            if images:
                writer = csv.DictWriter(output, fieldnames=images[0].keys())
                writer.writeheader()
                writer.writerows(images)
            
            return output.getvalue()

# Convenience functions for integration
def create_enhanced_gallery(gallery_dir: str = "generated_images") -> EnhancedImageGallery:
    """Create an enhanced gallery instance"""
    return EnhancedImageGallery(gallery_dir)

def get_gallery_stats(gallery_dir: str = "generated_images") -> Dict:
    """Get quick gallery statistics"""
    gallery = EnhancedImageGallery(gallery_dir)
    return gallery.get_statistics()
