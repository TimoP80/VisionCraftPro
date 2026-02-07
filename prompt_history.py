"""
Prompt History and Favorites Management System
Tracks, organizes, and suggests prompts for VisionCraft Pro

Author: Timo Pitkänen (tpitkane@gmail.com)
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib

class PromptHistoryManager:
    """Manages prompt history, favorites, and intelligent suggestions"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "prompts.db"
        
        # Initialize database
        self._init_database()
        
        # Prompt categories for organization
        self.prompt_categories = {
            "portrait": "Portrait & Character",
            "landscape": "Landscape & Nature",
            "abstract": "Abstract & Artistic",
            "fantasy": "Fantasy & Sci-Fi",
            "anime": "Anime & Cartoon",
            "architecture": "Architecture & Buildings",
            "animals": "Animals & Wildlife",
            "food": "Food & Culinary",
            "fashion": "Fashion & Style",
            "technology": "Technology & Digital",
            "vehicles": "Vehicles & Transport",
            "other": "Other & Miscellaneous"
        }
    
    def _init_database(self):
        """Initialize SQLite database for prompt management"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create prompts history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                negative_prompt TEXT,
                hash TEXT UNIQUE,
                category TEXT,
                tags TEXT,
                model_used TEXT,
                generation_params TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_generation_time REAL DEFAULT 0,
                rating_sum INTEGER DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                negative_prompt TEXT,
                hash TEXT UNIQUE,
                category TEXT,
                tags TEXT,
                notes TEXT,
                rating INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create prompt templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                template TEXT NOT NULL,
                negative_template TEXT,
                category TEXT,
                tags TEXT,
                description TEXT,
                usage_count INTEGER DEFAULT 0,
                rating_sum INTEGER DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                is_public BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create prompt suggestions table (for ML-based recommendations)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_prompt TEXT NOT NULL,
                suggested_prompt TEXT NOT NULL,
                similarity_score REAL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _generate_prompt_hash(self, prompt: str, negative_prompt: str = "") -> str:
        """Generate unique hash for prompt combination"""
        combined = f"{prompt}|||{negative_prompt}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def add_prompt_to_history(self, prompt: str, negative_prompt: str = "", 
                             model_used: str = "", generation_params: Dict = None,
                             category: str = None, tags: List[str] = None,
                             success: bool = True, generation_time: float = 0) -> int:
        """Add a prompt to history with usage statistics"""
        try:
            prompt_hash = self._generate_prompt_hash(prompt, negative_prompt)
            
            # Auto-categorize if not provided
            if not category:
                category = self._auto_categorize_prompt(prompt)
            
            # Extract tags if not provided
            if not tags:
                tags = self._extract_tags_from_prompt(prompt)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if prompt already exists
            cursor.execute('SELECT id, success_count, failure_count, avg_generation_time FROM prompt_history WHERE hash = ?', (prompt_hash,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing prompt
                prompt_id, success_count, failure_count, avg_time = existing
                
                # Update statistics
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                
                # Update average generation time
                if generation_time > 0:
                    total_time = avg_time * (success_count + failure_count - 1) + generation_time
                    avg_time = total_time / (success_count + failure_count)
                
                cursor.execute('''
                    UPDATE prompt_history 
                    SET success_count = ?, failure_count = ?, avg_generation_time = ?, 
                        last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (success_count, failure_count, avg_time, prompt_id))
                
            else:
                # Insert new prompt
                cursor.execute('''
                    INSERT INTO prompt_history 
                    (prompt, negative_prompt, hash, category, tags, model_used, 
                     generation_params, success_count, failure_count, avg_generation_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prompt, negative_prompt, prompt_hash, category, 
                    json.dumps(tags) if tags else None, model_used,
                    json.dumps(generation_params) if generation_params else None,
                    1 if success else 0, 0 if success else 1, generation_time
                ))
                
                prompt_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return prompt_id
            
        except Exception as e:
            print(f"[PromptHistory] Error adding to history: {e}")
            return -1
    
    def add_to_favorites(self, prompt: str, negative_prompt: str = "", 
                        category: str = None, tags: List[str] = None, 
                        notes: str = "", rating: int = 0) -> int:
        """Add a prompt to favorites"""
        try:
            prompt_hash = self._generate_prompt_hash(prompt, negative_prompt)
            
            if not category:
                category = self._auto_categorize_prompt(prompt)
            
            if not tags:
                tags = self._extract_tags_from_prompt(prompt)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO prompt_favorites 
                (prompt, negative_prompt, hash, category, tags, notes, rating, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                prompt, negative_prompt, prompt_hash, category,
                json.dumps(tags) if tags else None, notes, rating
            ))
            
            prompt_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return prompt_id
            
        except Exception as e:
            print(f"[PromptHistory] Error adding to favorites: {e}")
            return -1
    
    def get_history(self, category: str = None, tags: List[str] = None,
                   search_term: str = None, limit: int = 50, 
                   sort_by: str = "last_used", order: str = "DESC") -> List[Dict]:
        """Get prompt history with filtering"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM prompt_history WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search_term:
            query += " AND (prompt LIKE ? OR negative_prompt LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += f" ORDER BY {sort_by} {order} LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        history = []
        
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            
            if item['generation_params']:
                item['generation_params'] = json.loads(item['generation_params'])
            else:
                item['generation_params'] = {}
            
            # Calculate success rate
            total_attempts = item['success_count'] + item['failure_count']
            item['success_rate'] = item['success_count'] / total_attempts if total_attempts > 0 else 0
            
            history.append(item)
        
        conn.close()
        return history
    
    def get_favorites(self, category: str = None, tags: List[str] = None,
                     search_term: str = None, limit: int = 50,
                     sort_by: str = "updated_at", order: str = "DESC") -> List[Dict]:
        """Get favorite prompts"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM prompt_favorites WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search_term:
            query += " AND (prompt LIKE ? OR notes LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += f" ORDER BY {sort_by} {order} LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        favorites = []
        
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            
            favorites.append(item)
        
        conn.close()
        return favorites
    
    def get_templates(self, category: str = None, tags: List[str] = None,
                     search_term: str = None, limit: int = 50,
                     include_public: bool = True) -> List[Dict]:
        """Get prompt templates"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM prompt_templates WHERE 1=1"
        params = []
        
        if not include_public:
            query += " AND is_public = 0"
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search_term:
            query += " AND (name LIKE ? OR template LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += " ORDER BY usage_count DESC, rating_sum DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        templates = []
        
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            
            # Calculate average rating
            if item['rating_count'] > 0:
                item['avg_rating'] = item['rating_sum'] / item['rating_count']
            else:
                item['avg_rating'] = 0
            
            templates.append(item)
        
        conn.close()
        return templates
    
    def add_template(self, name: str, template: str, negative_template: str = "",
                    category: str = None, tags: List[str] = None, 
                    description: str = "", is_public: bool = False) -> int:
        """Add a prompt template"""
        try:
            if not category:
                category = self._auto_categorize_prompt(template)
            
            if not tags:
                tags = self._extract_tags_from_prompt(template)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO prompt_templates 
                (name, template, negative_template, category, tags, description, 
                 is_public, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                name, template, negative_template, category,
                json.dumps(tags) if tags else None, description, is_public
            ))
            
            template_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return template_id
            
        except Exception as e:
            print(f"[PromptHistory] Error adding template: {e}")
            return -1
    
    def get_suggestions(self, base_prompt: str, limit: int = 10) -> List[Dict]:
        """Get intelligent prompt suggestions based on input"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        suggestions = []
        
        # Get similar prompts from history
        cursor.execute('''
            SELECT prompt, negative_prompt, category, tags, success_rate, rating_sum, rating_count
            FROM prompt_history 
            WHERE prompt LIKE ? 
            ORDER BY success_rate DESC, (rating_sum / NULLIF(rating_count, 0)) DESC
            LIMIT ?
        ''', (f"%{base_prompt}%", limit))
        
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            
            item['source'] = 'history'
            item['avg_rating'] = item['rating_sum'] / item['rating_count'] if item['rating_count'] > 0 else 0
            suggestions.append(item)
        
        # Get matching templates
        cursor.execute('''
            SELECT name, template, negative_template, category, tags, usage_count, rating_sum, rating_count
            FROM prompt_templates 
            WHERE template LIKE ? OR name LIKE ?
            ORDER BY usage_count DESC, (rating_sum / NULLIF(rating_count, 0)) DESC
            LIMIT ?
        ''', (f"%{base_prompt}%", f"%{base_prompt}%", limit))
        
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            
            item['source'] = 'template'
            item['avg_rating'] = item['rating_sum'] / item['rating_count'] if item['rating_count'] > 0 else 0
            suggestions.append(item)
        
        conn.close()
        
        # Remove duplicates and sort by relevance
        unique_suggestions = {}
        for item in suggestions:
            key = item.get('prompt', item.get('template', ''))
            if key not in unique_suggestions:
                unique_suggestions[key] = item
        
        # Sort by combined score (success rate + rating + usage)
        sorted_suggestions = sorted(
            unique_suggestions.values(),
            key=lambda x: (x.get('success_rate', 0) + x.get('avg_rating', 0) + min(x.get('usage_count', 0) / 10, 1)),
            reverse=True
        )
        
        return sorted_suggestions[:limit]
    
    def get_autocomplete_suggestions(self, partial_prompt: str, limit: int = 10) -> List[str]:
        """Get autocomplete suggestions for partial prompt"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        suggestions = []
        
        # Get prompts starting with or containing the partial text
        cursor.execute('''
            SELECT DISTINCT prompt FROM prompt_history 
            WHERE prompt LIKE ? 
            ORDER BY success_count DESC, last_used DESC
            LIMIT ?
        ''', (f"{partial_prompt}%", limit))
        
        for row in cursor.fetchall():
            suggestions.append(row[0])
        
        # If not enough, get prompts containing the partial text
        if len(suggestions) < limit:
            cursor.execute('''
                SELECT DISTINCT prompt FROM prompt_history 
                WHERE prompt LIKE ? AND prompt NOT LIKE ?
                ORDER BY success_count DESC, last_used DESC
                LIMIT ?
            ''', (f"%{partial_prompt}%", f"{partial_prompt}%", limit - len(suggestions)))
            
            for row in cursor.fetchall():
                suggestions.append(row[0])
        
        conn.close()
        return suggestions[:limit]
    
    def get_statistics(self) -> Dict:
        """Get prompt usage statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        
        # History stats
        cursor.execute('SELECT COUNT(*) FROM prompt_history')
        stats['total_prompts_in_history'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM prompt_history WHERE success_count > 0')
        stats['successful_prompts'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(success_count * 1.0 / (success_count + failure_count)) FROM prompt_history WHERE success_count + failure_count > 0')
        avg_success = cursor.fetchone()[0]
        stats['average_success_rate'] = round(avg_success or 0, 3)
        
        # Favorites stats
        cursor.execute('SELECT COUNT(*) FROM prompt_favorites')
        stats['total_favorites'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(rating) FROM prompt_favorites WHERE rating > 0')
        avg_rating = cursor.fetchone()[0]
        stats['average_favorite_rating'] = round(avg_rating or 0, 2)
        
        # Templates stats
        cursor.execute('SELECT COUNT(*) FROM prompt_templates')
        stats['total_templates'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(usage_count) FROM prompt_templates')
        total_usage = cursor.fetchone()[0] or 0
        stats['total_template_usage'] = total_usage
        
        # Category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM prompt_history 
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        ''')
        stats['category_distribution'] = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Most used tags
        cursor.execute('''
            SELECT tags, COUNT(*) as count
            FROM prompt_history 
            WHERE tags IS NOT NULL
            GROUP BY tags
            ORDER BY count DESC
            LIMIT 10
        ''')
        stats['popular_tags'] = []
        for row in cursor.fetchall():
            if row[0]:
                tags = json.loads(row[0])
                for tag in tags:
                    stats['popular_tags'].append({'tag': tag, 'count': row[1]})
        
        conn.close()
        return stats
    
    def _auto_categorize_prompt(self, prompt: str) -> str:
        """Automatically categorize a prompt based on content"""
        prompt_lower = prompt.lower()
        
        # Category keywords
        category_keywords = {
            "portrait": ["portrait", "face", "person", "woman", "man", "people", "headshot", "character"],
            "landscape": ["landscape", "nature", "mountain", "forest", "ocean", "sky", "sunset", "sunrise", "scenery"],
            "abstract": ["abstract", "geometric", "pattern", "shapes", "colors", "artistic", "modern art"],
            "fantasy": ["fantasy", "dragon", "magic", "wizard", "fairy", "mythical", "sword", "castle"],
            "anime": ["anime", "manga", "cartoon", "character", "studio ghibli", "japanese"],
            "architecture": ["building", "architecture", "house", "city", "street", "bridge", "tower"],
            "animals": ["animal", "dog", "cat", "bird", "horse", "wildlife", "pet", "creature"],
            "food": ["food", "pizza", "burger", "cake", "coffee", "meal", "cooking", "dish"],
            "fashion": ["fashion", "clothing", "dress", "outfit", "style", "model", "wearing"],
            "technology": ["technology", "computer", "robot", "futuristic", "tech", "digital", "cyber"],
            "vehicles": ["car", "truck", "plane", "boat", "vehicle", "motorcycle", "spaceship"]
        }
        
        # Check for category matches
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return category
        
        return "other"
    
    def _extract_tags_from_prompt(self, prompt: str) -> List[str]:
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
            "vibrant": ["vibrant", "colorful", "bright colors"],
            "dark": ["dark", "moody", "shadow", "dim"],
            "bright": ["bright", "light", "sunny", "vibrant"]
        }
        
        # Composition tags
        composition_keywords = {
            "close-up": ["close up", "close-up", "portrait", "headshot"],
            "wide-angle": ["wide angle", "wide-angle", "landscape", "scenic"],
            "macro": ["macro", "close", "detail", "texture"]
        }
        
        # Combine all keywords
        all_keywords = {**style_keywords, **quality_keywords, **composition_keywords}
        
        for tag, keywords in all_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    extracted_tags.append(tag)
                    break
        
        return list(set(extracted_tags))  # Remove duplicates
    
    def export_data(self, format: str = "json") -> str:
        """Export all prompt data"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        data = {
            "history": [],
            "favorites": [],
            "templates": []
        }
        
        # Export history
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prompt_history")
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            if item['generation_params']:
                item['generation_params'] = json.loads(item['generation_params'])
            data["history"].append(item)
        
        # Export favorites
        cursor.execute("SELECT * FROM prompt_favorites")
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            data["favorites"].append(item)
        
        # Export templates
        cursor.execute("SELECT * FROM prompt_templates")
        for row in cursor.fetchall():
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            data["templates"].append(item)
        
        conn.close()
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            # CSV format for each table
            import csv
            import io
            
            output = io.StringIO()
            output.write("=== PROMPT HISTORY ===\n")
            
            if data["history"]:
                writer = csv.DictWriter(output, fieldnames=data["history"][0].keys())
                writer.writeheader()
                writer.writerows(data["history"])
            
            output.write("\n=== FAVORITES ===\n")
            
            if data["favorites"]:
                writer = csv.DictWriter(output, fieldnames=data["favorites"][0].keys())
                writer.writeheader()
                writer.writerows(data["favorites"])
            
            output.write("\n=== TEMPLATES ===\n")
            
            if data["templates"]:
                writer = csv.DictWriter(output, fieldnames=data["templates"][0].keys())
                writer.writeheader()
                writer.writerows(data["templates"])
            
            return output.getvalue()

# Convenience functions
def create_prompt_manager(data_dir: str = "data") -> PromptHistoryManager:
    """Create a prompt history manager instance"""
    return PromptHistoryManager(data_dir)

def get_prompt_suggestions(partial_prompt: str, limit: int = 10) -> List[str]:
    """Get quick prompt suggestions"""
    manager = PromptHistoryManager()
    return manager.get_autocomplete_suggestions(partial_prompt, limit)
