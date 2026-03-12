"""
Video Generator Manager
Manages video generation models and provides navigation functionality
"""

import json
import os
import time
from typing import Dict, Any, Optional, List
from PIL import Image
import io
import base64
import asyncio
import hashlib
import sys

aiohttp_available = False
sync_requests_available = False
fernet_available = False

try:
    import aiohttp
    aiohttp_available = True
except ImportError:
    pass

try:
    import requests as sync_requests
    sync_requests_available = True
except ImportError:
    pass

try:
    from cryptography.fernet import Fernet
    fernet_available = True
except ImportError:
    pass

if not aiohttp_available and not sync_requests_available:
    print("[VIDEO] Warning: Neither aiohttp nor requests library available. Video API calls will use mock responses.")

if not fernet_available:
    print("[VIDEO] Warning: cryptography library not available. API keys cannot be stored securely without it. Run: pip install cryptography")

# Encryption helper functions
def _get_encryption_key() -> Optional[bytes]:
    """Get or generate encryption key for API key storage.
    
    Priority:
    1. Load existing key from file (most reliable for persistence)
    2. Check environment variable VIDEO_API_KEY_ENC_KEY (for containerized deployments)
    3. Generate new key as last resort (with warning that existing encrypted keys will become inaccessible)
    """
    key_file = os.path.join(os.path.dirname(__file__), 'data', '.video_key')
    
    # First, try to load existing key from file (most reliable for persistence)
    if os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
                # Validate key is 32 bytes for Fernet
                if len(key) == 32:
                    return key
                else:
                    print("[VIDEO] Warning: Invalid key length in file, will generate new key")
        except Exception as e:
            print(f"[VIDEO] Warning: Could not read encryption key file: {e}")
    
    # Second, check environment variable (for containerized deployments)
    key_from_env = os.environ.get('VIDEO_API_KEY_ENC_KEY')
    if key_from_env:
        # Must be valid base64 and 32 bytes for Fernet
        try:
            decoded = base64.urlsafe_b64decode(key_from_env)
            if len(decoded) != 32:
                print("[VIDEO] Warning: VIDEO_API_KEY_ENC_KEY must be 32 bytes, generating new key")
            else:
                # Save env key to file for future use to ensure consistency
                _save_key_to_file(decoded, key_file)
                return decoded
        except Exception:
            print("[VIDEO] Warning: VIDEO_API_KEY_ENC_KEY is invalid, generating new key")
    
    # Third, generate new key as last resort
    print("[VIDEO] WARNING: Generating new encryption key!")
    print("[VIDEO] WARNING: If you have previously stored encrypted API keys, they will become inaccessible!")
    print("[VIDEO] WARNING: To preserve existing keys, set VIDEO_API_KEY_ENC_KEY environment variable or restore the key file.")
    
    key = Fernet.generate_key()
    
    # Save to file for future use
    _save_key_to_file(key, key_file)
    
    return key

def _save_key_to_file(key: bytes, key_file: str) -> None:
    """Save encryption key to file with proper permissions"""
    key_dir = os.path.dirname(key_file)
    if key_dir and not os.path.exists(key_dir):
        os.makedirs(key_dir, exist_ok=True)
    try:
        with open(key_file, 'wb') as f:
            f.write(key)
        # Set restrictive permissions
        try:
            os.chmod(key_file, 0o600)
        except OSError:
            # Windows doesn't support chmod - try Windows-specific ACL
            if sys.platform == 'win32':
                _set_windows_file_permissions(key_file)
    except Exception as e:
        print(f"[VIDEO] Warning: Could not save encryption key: {e}")


def _set_windows_file_permissions(key_file: str) -> None:
    """Set restrictive Windows ACL permissions for encryption key file"""
    import subprocess
    
    # First, print a warning about Windows security implications
    print(f"[VIDEO] Security Warning: Running on Windows - file permissions may not be restrictive.")
    print(f"[VIDEO] The encryption key file '{key_file}' may be readable by other users.")
    print(f"[VIDEO] Consider manually setting permissions using: icacls \"{key_file}\" /inheritance:r /grant:r Administrators:F /grant:r SYSTEM:F")
    
    # Try to use icacls to set restrictive permissions
    try:
        # Remove inheritance and grant only Administrators and SYSTEM full control
        subprocess.run(
            ['icacls', key_file, '/inheritance:r', '/grant:r', 'Administrators:F', 'SYSTEM:F'],
            check=True,
            capture_output=True,
            text=True
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        # If icacls fails or isn't available, try win32security if available
        try:
            import win32security
            import win32api
            
            # Get current DACL
            sd = win32security.GetFileSecurity(key_file, win32security.DACL_SECURITY_INFORMATION)
            dacl = sd.GetSecurityDescriptorDacl()
            
            # Create a new DACL with only Administrators and SYSTEM
            new_dacl = win32security.ACL()
            
            # Get SIDs
            admin_sid = win32security.LookupAccountName(None, "Administrators")[0]
            system_sid = win32security.LookupAccountName(None, "SYSTEM")[0]
            
            # Add ACEs for Administrators and SYSTEM with full control
            new_dacl.AddAccessAllowedAce(win32security.ACL_REVISION, win32security.FILE_ALL_ACCESS, admin_sid)
            new_dacl.AddAccessAllowedAce(win32security.ACL_REVISION, win32security.FILE_ALL_ACCESS, system_sid)
            
            # Set the new DACL
            sd.SetSecurityDescriptorDacl(True, new_dacl, False)
            win32security.SetFileSecurity(key_file, win32security.DACL_SECURITY_INFORMATION, sd)
        except ImportError:
            # win32security not available - user has been warned
            pass

def _encrypt_value(value: str, key: Optional[bytes] = None) -> str:
    """Encrypt a value using Fernet symmetric encryption"""
    if not fernet_available:
        # Fallback: raise error instead of using weak basic encoding
        raise ValueError("cryptography library not available. API key encryption requires 'cryptography' package. Run: pip install cryptography")
    
    try:
        if key is None:
            key = _get_encryption_key()
        f = Fernet(key)
        return f.encrypt(value.encode()).decode()
    except Exception as e:
        print(f"[VIDEO] Warning: Encryption failed: {e}")
        raise ValueError("Failed to encrypt API key")

def _decrypt_value(encrypted_value: str, key: Optional[bytes] = None) -> str:
    """Decrypt a value using Fernet symmetric encryption"""
    if not fernet_available:
        # Fallback: raise error instead of using weak basic decoding
        raise ValueError("cryptography library not available. API key decryption requires 'cryptography' package. Run: pip install cryptography")
    
    try:
        if key is None:
            key = _get_encryption_key()
        f = Fernet(key)
        return f.decrypt(encrypted_value.encode()).decode()
    except Exception as e:
        print(f"[VIDEO] Warning: Decryption failed: {e}")
        raise ValueError("Failed to decrypt API key")

class VideoGeneratorManager:
    """Manages video generation models and provides video generation capabilities"""
    
    def __init__(self):
        self.video_models = []
        self.categories = {}
        self.badges = {}
        self.available_providers = {}
        self.api_keys = {}
        self.current_provider = None
        
        # Track if we're in mock mode (no HTTP libraries available)
        self.mock_mode = not (aiohttp_available or sync_requests_available)
        if self.mock_mode:
            print("[VIDEO] WARNING: Running in MOCK MODE - No HTTP libraries available.")
            print("[VIDEO] Video generation will return mock responses. Install aiohttp or requests to enable real API calls.")
        
        # API keys file for persistence - use project root relative path
        # Support environment variable override for flexibility
        project_root = os.environ.get('VISIONCRAFT_PROJECT_ROOT')
        if project_root:
            self.api_keys_file = os.path.join(project_root, 'data', 'video_api_keys.json')
        else:
            # Fallback: use path relative to this module, normalized to project root
            module_dir = os.path.dirname(os.path.abspath(__file__))
            # If running from project root, use current directory; otherwise use module location
            if os.path.exists(os.path.join(module_dir, 'visioncraft_server.py')):
                self.api_keys_file = os.path.join(module_dir, 'data', 'video_api_keys.json')
            else:
                self.api_keys_file = os.path.join('data', 'video_api_keys.json')
        
        # Load video models from JSON
        self._load_video_models()
        
        # Setup available video providers
        self._setup_providers()
        
        # Load persisted API keys
        self._load_api_keys()
        
        print(f"[VIDEO] Loaded {len(self.video_models)} video models")
        print(f"[VIDEO] Available providers: {list(self.available_providers.keys())}")
        print(f"[VIDEO] Configured providers: {list(self.api_keys.keys())}")
    
    def _load_video_models(self):
        """Load video models from the JSON configuration file"""
        try:
            # Try multiple paths to find the JSON file
            json_paths = [
                "static/video_models.json",
                os.path.join(os.path.dirname(__file__), "static", "video_models.json"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "video_models.json")
            ]
            
            data_loaded = False
            for json_path in json_paths:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        self.video_models = data.get('video_models', [])
                        self.categories = data.get('categories', [])
                        self.badges = data.get('badges', {})
                        print(f"[VIDEO] Loaded video models from {json_path}")
                        data_loaded = True
                        break
            
            if not data_loaded:
                print(f"[VIDEO] Warning: video_models.json not found in any location, using embedded data")
                self._load_embedded_models()
        except Exception as e:
            print(f"[VIDEO] Error loading video models: {e}")
            self._load_embedded_models()
    
    def _load_embedded_models(self):
        """Load embedded video models data"""
        self.video_models = [
            {
                "id": "openai-sora",
                "name": "OpenAI Sora",
                "provider": "OpenAI",
                "description": "Advanced text-to-video model capable of generating highly realistic videos from text prompts.",
                "features": ["Text-to-Video", "Image-to-Video", "Video Extension"],
                "max_duration": "20 seconds",
                "resolution": "Up to 1920x1080",
                "strengths": ["Photorealistic quality", "Physics simulation"],
                "website": "https://openai.com/sora",
                "pricing": "Credits-based",
                "badge": "top-pick"
            },
            {
                "id": "runway-gen3-alpha",
                "name": "Runway Gen-3 Alpha",
                "provider": "Runway",
                "description": "Next-generation AI video generation model with exceptional visual quality.",
                "features": ["Text-to-Video", "Image-to-Video", "Video-to-Video"],
                "max_duration": "10 seconds",
                "resolution": "1280x720",
                "strengths": ["Cinematic quality", "Consistent characters"],
                "website": "https://runwayml.com",
                "pricing": "Subscription",
                "badge": "editor-choice"
            },
            {
                "id": "pika-labs",
                "name": "Pika Labs",
                "provider": "Pika",
                "description": "Fast and intuitive AI video generation platform.",
                "features": ["Text-to-Video", "Image-to-Video", "Video Editing"],
                "max_duration": "10 seconds",
                "resolution": "16:9 aspect ratio",
                "strengths": ["Fast generation", "Easy to use"],
                "website": "https://pika.art",
                "pricing": "Freemium",
                "badge": "fastest"
            },
            {
                "id": "kling-ai",
                "name": "Kling AI",
                "provider": "Kuaishou",
                "description": "Powerful text-to-video model with impressive motion quality.",
                "features": ["Text-to-Video", "Image-to-Video", "Video Extension"],
                "max_duration": "2 minutes",
                "resolution": "1920x1080",
                "strengths": ["Long videos", "Realistic motion"],
                "website": "https://kling.ai",
                "pricing": "Credits-based",
                "badge": "best-value"
            },
            {
                "id": "luma-dream-machine",
                "name": "Luma Dream Machine",
                "provider": "Luma AI",
                "description": "Advanced video generation focused on high-quality, realistic video output.",
                "features": ["Text-to-Video", "Image-to-Video", "Camera Controls"],
                "max_duration": "5 seconds",
                "resolution": "1280x720",
                "strengths": ["Photorealistic", "Natural motion"],
                "website": "https://lumalabs.ai/dream-machine",
                "pricing": "Subscription",
                "badge": "new"
            },
            {
                "id": "minimax-video",
                "name": "Minimax Video",
                "provider": "Minimax",
                "description": "Chinese AI video generation model with strong performance.",
                "features": ["Text-to-Video", "Image-to-Video", "Multi-subject"],
                "max_duration": "10 seconds",
                "resolution": "16:9",
                "strengths": ["Multi-language support", "Fast processing"],
                "website": "https://minimax.ai",
                "pricing": "Credits-based",
                "badge": None
            },
            {
                "id": "seedance",
                "name": "Seedance",
                "provider": "ByteDance",
                "description": "AI video generation from ByteDance with creative capabilities.",
                "features": ["Text-to-Video", "Image-to-Video", "Creative Effects"],
                "max_duration": "10 seconds",
                "resolution": "9:16 (vertical)",
                "strengths": ["Social media optimized", "Creative styles"],
                "website": "https://seedance.com",
                "pricing": "Beta",
                "badge": "social-ready"
            },
            {
                "id": "haiper",
                "name": "Haiper",
                "provider": "Haiper",
                "description": "User-friendly AI video generator with artistic styles.",
                "features": ["Text-to-Video", "Image-to-Video", "Art Styles"],
                "max_duration": "8 seconds",
                "resolution": "1280x720",
                "strengths": ["Artistic quality", "Easy interface"],
                "website": "https://haiper.ai",
                "pricing": "Freemium",
                "badge": None
            },
            {
                "id": "moonvalley",
                "name": "Moonvalley",
                "provider": "Moonvalley",
                "description": "AI video generation focusing on cinematic quality.",
                "features": ["Text-to-Video", "Style Controls", "Camera Movement"],
                "max_duration": "6 seconds",
                "resolution": "16:9",
                "strengths": ["Cinematic look", "Artistic control"],
                "website": "https://moonvalley.ai",
                "pricing": "Credits-based",
                "badge": "artistic"
            },
            {
                "id": "stepo",
                "name": "Stepo",
                "provider": "Stepo",
                "description": "Emerging AI video generation platform.",
                "features": ["Text-to-Video", "Image Animation", "Motion Controls"],
                "max_duration": "5 seconds",
                "resolution": "16:9",
                "strengths": ["Innovation", "Clean interface"],
                "website": "https://stepo.io",
                "pricing": "Freemium",
                "badge": None
            },
            {
                "id": "kling-1-5",
                "name": "Kling 1.5",
                "provider": "Kuaishou",
                "description": "Enhanced Kling with improved physics and longer generation.",
                "features": ["Text-to-Video", "Image-to-Video", "Advanced Physics", "4K Support"],
                "max_duration": "3 minutes",
                "resolution": "3840x2160",
                "strengths": ["4K quality", "Longest duration"],
                "website": "https://kling.ai",
                "pricing": "Credits-based",
                "badge": "premium"
            },
            {
                "id": "runway-gen3-alpha-turbo",
                "name": "Runway Gen-3 Alpha Turbo",
                "provider": "Runway",
                "description": "Faster version of Gen-3 with improved generation speed.",
                "features": ["Text-to-Video", "Image-to-Video", "Quick Mode"],
                "max_duration": "10 seconds",
                "resolution": "1280x720",
                "strengths": ["4x faster", "Same controls"],
                "website": "https://runwayml.com",
                "pricing": "Subscription",
                "badge": "speed"
            }
        ]
        
        self.categories = [
            {"id": "text-to-video", "name": "Text-to-Video", "description": "Generate videos from text descriptions"},
            {"id": "image-to-video", "name": "Image-to-Video", "description": "Animate static images into video"},
            {"id": "video-editing", "name": "Video Editing", "description": "Edit and enhance existing videos"}
        ]
        
        self.badges = {
            "top-pick": {"label": "Top Pick", "color": "cyan"},
            "editor-choice": {"label": "Editor's Choice", "color": "purple"},
            "fastest": {"label": "Fastest", "color": "yellow"},
            "best-value": {"label": "Best Value", "color": "green"},
            "new": {"label": "New", "color": "blue"},
            "premium": {"label": "Premium", "color": "gold"},
            "social-ready": {"label": "Social Ready", "color": "pink"},
            "artistic": {"label": "Artistic", "color": "orange"},
            "speed": {"label": "Speed", "color": "lime"}
        }
    
    def _setup_providers(self):
        """Setup available video generation providers"""
        self.available_providers = {
            "runway": {
                "name": "Runway",
                "api_endpoint": "https://api.runwayml.com/v1/video/generate",
                "requires_api_key": True,
                "models": ["runway-gen3-alpha", "runway-gen3-alpha-turbo"]
            },
            "pika": {
                "name": "Pika Labs",
                "api_endpoint": "https://api.pika.art/v1/generate",
                "requires_api_key": True,
                "models": ["pika-labs"]
            },
            "kling": {
                "name": "Kling AI",
                "api_endpoint": "https://api.kling.ai/v1/videos/generations",
                "requires_api_key": True,
                "models": ["kling-ai", "kling-1-5"]
            },
            "luma": {
                "name": "Luma Dream Machine",
                "api_endpoint": "https://api.lumalabs.ai/dream-machine/v1/generations",
                "requires_api_key": True,
                "models": ["luma-dream-machine"]
            },
            "minimax": {
                "name": "Minimax",
                "api_endpoint": "https://api.minimax.chat/v1/video_generation",
                "requires_api_key": True,
                "models": ["minimax-video"]
            }
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available video models"""
        return self.video_models
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific video model by ID"""
        for model in self.video_models:
            if model.get('id') == model_id:
                return model
        return None
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all video categories"""
        return self.categories
    
    def get_models_by_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get video models by category"""
        models = []
        for model in self.video_models:
            if category_id in model.get('features', []):
                models.append(model)
        return models
    
    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get video models by provider"""
        models = []
        for model in self.video_models:
            if model.get('provider', '').lower() == provider.lower():
                models.append(model)
        return models
    
    def get_badges(self) -> Dict[str, Any]:
        """Get all badge definitions"""
        return self.badges
    
    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """Search video models by query"""
        query = query.lower()
        results = []
        for model in self.video_models:
            if (query in model.get('name', '').lower() or 
                query in model.get('description', '').lower() or
                query in model.get('provider', '').lower()):
                results.append(model)
        return results
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a video provider and persist to file"""
        # Validate API key - use reasonable minimum length
        if not api_key or len(api_key.strip()) < 8:
            raise ValueError(f"Invalid API key for {provider}: key is too short (minimum 8 characters)")
        if len(api_key) > 500:
            raise ValueError(f"Invalid API key for {provider}: key appears corrupted (too long)")
        
        self.api_keys[provider] = api_key
        self._save_api_keys()
        print(f"[VIDEO] API key set for {provider}")
    
    def _load_api_keys(self):
        """Load API keys from file (with decryption)"""
        try:
            # Ensure data directory exists
            data_dir = os.path.dirname(self.api_keys_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            if os.path.exists(self.api_keys_file):
                with open(self.api_keys_file, 'r') as f:
                    loaded_data = json.load(f)
                
                # Handle both encrypted and legacy plaintext formats
                if 'encrypted_keys' in loaded_data:
                    # New encrypted format
                    for key, encrypted_value in loaded_data['encrypted_keys'].items():
                        try:
                            decrypted = _decrypt_value(encrypted_value)
                            if 10 <= len(decrypted) <= 500:
                                self.api_keys[key] = decrypted
                        except Exception as e:
                            print(f"[VIDEO] Failed to decrypt key for {key}: {e}")
                elif 'keys' in loaded_data:
                    # Legacy plaintext format - migrate to encrypted
                    print("[VIDEO] Found legacy plaintext API keys, migrating to encrypted format...")
                    for key, value in loaded_data['keys'].items():
                        if isinstance(value, str) and 10 <= len(value) <= 500:
                            self.api_keys[key] = value
                    # Save in new encrypted format
                    self._save_api_keys()
                
                print(f"[VIDEO] Loaded {len(self.api_keys)} API key(s) from file")
        except Exception as e:
            print(f"[VIDEO] Could not load API keys: {e}")
    
    def _save_api_keys(self):
        """Save API keys to file with encryption and secure permissions"""
        # Backup current keys for rollback on failure
        original_keys = self.api_keys.copy()
        
        try:
            # Ensure data directory exists
            data_dir = os.path.dirname(self.api_keys_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            # Encrypt all keys before saving
            encrypted_keys = {}
            for key, value in self.api_keys.items():
                encrypted_keys[key] = _encrypt_value(value)
            
            data_to_save = {
                'version': 2,
                'encrypted_keys': encrypted_keys
            }
            
            with open(self.api_keys_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            # Set restrictive file permissions (owner read/write only)
            # This helps protect API keys from other users on multi-user systems
            try:
                os.chmod(self.api_keys_file, 0o600)
            except OSError as e:
                # Windows doesn't support chmod, but file may have other protections
                if sys.platform == 'win32':
                    print(f"[VIDEO] Note: File permissions not set (Windows). Consider using NTFS encryption.")
                else:
                    print(f"[VIDEO] Warning: Could not set file permissions: {e}")
            
            print(f"[VIDEO] Saved {len(self.api_keys)} encrypted API key(s) to {self.api_keys_file}")
        except Exception as e:
            # Rollback to original state on failure
            self.api_keys = original_keys
            print(f"[VIDEO] ERROR: Could not save API keys: {e}")
    
    def get_api_keys(self) -> Dict[str, bool]:
        """Get which providers have API keys set (returns empty for security).
        
        Note: This method intentionally returns an empty dict to avoid exposing
        sensitive API keys. Use get_configured_providers() to check which
        providers have keys configured.
        """
        # Return empty dict to avoid exposing which providers have keys configured
        return {}
    
    def get_configured_providers(self) -> List[str]:
        """Get list of providers with API keys configured.
        
        Use this method to check which providers have API keys set.
        For actual API key values, use the internal api_keys dict directly.
        """
        return list(self.api_keys.keys())
    
    async def generate_video(
        self, 
        model_id: str, 
        prompt: str, 
        negative_prompt: str = "",
        duration: str = "5 seconds",
        aspect_ratio: str = "16:9",
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate video using the specified model"""
        # Validate input parameters
        if not model_id:
            raise ValueError("model_id is required")
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("prompt is required")
        if len(prompt) > 2000:
            prompt = prompt[:2000]  # Truncate long prompts
        if len(negative_prompt) > 1000:
            negative_prompt = negative_prompt[:1000]
        
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Unknown video model: {model_id}")
        
        provider_name = model.get('provider', '').lower()
        
        # Find the provider configuration using exact matching
        provider_config = None
        provider_key = None
        for provider_id, config in self.available_providers.items():
            if provider_name.lower() == config['name'].lower():
                provider_config = config
                provider_key = provider_id
                break
        
        if not provider_config:
            # Return mock response for models without API integration
            return await self._generate_mock_video(
                model, prompt, negative_prompt, duration, aspect_ratio,
                reason="No API Integration"
            )
        
        # Check if API key is available
        if provider_config.get('requires_api_key') and provider_key not in self.api_keys:
            # Return error response for missing API key
            return {
                "success": False,
                "video_url": None,
                "thumbnail_url": None,
                "generation_time": 0,
                "model_used": model.get('name'),
                "model_id": model.get('id'),
                "provider": provider_config['name'],
                "error": "API Key Missing",
                "message": f"API key not configured for {provider_config['name']}. Please set it via /set-video-api-key endpoint."
            }
        
        # Try to generate using the API
        try:
            return await self._generate_via_api(
                provider_key, 
                provider_config, 
                model, 
                prompt, 
                negative_prompt, 
                duration, 
                aspect_ratio,
                image_url
            )
        except Exception as e:
            print(f"[VIDEO] API generation failed: {e}")
            # Return error response without exposing internal details to client
            return {
                "success": False,
                "video_url": None,
                "thumbnail_url": None,
                "generation_time": 0,
                "model_used": model.get('name'),
                "model_id": model.get('id'),
                "provider": provider_config['name'],
                "error": "Generation Failed",
                "message": "Video generation failed. Please try again or check your API key configuration."
            }
    
    async def _generate_via_api(
        self,
        provider_key: str,
        provider_config: Dict,
        model: Dict,
        prompt: str,
        negative_prompt: str,
        duration: str,
        aspect_ratio: str,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate video via API provider"""
        api_key = self.api_keys.get(provider_key)
        
        if not api_key:
            raise Exception(f"No API key configured for {provider_key}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build payload with validated input
        payload = {
            "prompt": prompt[:2000] if prompt else "",
            "negative_prompt": negative_prompt[:1000] if negative_prompt else "",
            "duration": duration or "5 seconds",
            "aspect_ratio": aspect_ratio or "16:9",
            "model": model.get('id', '')
        }
        
        if image_url:
            payload["image_url"] = image_url
        
        # Make async API request
        if aiohttp_available:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    provider_config['api_endpoint'],
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Robust response parsing
                        video_url = (
                            result.get('video_url') or 
                            result.get('output', {}).get('url') or
                            result.get('data', {}).get('video_url') or
                            result.get('result', {}).get('video_url')
                        )
                        thumbnail_url = (
                            result.get('thumbnail_url') or 
                            result.get('preview') or
                            result.get('output', {}).get('thumbnail') or
                            result.get('data', {}).get('thumbnail')
                        )
                        generation_time = (
                            result.get('processing_time') or
                            result.get('generation_time') or
                            result.get('processing_time_ms', 0) / 1000
                        )
                        
                        if not video_url:
                            raise Exception(f"Invalid API response: missing video_url. Response: {result}")
                        
                        return {
                            "success": True,
                            "video_url": video_url,
                            "thumbnail_url": thumbnail_url,
                            "generation_time": generation_time,
                            "model_used": model.get('name'),
                            "model_id": model.get('id'),
                            "provider": provider_config['name']
                        }
                    else:
                        response_text = await response.text()
                        raise Exception(f"API error: {response.status} - {response_text}")
        elif sync_requests_available:
            # Fallback to synchronous requests if aiohttp not available
            response = sync_requests.post(
                provider_config['api_endpoint'],
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                # Robust response parsing
                video_url = (
                    result.get('video_url') or 
                    result.get('output', {}).get('url') or
                    result.get('data', {}).get('video_url') or
                    result.get('result', {}).get('video_url')
                )
                thumbnail_url = (
                    result.get('thumbnail_url') or 
                    result.get('preview') or
                    result.get('output', {}).get('thumbnail') or
                    result.get('data', {}).get('thumbnail')
                )
                generation_time = (
                    result.get('processing_time') or
                    result.get('generation_time') or
                    result.get('processing_time_ms', 0) / 1000
                )
                
                if not video_url:
                    raise Exception(f"Invalid API response: missing video_url. Response: {result}")
                
                return {
                    "success": True,
                    "video_url": video_url,
                    "thumbnail_url": thumbnail_url,
                    "generation_time": generation_time,
                    "model_used": model.get('name'),
                    "model_id": model.get('id'),
                    "provider": provider_config['name']
                }
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
        else:
            raise Exception("No HTTP library available (neither aiohttp nor requests)")
    
    async def _generate_mock_video(
        self,
        model: Dict,
        prompt: str,
        negative_prompt: str,
        duration: str,
        aspect_ratio: str,
        reason: str = "Demo mode"
    ) -> Dict[str, Any]:
        """Generate mock video response for demonstration"""
        # Simulate generation time
        await asyncio.sleep(1)
        
        # Create SVG placeholder for thumbnail (data URI to avoid 404 errors)
        svg_placeholder = '''data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTI4MCIgaGVpZ2h0PSI3MjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjEyMDAiIGhlaWdodD0iNzIwIiBmaWxsPSIjMjIyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSI0MCIgZmlsbD0iIzU1NSI+VmlkZW8gR2VuZXJhdGlvbiA8c3BhbiBmaWxsPSIjZmZmIj5Nb2NrPC9zcGFuPjwvdGV4dD48L3N2Zz4='''
        
        # Use placeholder video URL for mock mode - mark as demo/mock clearly
        # Clients should check for 'mock' field in response
        mock_video_url = f"/api/demo/video/{model.get('id', 'unknown')}?prompt={hashlib.urlsafe_b64encode(prompt.encode()).decode()[:20]}"
        
        # Return a mock response
        return {
            "success": True,
            "video_url": mock_video_url,  # Placeholder URL for mock mode - not a playable video
            "thumbnail_url": svg_placeholder,
            "generation_time": 2.5,
            "model_used": model.get('name'),
            "model_id": model.get('id'),
            "provider": model.get('provider'),
            "message": f"[{reason}] Video generation simulated for {model.get('name')}. Configure API keys for actual generation.",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mock": True,
            "mock_mode": self.mock_mode  # Indicates if entire system is in mock mode
        }
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of video providers"""
        status = {}
        for provider_id, config in self.available_providers.items():
            status[provider_id] = {
                "name": config['name'],
                "api_key_configured": provider_id in self.api_keys,
                "models": config['models']
            }
        return status
