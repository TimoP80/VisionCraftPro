"""
Modern Commercial Image Generators
Support for Nano Banana Pro, Seedream, Leonardo.ai API-based generators, and Modal
"""

import requests
import json
import base64
import io
from typing import Dict, Any, Optional, List
from PIL import Image
import json
import os
import time
import asyncio
from datetime import datetime

# Leonardo.ai SDK
try:
    from leonardo_ai_sdk import LeonardoAiSDK
    from leonardo_ai_sdk.models import shared, operations
    LEONARDO_SDK_AVAILABLE = True
except ImportError:
    LEONARDO_SDK_AVAILABLE = False
    print("leonardo-ai-sdk not installed. Install with: pip install leonardo-ai-sdk")

# Modal imports - will be imported conditionally
try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    print("Modal not installed. Install with: pip install modal")

class ModernGeneratorManager:
    """Manages modern commercial image generators"""
    
    def __init__(self):
        self.generators = {}
        self.current_generator = None
        self.api_keys = {}
        self.api_keys_file = "api_keys.json"
        self.pending_callbacks = {}
        self._leonardo_platform_models_cache = {
            "fetched_at": 0.0,
            "models": []
        }
        
        # Load API keys on initialization
        print("Initializing ModernGeneratorManager...")
        self._load_api_keys()
        print(f"Loaded {len(self.api_keys)} API key(s)")
        
        # Initialize available generators
        self.available_generators = {}
        self._setup_leonardo_ai()
        self._setup_modal()  # Move this before Leonardo to ensure Modal is added
        print(f"Initialized {len(self.available_generators)} generator(s)")
        print(f"[SETUP] Modal setup completed. Available generators: {list(self.available_generators.keys())}")

    def _fetch_leonardo_platform_models(self, force: bool = False) -> List[Dict[str, Any]]:
        """Fetch Leonardo platform models (requires API key). Cached to avoid repeated calls."""
        cache_ttl_s = 10 * 60
        now = time.time()

        if not force and (now - float(self._leonardo_platform_models_cache.get("fetched_at", 0.0)) < cache_ttl_s):
            print(f"[LEONARDO] Using cached platform models ({len(self._leonardo_platform_models_cache.get('models', []))} models)")
            return self._leonardo_platform_models_cache.get("models", [])

        api_key = self.api_keys.get("leonardo-api")
        if not api_key:
            print("[LEONARDO] No API key configured, cannot fetch platform models")
            return []

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
        }

        url = "https://cloud.leonardo.ai/api/rest/v1/platformModels"
        print(f"[LEONARDO] Fetching platform models from: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            print(f"[LEONARDO] Response status: {resp.status_code}")
            resp.raise_for_status()
            data = resp.json() or {}
            print(f"[LEONARDO] Response keys: {list(data.keys())}")

            models = data.get("platformModels") or data.get("models") or []
            if not isinstance(models, list):
                models = []
            print(f"[LEONARDO] Fetched {len(models)} platform models")

            self._leonardo_platform_models_cache = {
                "fetched_at": now,
                "models": models,
            }
            return models
        except Exception as e:
            print(f"[WARNING] Failed to fetch Leonardo platform models: {e}")
            return self._leonardo_platform_models_cache.get("models", [])

    def _merge_leonardo_platform_models_into_generator(self):
        """Merge live Leonardo platform models into available_generators['leonardo-api']['models']."""
        if "leonardo-api" not in self.available_generators:
            print("[LEONARDO] leonardo-api not in available_generators")
            return

        generator_info = self.available_generators["leonardo-api"]
        base_models = generator_info.get("models", {})
        if not isinstance(base_models, dict):
            base_models = {}

        platform_models = self._fetch_leonardo_platform_models(force=False)
        merged = dict(base_models)

        print(f"[LEONARDO] Merging {len(platform_models)} platform models into {len(base_models)} base models")
        for m in platform_models:
            model_id = m.get("id")
            name = m.get("name")
            if not model_id:
                continue

            merged[str(model_id)] = {
                "id": str(model_id),
                "name": name or str(model_id),
                "description": m.get("description") or "",
                "max_resolution": generator_info.get("max_resolution", (1024, 1024)),
                "aspect_ratios": [ar.get("id") for ar in generator_info.get("aspect_ratios", []) if isinstance(ar, dict) and ar.get("id")],
                "note": "Platform model (fetched from Leonardo API)",
            }

        generator_info["models"] = merged
        print(f"[LEONARDO] After merge: {len(merged)} total models")

    def _leonardo_model_config(self, model_key: str) -> dict:
        """Return Leonardo model config: api_version, endpoint, modelId, and payload shape."""
        # Explicit mappings from Leonardo docs
        # These map both UUIDs and human-readable internal keys to their config
        mapping = {
            "lucid-origin": {"name": "Lucid Origin", "id": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9", "api_version": "v1", "endpoint": "generations"},
            "7b592283-e8a7-4c5a-9ba6-d18c31f258b9": {"name": "Lucid Origin", "id": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9", "api_version": "v1", "endpoint": "generations"},
            "flux-1-kontext": {"name": "FLUX.1 Kontext", "id": "28aeddf8-bd19-4803-80fc-79602d1a9989", "api_version": "v1", "endpoint": "generations"},
            "28aeddf8-bd19-4803-80fc-79602d1a9989": {"name": "FLUX.1 Kontext", "id": "28aeddf8-bd19-4803-80fc-79602d1a9989", "api_version": "v1", "endpoint": "generations"},
            "lucid-realism": {"name": "Lucid Realism", "id": "05ce0082-2d80-4a2d-8653-4d1c85e2418e", "api_version": "v1", "endpoint": "generations"},
            "05ce0082-2d80-4a2d-8653-4d1c85e2418e": {"name": "Lucid Realism", "id": "05ce0082-2d80-4a2d-8653-4d1c85e2418e", "api_version": "v1", "endpoint": "generations"},
            "phoenix-1-0": {"name": "Phoenix 1.0", "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", "api_version": "v1", "endpoint": "generations"},
            "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3": {"name": "Phoenix 1.0", "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", "api_version": "v1", "endpoint": "generations"},
            "flux-dev": {"name": "Flux Dev", "id": "b2614463-296c-462a-9586-aafdb8f00e36", "api_version": "v1", "endpoint": "generations"},
            "b2614463-296c-462a-9586-aafdb8f00e36": {"name": "Flux Dev", "id": "b2614463-296c-462a-9586-aafdb8f00e36", "api_version": "v1", "endpoint": "generations"},
            "flux-schnell": {"name": "Flux Schnell", "id": "1dd50843-d653-4516-a8e3-f0238ee453ff", "api_version": "v1", "endpoint": "generations"},
            "1dd50843-d653-4516-a8e3-f0238ee453ff": {"name": "Flux Schnell", "id": "1dd50843-d653-4516-a8e3-f0238ee453ff", "api_version": "v1", "endpoint": "generations"},
            "phoenix-0-9": {"name": "Phoenix 0.9", "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042", "api_version": "v1", "endpoint": "generations"},
            "6b645e3a-d64f-4341-a6d8-7a3690fbf042": {"name": "Phoenix 0.9", "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042", "api_version": "v1", "endpoint": "generations"},
            "leonardo-anime-xl": {"name": "Leonardo Anime XL", "id": "e71a1c2f-4f80-4800-934f-2c68979d8cc8", "api_version": "v1", "endpoint": "generations"},
            "e71a1c2f-4f80-4800-934f-2c68979d8cc8": {"name": "Leonardo Anime XL", "id": "e71a1c2f-4f80-4800-934f-2c68979d8cc8", "api_version": "v1", "endpoint": "generations"},
            "leonardo-lightning-xl": {"name": "Leonardo Lightning XL", "id": "b24e16ff-06e3-43eb-8d33-4416c2d75876", "api_version": "v1", "endpoint": "generations"},
            "b24e16ff-06e3-43eb-8d33-4416c2d75876": {"name": "Leonardo Lightning XL", "id": "b24e16ff-06e3-43eb-8d33-4416c2d75876", "api_version": "v1", "endpoint": "generations"},
            "sdxl-1-0": {"name": "SDXL 1.0", "id": "16e7060a-803e-4df3-97ee-edcfa5dc9cc8", "api_version": "v1", "endpoint": "generations"},
            "16e7060a-803e-4df3-97ee-edcfa5dc9cc8": {"name": "SDXL 1.0", "id": "16e7060a-803e-4df3-97ee-edcfa5dc9cc8", "api_version": "v1", "endpoint": "generations"},
            "leonardo-kino-xl": {"name": "Leonardo Kino XL", "id": "aa77f04e-3eec-4034-9c07-d0f619684628", "api_version": "v1", "endpoint": "generations"},
            "aa77f04e-3eec-4034-9c07-d0f619684628": {"name": "Leonardo Kino XL", "id": "aa77f04e-3eec-4034-9c07-d0f619684628", "api_version": "v1", "endpoint": "generations"},
            "leonardo-vision-xl": {"name": "Leonardo Vision XL", "id": "5c232a9e-9061-4777-980a-ddc8e65647c6", "api_version": "v1", "endpoint": "generations"},
            "5c232a9e-9061-4777-980a-ddc8e65647c6": {"name": "Leonardo Vision XL", "id": "5c232a9e-9061-4777-980a-ddc8e65647c6", "api_version": "v1", "endpoint": "generations"},
            "leonardo-diffusion-xl": {"name": "Leonardo Diffusion XL", "id": "1e60896f-3c26-4296-8ecc-53e2afecc132", "api_version": "v1", "endpoint": "generations"},
            "1e60896f-3c26-4296-8ecc-53e2afecc132": {"name": "Leonardo Diffusion XL", "id": "1e60896f-3c26-4296-8ecc-53e2afecc132", "api_version": "v1", "endpoint": "generations"},
            "albedobase-xl": {"name": "AlbedoBase XL", "id": "2067ae52-33fd-4a82-bb92-c2c55e7d2786", "api_version": "v1", "endpoint": "generations"},
            "2067ae52-33fd-4a82-bb92-c2c55e7d2786": {"name": "AlbedoBase XL", "id": "2067ae52-33fd-4a82-bb92-c2c55e7d2786", "api_version": "v1", "endpoint": "generations"},
            "rpg-v5": {"name": "RPG v5", "id": "f1929ea3-b169-4c18-a16c-5d58b4292c69", "api_version": "v1", "endpoint": "generations"},
            "f1929ea3-b169-4c18-a16c-5d58b4292c69": {"name": "RPG v5", "id": "f1929ea3-b169-4c18-a16c-5d58b4292c69", "api_version": "v1", "endpoint": "generations"},
            "sdxl-0-9": {"name": "SDXL 0.9", "id": "b63f7119-31dc-4540-969b-2a9df997e173", "api_version": "v1", "endpoint": "generations"},
            "b63f7119-31dc-4540-969b-2a9df997e173": {"name": "SDXL 0.9", "id": "b63f7119-31dc-4540-969b-2a9df997e173", "api_version": "v1", "endpoint": "generations"},
            "3d-animation-style": {"name": "3D Animation Style", "id": "d69c8273-6b17-4a30-a13e-d6637ae1c644", "api_version": "v1", "endpoint": "generations"},
            "d69c8273-6b17-4a30-a13e-d6637ae1c644": {"name": "3D Animation Style", "id": "d69c8273-6b17-4a30-a13e-d6637ae1c644", "api_version": "v1", "endpoint": "generations"},
            "dreamshaper-v7": {"name": "DreamShaper v7", "id": "ac614f96-1082-45bf-be9d-757f2d31c174", "api_version": "v1", "endpoint": "generations"},
            "ac614f96-1082-45bf-be9d-757f2d31c174": {"name": "DreamShaper v7", "id": "ac614f96-1082-45bf-be9d-757f2d31c174", "api_version": "v1", "endpoint": "generations"},
            "absolute-reality-v1-6": {"name": "Absolute Reality v1.6", "id": "e316348f-7773-490e-adcd-46757c738eb7", "api_version": "v1", "endpoint": "generations"},
            "e316348f-7773-490e-adcd-46757c738eb7": {"name": "Absolute Reality v1.6", "id": "e316348f-7773-490e-adcd-46757c738eb7", "api_version": "v1", "endpoint": "generations"},
            "anime-pastel-dream": {"name": "Anime Pastel Dream", "id": "1aa0f478-51be-4efd-94e8-76bfc8f533af", "api_version": "v1", "endpoint": "generations"},
            "1aa0f478-51be-4efd-94e8-76bfc8f533af": {"name": "Anime Pastel Dream", "id": "1aa0f478-51be-4efd-94e8-76bfc8f533af", "api_version": "v1", "endpoint": "generations"},
            "dreamshaper-v6": {"name": "DreamShaper v6", "id": "b7aa9939-abed-4d4e-96c4-140b8c65dd92", "api_version": "v1", "endpoint": "generations"},
            "b7aa9939-abed-4d4e-96c4-140b8c65dd92": {"name": "DreamShaper v6", "id": "b7aa9939-abed-4d4e-96c4-140b8c65dd92", "api_version": "v1", "endpoint": "generations"},
            "dreamshaper-v5": {"name": "DreamShaper v5", "id": "d2fb9cf9-7999-4ae5-8bfe-f0df2d32abf8", "api_version": "v1", "endpoint": "generations"},
            "d2fb9cf9-7999-4ae5-8bfe-f0df2d32abf8": {"name": "DreamShaper v5", "id": "d2fb9cf9-7999-4ae5-8bfe-f0df2d32abf8", "api_version": "v1", "endpoint": "generations"},
            "leonardo-diffusion": {"name": "Leonardo Diffusion", "id": "b820ea11-02bf-4652-97ae-9ac0cc00593d", "api_version": "v1", "endpoint": "generations"},
            "b820ea11-02bf-4652-97ae-9ac0cc00593d": {"name": "Leonardo Diffusion", "id": "b820ea11-02bf-4652-97ae-9ac0cc00593d", "api_version": "v1", "endpoint": "generations"},
            "rpg-4-0": {"name": "RPG 4.0", "id": "a097c2df-8f0c-4029-ae0f-8fd349055e61", "api_version": "v1", "endpoint": "generations"},
            "a097c2df-8f0c-4029-ae0f-8fd349055e61": {"name": "RPG 4.0", "id": "a097c2df-8f0c-4029-ae0f-8fd349055e61", "api_version": "v1", "endpoint": "generations"},
            "deliberate-1-1": {"name": "Deliberate 1.1", "id": "458ecfff-f76c-402c-8b85-f09f6fb198de", "api_version": "v1", "endpoint": "generations"},
            "458ecfff-f76c-402c-8b85-f09f6fb198de": {"name": "Deliberate 1.1", "id": "458ecfff-f76c-402c-8b85-f09f6fb198de", "api_version": "v1", "endpoint": "generations"},
            "vintage-style-photography": {"name": "Vintage Style Photography", "id": "17e4edbf-690b-425d-a466-53c816f0de8a", "api_version": "v1", "endpoint": "generations"},
            "17e4edbf-690b-425d-a466-53c816f0de8a": {"name": "Vintage Style Photography", "id": "17e4edbf-690b-425d-a466-53c816f0de8a", "api_version": "v1", "endpoint": "generations"},
            "dreamshaper-3-2": {"name": "DreamShaper 3.2", "id": "f3296a34-9aef-4370-ad18-88daf26862c3", "api_version": "v1", "endpoint": "generations"},
            "f3296a34-9aef-4370-ad18-88daf26862c3": {"name": "DreamShaper 3.2", "id": "f3296a34-9aef-4370-ad18-88daf26862c3", "api_version": "v1", "endpoint": "generations"},
            "leonardo-select": {"name": "Leonardo Select", "id": "cd2b2a15-9760-4174-a5ff-4d2925057376", "api_version": "v1", "endpoint": "generations"},
            "cd2b2a15-9760-4174-a5ff-4d2925057376": {"name": "Leonardo Select", "id": "cd2b2a15-9760-4174-a5ff-4d2925057376", "api_version": "v1", "endpoint": "generations"},
            "leonardo-creative": {"name": "Leonardo Creative", "id": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", "api_version": "v1", "endpoint": "generations"},
            "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3": {"name": "Leonardo Creative", "id": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", "api_version": "v1", "endpoint": "generations"},
            "battle-axes": {"name": "Battle Axes", "id": "47a6232a-1d49-4c95-83c3-2cc5342f82c7", "api_version": "v1", "endpoint": "generations"},
            "47a6232a-1d49-4c95-83c3-2cc5342f82c7": {"name": "Battle Axes", "id": "47a6232a-1d49-4c95-83c3-2cc5342f82c7", "api_version": "v1", "endpoint": "generations"},
            "pixel-art": {"name": "Pixel Art", "id": "e5a291b6-3990-495a-b1fa-7bd1864510a6", "api_version": "v1", "endpoint": "generations"},
            "e5a291b6-3990-495a-b1fa-7bd1864510a6": {"name": "Pixel Art", "id": "e5a291b6-3990-495a-b1fa-7bd1864510a6", "api_version": "v1", "endpoint": "generations"},
            "magic-potions": {"name": "Magic Potions", "id": "45ab2421-87de-44c8-a07c-3b87e3bfdf84", "api_version": "v1", "endpoint": "generations"},
            "45ab2421-87de-44c8-a07c-3b87e3bfdf84": {"name": "Magic Potions", "id": "45ab2421-87de-44c8-a07c-3b87e3bfdf84", "api_version": "v1", "endpoint": "generations"},
            "chest-armor": {"name": "Chest Armor", "id": "302e258f-29b5-4dd8-9a7c-0cd898cb2143", "api_version": "v1", "endpoint": "generations"},
            "302e258f-29b5-4dd8-9a7c-0cd898cb2143": {"name": "Chest Armor", "id": "302e258f-29b5-4dd8-9a7c-0cd898cb2143", "api_version": "v1", "endpoint": "generations"},
            "crystal-deposits": {"name": "Crystal Deposits", "id": "102a8ee0-cf16-477c-8477-c76963a0d766", "api_version": "v1", "endpoint": "generations"},
            "102a8ee0-cf16-477c-8477-c76963a0d766": {"name": "Crystal Deposits", "id": "102a8ee0-cf16-477c-8477-c76963a0d766", "api_version": "v1", "endpoint": "generations"},
            "character-portraits": {"name": "Character Portraits", "id": "6c95de60-a0bc-4f90-b637-ee8971caf3b0", "api_version": "v1", "endpoint": "generations"},
            "6c95de60-a0bc-4f90-b637-ee8971caf3b0": {"name": "Character Portraits", "id": "6c95de60-a0bc-4f90-b637-ee8971caf3b0", "api_version": "v1", "endpoint": "generations"},
            "magic-items": {"name": "Magic Items", "id": "2d18c0af-374e-4391-9ca2-639f59837c85", "api_version": "v1", "endpoint": "generations"},
            "2d18c0af-374e-4391-9ca2-639f59837c85": {"name": "Magic Items", "id": "2d18c0af-374e-4391-9ca2-639f59837c85", "api_version": "v1", "endpoint": "generations"},
            "shields": {"name": "Shields", "id": "ee0fc1a3-aacb-48bf-9234-ada3cc02748f", "api_version": "v1", "endpoint": "generations"},
            "ee0fc1a3-aacb-48bf-9234-ada3cc02748f": {"name": "Shields", "id": "ee0fc1a3-aacb-48bf-9234-ada3cc02748f", "api_version": "v1", "endpoint": "generations"},
            "spirit-creatures": {"name": "Spirit Creatures", "id": "5fdadebb-17ae-472c-bf76-877e657f97de", "api_version": "v1", "endpoint": "generations"},
            "5fdadebb-17ae-472c-bf76-877e657f97de": {"name": "Spirit Creatures", "id": "5fdadebb-17ae-472c-bf76-877e657f97de", "api_version": "v1", "endpoint": "generations"},
            "cute-animal-characters": {"name": "Cute Animal Characters", "id": "6908bfaf-8cf2-4fda-8c46-03f892d82e06", "api_version": "v1", "endpoint": "generations"},
            "6908bfaf-8cf2-4fda-8c46-03f892d82e06": {"name": "Cute Animal Characters", "id": "6908bfaf-8cf2-4fda-8c46-03f892d82e06", "api_version": "v1", "endpoint": "generations"},
            "christmas-stickers": {"name": "Christmas Stickers", "id": "4b2e0f95-f15e-48d8-ada3-c071d6104db8", "api_version": "v1", "endpoint": "generations"},
            "4b2e0f95-f15e-48d8-ada3-c071d6104db8": {"name": "Christmas Stickers", "id": "4b2e0f95-f15e-48d8-ada3-c071d6104db8", "api_version": "v1", "endpoint": "generations"},
            "isometric-scifi-buildings": {"name": "Isometric Scifi Buildings", "id": "7a65f0ab-64a7-4be2-bcf3-64a1cc56f627", "api_version": "v1", "endpoint": "generations"},
            "7a65f0ab-64a7-4be2-bcf3-64a1cc56f627": {"name": "Isometric Scifi Buildings", "id": "7a65f0ab-64a7-4be2-bcf3-64a1cc56f627", "api_version": "v1", "endpoint": "generations"},
            "isometric-fantasy": {"name": "Isometric Fantasy", "id": "ab200606-5d09-4e1e-9050-0b05b839e944", "api_version": "v1", "endpoint": "generations"},
            "ab200606-5d09-4e1e-9050-0b05b839e944": {"name": "Isometric Fantasy", "id": "ab200606-5d09-4e1e-9050-0b05b839e944", "api_version": "v1", "endpoint": "generations"},
            "cute-characters": {"name": "Cute Characters", "id": "50c4f43b-f086-4838-bcac-820406244cec", "api_version": "v1", "endpoint": "generations"},
            "50c4f43b-f086-4838-bcac-820406244cec": {"name": "Cute Characters", "id": "50c4f43b-f086-4838-bcac-820406244cec", "api_version": "v1", "endpoint": "generations"},
            "amulets": {"name": "Amulets", "id": "ff883b60-9040-4c18-8d4e-ba7522c6b71d", "api_version": "v1", "endpoint": "generations"},
            "ff883b60-9040-4c18-8d4e-ba7522c6b71d": {"name": "Amulets", "id": "ff883b60-9040-4c18-8d4e-ba7522c6b71d", "api_version": "v1", "endpoint": "generations"},
            "crystal-deposits-alternate": {"name": "Crystal Deposits Alternate", "id": "5fce4543-8e23-4b77-9c3f-202b3f1c211e", "api_version": "v1", "endpoint": "generations"},
            "5fce4543-8e23-4b77-9c3f-202b3f1c211e": {"name": "Crystal Deposits Alternate", "id": "5fce4543-8e23-4b77-9c3f-202b3f1c211e", "api_version": "v1", "endpoint": "generations"},
            "isometric-asteroid-tiles": {"name": "Isometric Asteroid Tiles", "id": "756be0a8-38b1-4946-ad62-c0ac832422e3", "api_version": "v1", "endpoint": "generations"},
            "756be0a8-38b1-4946-ad62-c0ac832422e3": {"name": "Isometric Asteroid Tiles", "id": "756be0a8-38b1-4946-ad62-c0ac832422e3", "api_version": "v1", "endpoint": "generations"},
            "leonardo-signature": {"name": "Leonardo Signature", "id": "291be633-cb24-434f-898f-e662799936ad", "api_version": "v1", "endpoint": "generations"},
            "291be633-cb24-434f-898f-e662799936ad": {"name": "Leonardo Signature", "id": "291be633-cb24-434f-898f-e662799936ad", "api_version": "v1", "endpoint": "generations"},


            # Special Aliases and V2 Models
            "universal": {"name": "Universal Enhanced", "id": "6bef9f1b-713b-4271-9231-ef9090632332", "api_version": "v1", "endpoint": "generations"},
            "6bef9f1b-713b-4271-9231-ef9090632332": {"name": "Universal Enhanced", "id": "6bef9f1b-713b-4271-9231-ef9090632332", "api_version": "v1", "endpoint": "generations"},
            "gemini-image-2": {"name": "Nano Banana Pro", "id": "gemini-image-2", "api_version": "v2", "endpoint": "generations"},
            "flux-pro-2.0": {"name": "FLUX.2 Pro", "id": "flux-pro-2.0", "api_version": "v2", "endpoint": "generations"},
        }

        # Fallback: try to infer by modelId pattern
        if model_key in mapping:
            return mapping[model_key]
        
        # If we don't have an explicit mapping, assume V1 for legacy compatibility but log it
        print(f"[WARNING] No explicit mapping for Leonardo model: {model_key}, using fallback")
        return {"name": model_key, "id": model_key, "api_version": "v1", "endpoint": "generations"}

    def _build_leonardo_payload_v1(self, model_key: str, model_config: dict, prompt: str, **kwargs) -> dict:
        """Build Leonardo V1 payload (modelId, styleUUID, enhancePrompt, etc.)."""
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        
        # Map quality string to numeric value
        quality = kwargs.get("quality", 80)
        if isinstance(quality, str):
            quality_map = {"standard": 60, "high": 80, "ultra": 100}
            quality = quality_map.get(quality.lower(), 80)
        
        payload = {
            "prompt": prompt,
            "modelId": model_config.get("id", model_key),
            "width": width,
            "height": height,
            "num_images": 1,
            "enhancePrompt": kwargs.get("enhancePrompt", False),
        }
        
        # Only add quality if valid numeric
        if isinstance(quality, (int, float)) and quality > 0:
            payload["quality"] = int(quality)

        # Add optional parameters if provided
        if "preset_style" in kwargs:
            # Map preset style names to styleUUIDs (use a common Leonardo UUID for now)
            style_uuid_map = {
                "LEONARDO": "111dc692-d470-4eec-b791-3475abac4c46",
                "CREATIVE": "3cbb655a-7ca4-463f-b697-8a03ad67327c",
                "DYNAMIC": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
                "CINEMATIC": "594c1a08-a522-4e0e-b7ff-e4dac4b6b622",
                "FANTASY_ART": "09d2b5b5-d7c02-905d-9f84051640f4",
                "ANIME": "7d7c2bc5-4b12-4ac3-81a9-630057e9e89f",
                "COMIC_BOOK": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
                "ILLUSTRATION": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
            }
            style_uuid = style_uuid_map.get(kwargs["preset_style"], "111dc692-d470-4eec-b791-3475abac4c46")
            payload["styleUUID"] = style_uuid

        # Add negative prompt if provided
        if kwargs.get("negative_prompt"):
            payload["negative_prompt"] = kwargs["negative_prompt"]

        # Add guidance scale if provided (V1 uses guidance_scale)
        if "guidance_scale" in kwargs and kwargs["guidance_scale"] is not None:
            payload["guidance_scale"] = kwargs["guidance_scale"]

        # Add num_inference_steps if provided
        if "num_inference_steps" in kwargs and kwargs["num_inference_steps"] is not None:
            payload["num_inference_steps"] = kwargs["num_inference_steps"]

        # Add seed if provided (must be a valid integer, not None)
        if "seed" in kwargs and kwargs["seed"] is not None and kwargs["seed"] >= 0:
            payload["seed"] = kwargs["seed"]

        return payload

    def _build_leonardo_payload_v2(self, model_key: str, model_config: dict, prompt: str, **kwargs) -> dict:
        """Build Leonardo V2 payload (model, parameters wrapper, prompt_enhance, style_ids)."""
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        
        # Map quality string to numeric value
        quality = kwargs.get("quality", 80)
        if isinstance(quality, str):
            quality_map = {"standard": 60, "high": 80, "ultra": 100}
            quality = quality_map.get(quality.lower(), 80)
        
        parameters = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "quantity": 1,
            "prompt_enhance": "OFF",  # Default to OFF for V2 models
            "quality": int(quality) if isinstance(quality, (int, float)) and quality > 0 else 80,
        }

        # Add style_ids if preset_style is provided
        if "preset_style" in kwargs:
            # Map preset style names to style_ids (use common Leonardo style UUIDs)
            style_id_map = {
                "LEONARDO": ["111dc692-d470-4eec-b791-3475abac4c46"],
                "CREATIVE": ["3cbb655a-7ca4-463f-b697-8a03ad67327c"],
                "DYNAMIC": ["6fedbf1f-4a17-45ec-84fb-92fe524a29ef"],
                "CINEMATIC": ["594c1a08-a522-4e0e-b7ff-e4dac4b6b622"],
                "FANTASY_ART": ["09d2b5b5-d7c02-905d-9f84051640f4"],
                "ANIME": ["7d7c2bc5-4b12-4ac3-81a9-630057e9e89f"],
                "COMIC_BOOK": ["645e4195-f63d-4715-a3f2-3fb1e6eb8c70"],
                "ILLUSTRATION": ["556c1ee5-ec38-42e8-955a-1e82dad0ffa1"],
            }
            style_ids = style_id_map.get(kwargs["preset_style"], ["111dc692-d470-4eec-b791-3475abac4c46"])
            parameters["style_ids"] = style_ids
        else:
            # Default style_ids for V2 models (required for some models)
            parameters["style_ids"] = ["111dc692-d470-4eec-b791-3475abac4c46"]

        # Add negative prompt if provided
        if kwargs.get("negative_prompt"):
            parameters["negative_prompt"] = kwargs["negative_prompt"]

        # Add guidance scale if provided (V2 uses guidance_scale in parameters)
        if "guidance_scale" in kwargs and kwargs["guidance_scale"] is not None:
            parameters["guidance_scale"] = kwargs["guidance_scale"]

        # Add num_inference_steps if provided (V2 uses steps)
        if "num_inference_steps" in kwargs and kwargs["num_inference_steps"] is not None:
            parameters["steps"] = kwargs["num_inference_steps"]

        # Add seed if provided (must be a valid integer, not None)
        if "seed" in kwargs and kwargs["seed"] is not None and kwargs["seed"] >= 0:
            parameters["seed"] = kwargs["seed"]

        payload = {
            "model": model_config.get("id", model_key),
            "parameters": parameters,
            "public": False,
        }

        return payload
    
    def _setup_leonardo_ai(self):
        """Setup Leonardo.ai generator configuration"""
        self.available_generators["leonardo-api"] = {
            "name": "Leonardo.ai API",
            "type": "api",
            "description": "Professional game asset generator with model selection",
            "api_endpoint": "https://cloud.leonardo.ai/api/rest/v1/generations",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Fast",
            "cost": "Paid",
            "features": ["text-to-image", "fine-tuned-models", "texture-generation"],
            "models": {
"lucid-origin": {
                    "id": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9",
                    "name": "Lucid Origin",
                    "description": "Your go-to model for vibrant, diverse imagery in HD output. Excellent prompt adherence and text rendering.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "flux-1-kontext": {
                    "id": "28aeddf8-bd19-4803-80fc-79602d1a9989",
                    "name": "FLUX.1 Kontext",
                    "description": "FLUX.1 Kontext is an Omni model by Black Forest Labs, built for precise, controllable image generation and editing",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "lucid-realism": {
                    "id": "05ce0082-2d80-4a2d-8653-4d1c85e2418e",
                    "name": "Lucid Realism",
                    "description": "A high-speed model, designed for efficient, quick outputs. Perfect for fast-paced projects without sacrificing quality.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "phoenix-1-0": {
                    "id": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",
                    "name": "Phoenix 1.0",
                    "description": "Leonardo's proprietary foundational model, delivering exceptional prompt adherence and text rendering.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "flux-dev": {
                    "id": "b2614463-296c-462a-9586-aafdb8f00e36",
                    "name": "Flux Dev",
                    "description": "A specialized model built for developers. Great for rapid prototyping and creative iteration.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "flux-schnell": {
                    "id": "1dd50843-d653-4516-a8e3-f0238ee453ff",
                    "name": "Flux Schnell",
                    "description": "A high-speed model, designed for efficient, quick outputs. Perfect for fast-paced projects without sacrificing quality.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "phoenix-0-9": {
                    "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",
                    "name": "Phoenix 0.9",
                    "description": "Preview of our foundational model. Extreme prompt adherence and text rendering.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-anime-xl": {
                    "id": "e71a1c2f-4f80-4800-934f-2c68979d8cc8",
                    "name": "Leonardo Anime XL",
                    "description": "A new high-speed Anime-focused model that excels at a range of anime, illustrative, and CG styles.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-lightning-xl": {
                    "id": "b24e16ff-06e3-43eb-8d33-4416c2d75876",
                    "name": "Leonardo Lightning XL",
                    "description": "Our new high-speed generalist image gen model. Great at everything from photorealism to painterly styles.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "sdxl-1-0": {
                    "id": "16e7060a-803e-4df3-97ee-edcfa5dc9cc8",
                    "name": "SDXL 1.0",
                    "description": "Diffusion-based text-to-image generative model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-kino-xl": {
                    "id": "aa77f04e-3eec-4034-9c07-d0f619684628",
                    "name": "Leonardo Kino XL",
                    "description": "A model with a strong focus on cinematic outputs. Excels at wider aspect ratios, and does not need a negative prompt.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-vision-xl": {
                    "id": "5c232a9e-9061-4777-980a-ddc8e65647c6",
                    "name": "Leonardo Vision XL",
                    "description": "A versatile model that excels at realism and photography. Better results with longer prompts.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-diffusion-xl": {
                    "id": "1e60896f-3c26-4296-8ecc-53e2afecc132",
                    "name": "Leonardo Diffusion XL",
                    "description": "The next phase of the core Leonardo model. Stunning outputs, even with short prompts.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "albedobase-xl": {
                    "id": "2067ae52-33fd-4a82-bb92-c2c55e7d2786",
                    "name": "AlbedoBase XL",
                    "description": "A great generalist model that tends towards more CG artistic outputs. By albedobond.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "rpg-v5": {
                    "id": "f1929ea3-b169-4c18-a16c-5d58b4292c69",
                    "name": "RPG v5",
                    "description": "Anashel returns with another great model, specialising in RPG characters of all kinds.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "sdxl-0-9": {
                    "id": "b63f7119-31dc-4540-969b-2a9df997e173",
                    "name": "SDXL 0.9",
                    "description": "The latest Stable Diffusion model, currently in Beta.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "3d-animation-style": {
                    "id": "d69c8273-6b17-4a30-a13e-d6637ae1c644",
                    "name": "3D Animation Style",
                    "description": "Great at 3D film vibes, capable of complex scenes with rich color. Storyboard time!",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "dreamshaper-v7": {
                    "id": "ac614f96-1082-45bf-be9d-757f2d31c174",
                    "name": "DreamShaper v7",
                    "description": "Lykon is back with another update. This model is great at a range of different styles.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "absolute-reality-v1-6": {
                    "id": "e316348f-7773-490e-adcd-46757c738eb7",
                    "name": "Absolute Reality v1.6",
                    "description": "A photorealistic style model from Lykon. Great at all sorts of photorealism.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "anime-pastel-dream": {
                    "id": "1aa0f478-51be-4efd-94e8-76bfc8f533af",
                    "name": "Anime Pastel Dream",
                    "description": "Pastel anime styling. Use with PMv3 and the anime preset for incredible range. Model by Lykon.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "dreamshaper-v6": {
                    "id": "b7aa9939-abed-4d4e-96c4-140b8c65dd92",
                    "name": "DreamShaper v6",
                    "description": "A new update to an incredibly versatile model, excels at both people and environments, by Lykon.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "dreamshaper-v5": {
                    "id": "d2fb9cf9-7999-4ae5-8bfe-f0df2d32abf8",
                    "name": "DreamShaper v5",
                    "description": "A versatile model great at both photorealism and anime, includes noise offset training, by Lykon.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-diffusion": {
                    "id": "b820ea11-02bf-4652-97ae-9ac0cc00593d",
                    "name": "Leonardo Diffusion",
                    "description": "A model with incredible shading and contrast, great at both photos and artistic styles, by cac0e.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "rpg-4-0": {
                    "id": "a097c2df-8f0c-4029-ae0f-8fd349055e61",
                    "name": "RPG 4.0",
                    "description": "This model is best at creating RPG character portraits with the ability for great photorealism. Created by Anashel.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "deliberate-1-1": {
                    "id": "458ecfff-f76c-402c-8b85-f09f6fb198de",
                    "name": "Deliberate 1.1",
                    "description": "A powerful model created by XpucT that  is great for both photorealism and artistic creations.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "vintage-style-photography": {
                    "id": "17e4edbf-690b-425d-a466-53c816f0de8a",
                    "name": "Vintage Style Photography",
                    "description": "This model can generate a broad range of imagery with a vintage style as if it was taken from a film camera",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "dreamshaper-3-2": {
                    "id": "f3296a34-9aef-4370-ad18-88daf26862c3",
                    "name": "DreamShaper 3.2",
                    "description": "This model by Lykon is great at a range of portrait styles as well as artistic backgrounds.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-select": {
                    "id": "cd2b2a15-9760-4174-a5ff-4d2925057376",
                    "name": "Leonardo Select",
                    "description": "A powerful finetune of SD2.1 that can achieve a high level of realism.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-creative": {
                    "id": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
                    "name": "Leonardo Creative",
                    "description": "An alternative finetune of SD 2.1 that brings a little more creative interpretation to the mix.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "battle-axes": {
                    "id": "47a6232a-1d49-4c95-83c3-2cc5342f82c7",
                    "name": "Battle Axes",
                    "description": "Generate a variety of detailed axe designs with this model. From medieval battle axes to modern chopping axes, this model is great for creating a r...",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "pixel-art": {
                    "id": "e5a291b6-3990-495a-b1fa-7bd1864510a6",
                    "name": "Pixel Art",
                    "description": "A pixel art model that's trained on headshots, but is surprisingly flexible with all sorts of subjects.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "magic-potions": {
                    "id": "45ab2421-87de-44c8-a07c-3b87e3bfdf84",
                    "name": "Magic Potions",
                    "description": "A great model for creating incredible semi-realistic magic potions. Try appending \"intricately detailed, 3d vray render\" to your prompt.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "chest-armor": {
                    "id": "302e258f-29b5-4dd8-9a7c-0cd898cb2143",
                    "name": "Chest Armor",
                    "description": "Create all sorts of chest armor with this model in a consistent style but with wide thematic range.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "crystal-deposits": {
                    "id": "102a8ee0-cf16-477c-8477-c76963a0d766",
                    "name": "Crystal Deposits",
                    "description": "A model for creating crystal deposits. Well-suited for use as items or in an isometric environment.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "character-portraits": {
                    "id": "6c95de60-a0bc-4f90-b637-ee8971caf3b0",
                    "name": "Character Portraits",
                    "description": "A model that's for creating awesome RPG characters of varying classes in a consistent style.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "magic-items": {
                    "id": "2d18c0af-374e-4391-9ca2-639f59837c85",
                    "name": "Magic Items",
                    "description": "Create a wide range of magical items like weapons, shields, boots, books. Very versatile.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "shields": {
                    "id": "ee0fc1a3-aacb-48bf-9234-ada3cc02748f",
                    "name": "Shields",
                    "description": "Create a variety of impressively varied and detailed shield designs. Allows for an incredible range of material types.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "spirit-creatures": {
                    "id": "5fdadebb-17ae-472c-bf76-877e657f97de",
                    "name": "Spirit Creatures",
                    "description": "From whimsical fairy-like beings to mythical creatures, create unique cute spirit characters.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "cute-animal-characters": {
                    "id": "6908bfaf-8cf2-4fda-8c46-03f892d82e06",
                    "name": "Cute Animal Characters",
                    "description": "Perfect for creating adorable and cute animal characters - loveable and playful designs.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "christmas-stickers": {
                    "id": "4b2e0f95-f15e-48d8-ada3-c071d6104db8",
                    "name": "Christmas Stickers",
                    "description": "Generate festive and fun Christmas stickers with this model. From cute and colorful to traditional and elegant.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "isometric-scifi-buildings": {
                    "id": "7a65f0ab-64a7-4be2-bcf3-64a1cc56f627",
                    "name": "Isometric Scifi Buildings",
                    "description": "Great at creating scifi buildings of varying themes. Append the word isometric to your prompt to ensure an isometric view. \"3d vray render\" also helps steer the generation well. ",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "isometric-fantasy": {
                    "id": "ab200606-5d09-4e1e-9050-0b05b839e944",
                    "name": "Isometric Fantasy",
                    "description": "Create all sorts of isometric fantasy environments. Try appending \"3d vray render, isometric\" and using a guidance scale of 6. For the negative prompt, try \"unclear, harsh, oversaturated, soft, blurry\".",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "cute-characters": {
                    "id": "50c4f43b-f086-4838-bcac-820406244cec",
                    "name": "Cute Characters",
                    "description": "Create cute and charming game characters, perfect for adding some whimsy to your game design. Be sure to include the word \"character\" in your prompts for best results.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "amulets": {
                    "id": "ff883b60-9040-4c18-8d4e-ba7522c6b71d",
                    "name": "Amulets",
                    "description": "Create unique and intricate amulets, jewellery and more. Try loading up the prompt terms to steer it in interesting directions.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "crystal-deposits-alternate": {
                    "id": "5fce4543-8e23-4b77-9c3f-202b3f1c211e",
                    "name": "Crystal Deposits Alternate",
                    "description": "An alternative crystal deposits model that gives a slightly more realistic feel with its creations. Try using \"object\" and \"3d vray render\" in your prompts.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "isometric-asteroid-tiles": {
                    "id": "756be0a8-38b1-4946-ad62-c0ac832422e3",
                    "name": "Isometric Asteroid Tiles",
                    "description": "A model for creating isometric asteroid environment tiles. Try appending \"3d vray render, unreal engine, beautiful, intricately detailed, trending on artstation, 8k\" to your prompt.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },
                "leonardo-signature": {
                    "id": "291be633-cb24-434f-898f-e662799936ad",
                    "name": "Leonardo Signature",
                    "description": "The core model of the Leonardo platform. An extremely powerful and diverse finetune which is highly effective for a wide range of uses.",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                },

                "universal": {
                    "id": "6bef9f1b-713b-4271-9231-ef9090632332",
                    "name": "Universal Enhanced",
                    "description": "Universal model with advanced prompt optimization",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Optimized for all content types"
                },
                "gemini-image-2": {
                    "id": "gemini-image-2",
                    "name": "Nano Banana Pro",
                    "description": "State-of-the-art V2 generation model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "V2 Engine Structure"
                },
                "flux-pro-2.0": {
                    "id": "flux-pro-2.0",
                    "name": "FLUX.2 Pro",
                    "description": "High fidelity V2 generation model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "V2 Engine Structure"
                },
            },
            "preset_styles": [
                {"id": "CREATIVE", "name": "Creative", "description": "Balanced creative output"},
                {"id": "DYNAMIC", "name": "Dynamic", "description": "More dynamic and dramatic"},
                {"id": "CINEMATIC", "name": "Cinematic", "description": "Movie-like quality"},
                {"id": "FANTASY_ART", "name": "Fantasy Art", "description": "Fantasy themed"},
                {"id": "ANIME", "name": "Anime", "description": "Anime style"},
                {"id": "COMIC_BOOK", "name": "Comic Book", "description": "Comic book style"}
            ],
            "quality_levels": [
                {"id": "standard", "name": "Standard", "description": "Good quality, faster generation"},
                {"id": "high", "name": "High", "description": "Better quality, moderate time"},
                {"id": "ultra", "name": "Ultra", "description": "Best quality, longer time"}
            ],
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": (1024, 1024)},
                {"id": "16:9", "name": "Widescreen", "resolution": (1344, 768)},
                {"id": "9:16", "name": "Portrait", "resolution": (768, 1344)},
                {"id": "4:3", "name": "Standard", "resolution": (1024, 768)},
                {"id": "3:4", "name": "Vertical", "resolution": (768, 1024)},
                {"id": "2:3", "name": "Tall", "resolution": (832, 1216)},
                {"id": "3:2", "name": "Wide", "resolution": (1216, 832)}
            ]
        }
    
    def _setup_modal(self):
        """Setup Modal generator configuration"""
        print(f"[SETUP] Setting up Modal generator...")
        print(f"[SETUP] MODAL_AVAILABLE: {MODAL_AVAILABLE}")
        
        if not MODAL_AVAILABLE:
            print("[SETUP] Modal not available - skipping setup")
            return
            
        print("[SETUP] Adding Modal to available generators...")
        self.available_generators["modal"] = {
            "name": "Modal Cloud GPU",
            "type": "modal",
            "description": "Infinite scalability with selectable NVIDIA GPUs (T4 to H200/B200).",
            "api_endpoint": "modal://remote",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Configurable (Fast to Ultra)",
            "cost": "Pay-per-use (Modal Credit)",
            "features": ["text-to-image", "cloud-rendering", "multi-gpu-support", "fast-generation"],
            "models": {
                "runwayml/stable-diffusion-v1-5": {
                    "name": "Stable Diffusion v1.5",
                    "description": "Classic Stable Diffusion model",
                    "max_resolution": (768, 768),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Fast generation on H100"
                },
                "stabilityai/stable-diffusion-xl-base-1.0": {
                    "name": "Stable Diffusion XL",
                    "description": "High-quality SDXL model",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Higher quality, longer generation"
                },
                "stabilityai/sdxl-turbo": {
                    "name": "SDXL Turbo",
                    "description": "Ultra-fast SDXL variant",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Very fast, fewer steps recommended"
                },
                "stabilityai/stable-diffusion-2-1-base": {
                    "name": "Stable Diffusion v2.1",
                    "description": "Stable Diffusion 2.1 (base checkpoint)",
                    "max_resolution": (768, 768),
                    "aspect_ratios": ["1:1", "9:16", "16:9"],
                    "note": "Good general-purpose model"
                },
                "black-forest-labs/FLUX.1-schnell": {
                    "name": "FLUX.1 Schnell",
                    "description": "Fast FLUX model (non-SD pipeline)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Uses FluxPipeline on Modal"
                },
                "stabilityai/stable-diffusion-3.5-large": {
                    "name": "Stable Diffusion 3.5 Large",
                    "description": "SD3.5 (StableDiffusion3Pipeline)",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16"],
                    "note": "Uses StableDiffusion3Pipeline on Modal"
                }
            },
            "aspect_ratios": [
                {"id": "1:1", "name": "Square", "resolution": (768, 768)},
                {"id": "16:9", "name": "Widescreen", "resolution": (1024, 576)},
                {"id": "9:16", "name": "Portrait", "resolution": (576, 1024)},
                {"id": "4:3", "name": "Standard", "resolution": (896, 672)},
                {"id": "3:4", "name": "Vertical", "resolution": (672, 896)}
            ],
            "quality_levels": [
                {"id": "standard", "name": "Standard", "description": "20 steps, good quality"},
                {"id": "high", "name": "High", "description": "30 steps, better quality"},
                {"id": "ultra", "name": "Ultra", "description": "50 steps, best quality"}
            ],
            "gpus": [
                {"id": "T4", "name": "NVIDIA T4 (Entry level)"},
                {"id": "L4", "name": "NVIDIA L4 (Balanced)"},
                {"id": "A10", "name": "NVIDIA A10 (High performance)"},
                {"id": "L40S", "name": "NVIDIA L40S (Multi-purpose)"},
                {"id": "A100 40gb", "name": "NVIDIA A100 40GB (Professional)"},
                {"id": "A100 80gb", "name": "NVIDIA A100 80GB (Professional High VRAM)"},
                {"id": "H100", "name": "NVIDIA H100 (State-of-the-art)"},
                {"id": "H200", "name": "NVIDIA H200 (Next-gen)"},
                {"id": "B200", "name": "NVIDIA B200 (Future-ready)"}
            ]
        }

        # Restore additional modern generators that were supported before Modal integration
        # (they require API keys to actually run).
        self.available_generators.setdefault("nano-banana-pro", {
            "name": "Nano Banana Pro",
            "type": "api",
            "description": "Fast commercial generator (requires API key)",
            "api_endpoint": "",
            "max_resolution": (1024, 1024),
            "quality": "High",
            "speed": "Very Fast",
            "cost": "Paid",
            "features": ["text-to-image"],
        })

        self.available_generators.setdefault("seedream", {
            "name": "Seedream",
            "type": "api",
            "description": "Professional generator with style control (requires API key)",
            "api_endpoint": "",
            "max_resolution": (1024, 1024),
            "quality": "Professional",
            "speed": "Fast",
            "cost": "Paid",
            "features": ["text-to-image"],
        })
    
    def set_api_key(self, generator_name: str, api_key: str):
        """Set API key for a generator and persist to file"""
        self.api_keys[generator_name] = api_key
        if generator_name == "leonardo-api":
            self._leonardo_platform_models_cache = {
                "fetched_at": 0.0,
                "models": []
            }
        self._save_api_keys()
        print(f"[OK] API key set for {generator_name}")

        if generator_name == "leonardo-api":
            self._merge_leonardo_platform_models_into_generator()
    
    def _load_api_keys(self):
        """Load API keys from file"""
        try:
            if os.path.exists(self.api_keys_file):
                with open(self.api_keys_file, 'r') as f:
                    loaded_keys = json.load(f)
                    # Validate API keys to ensure they're not corrupted
                    for key, value in loaded_keys.items():
                        if isinstance(value, str) and len(value) > 1000:
                            print(f"[WARNING] API key for {key} appears corrupted (too long), skipping")
                            continue
                        if not isinstance(value, str) or len(value) < 10:
                            print(f"[WARNING] API key for {key} appears invalid, skipping")
                            continue
                        self.api_keys[key] = value
                    print(f"[OK] Loaded {len(self.api_keys)} valid API key(s)")
        except Exception as e:
            print(f"[WARNING] Could not load API keys: {e}")
            self.api_keys = {}
    
    def _save_api_keys(self):
        """Save API keys to file"""
        try:
            with open(self.api_keys_file, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
            print(f"[SAVE] Saved API keys to {self.api_keys_file}")
        except Exception as e:
            print(f"[ERROR] Could not save API keys: {e}")
    
    def get_available_generators(self) -> Dict[str, Dict]:
        """Get all available modern generators"""
        # Keep Leonardo model list fresh if API key is configured.
        if "leonardo-api" in self.api_keys:
            print("[LEONARDO] API key present, attempting to merge platform models")
            self._merge_leonardo_platform_models_into_generator()
        return self.available_generators
    
    def get_generator_info(self, generator_name: str) -> Optional[Dict]:
        """Get information about a specific generator"""
        return self.available_generators.get(generator_name)
    
    async def generate_with_nano_banana_pro(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Nano Banana Pro API"""
        if "nano-banana-pro" not in self.api_keys:
            raise ValueError("API key required for Nano Banana Pro")

        endpoint = (self.available_generators.get("nano-banana-pro") or {}).get("api_endpoint")
        if not endpoint or not isinstance(endpoint, str) or not endpoint.startswith("http"):
            raise ValueError(
                "Nano Banana Pro api_endpoint is not configured. "
                "Set a valid URL in modern_generators.py available_generators['nano-banana-pro']['api_endpoint']."
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['nano-banana-pro']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
            "steps": kwargs.get("num_inference_steps", 20),
            "guidance_scale": kwargs.get("guidance_scale", 7.5),
            "style": kwargs.get("style", "realistic"),
            "quality": kwargs.get("quality", "high")
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            image_data = base64.b64decode(result["image"])
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            print(f"[ERROR] Nano Banana Pro generation failed: {e}")
            raise
    
    async def generate_with_seedream(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Seedream API"""
        if "seedream" not in self.api_keys:
            raise ValueError("API key required for Seedream")

        endpoint = (self.available_generators.get("seedream") or {}).get("api_endpoint")
        if not endpoint or not isinstance(endpoint, str) or not endpoint.startswith("http"):
            raise ValueError(
                "Seedream api_endpoint is not configured. "
                "Set a valid URL in modern_generators.py available_generators['seedream']['api_endpoint']."
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['seedream']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
            "style_preset": kwargs.get("style_preset", "photorealistic"),
            "quality": kwargs.get("quality", "ultra"),
            "negative_prompt": kwargs.get("negative_prompt", "")
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            
            result = response.json()
            image_data = base64.b64decode(result["image"])
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            print(f"[ERROR] Seedream generation failed: {e}")
            raise
    
    async def generate_with_modal(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Modal (gpu selectable) via web endpoint"""
        # Get model name from kwargs
        model_name = kwargs.get("model", "runwayml/stable-diffusion-v1-5")

        width = int(kwargs.get("width", 512) or 512)
        height = int(kwargs.get("height", 512) or 512)
        num_inference_steps = int(kwargs.get("num_inference_steps", 20) or 20)
        guidance_scale = float(kwargs.get("guidance_scale", 7.5) or 7.5)
        gpu = kwargs.get("gpu", "A100 40gb")

        # Prefer env var so you can paste the URL that `modal serve modal_web.py` prints.
        # Example: https://timop80--visioncraft-modal-fastapi-app-dev.modal.run
        base_url = os.environ.get(
            "VISIONCRAFT_MODAL_ENDPOINT",
            "https://timop80--visioncraft-modal-fastapi-app-dev.modal.run",
        ).rstrip("/")
        url = f"{base_url}/generate"

        try:
            import httpx
            import io
            from PIL import Image

            print(f"[MODAL] Calling Modal web endpoint...")
            print(f"[MODAL] Endpoint: {url}")
            print(f"[MODAL] Model: {model_name}")
            print(f"[MODAL] Prompt: {prompt[:100]}...")

            request_params = {
                "prompt": prompt,
                "model_name": model_name,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "gpu": gpu,
            }

            async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
                response = await client.post(url, params=request_params)

            if getattr(response, "history", None):
                for r in response.history:
                    loc = r.headers.get("location")
                    print(f"[MODAL] Redirect {r.status_code} {r.url} -> {loc}")

            if response.status_code == 200:
                print(f"[MODAL] Received {len(response.content)} bytes from Modal")
                image = Image.open(io.BytesIO(response.content))
                print(f"[MODAL] Image loaded: {image.size}")
                return image

            # Non-200
            print(f"[MODAL] Error: HTTP {response.status_code}")
            print(f"[MODAL] Response: {response.text}")
            raise ValueError(f"Modal web endpoint error: {response.status_code} {response.text}")

        except Exception as e:
            print(f"[ERROR] Modal generation failed: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise
    
    async def generate_with_dall_e_3(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using DALL-E 3 API"""
        if "dall-e-3" not in self.api_keys:
            raise ValueError("API key required for DALL-E 3")
        
        headers = {
            "Authorization": f"Bearer {self.api_keys['dall-e-3']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": f"{kwargs.get('width', 1024)}x{kwargs.get('height', 1024)}",
            "quality": kwargs.get("quality", "standard"),
            "n": 1
        }
        
        try:
            response = requests.post(
                self.available_generators["dall-e-3"]["api_endpoint"],
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            image_url = result["data"][0]["url"]
            
            # Download the image
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            image = Image.open(io.BytesIO(image_response.content))
            return image
            
        except Exception as e:
            print(f"[ERROR] DALL-E 3 generation failed: {e}")
            raise
    
    def _enhance_prompt_for_leonardo(self, prompt: str) -> str:
        """Enhance prompt for maximum quality with SD 1.5"""
        
        # Base quality terms that work well with SD 1.5
        quality_base = [
            "high quality", "highly detailed", "sharp focus", "well-defined",
            "professional", "masterpiece", "best quality", "8k resolution"
        ]
        
        # Style-specific enhancements
        style_enhancements = {
            "photorealistic": [
                "photorealistic", "realistic", "lifelike", "professional photography",
                "DSLR", "shot on Sony A7R IV", "85mm lens", "f/1.4", "sharp details",
                "natural lighting", "studio lighting", "cinematic lighting"
            ],
            "portrait": [
                "photorealistic portrait", "detailed face", "realistic skin texture",
                "professional photography", "studio lighting", "soft lighting",
                "sharp eyes", "detailed hair", "natural expression", "high resolution"
            ],
            "cinematic": [
                "cinematic shot", "film still", "movie quality", "epic composition",
                "dramatic lighting", "cinematic color grading", "film grain",
                "anamorphic lens", "widescreen", "professional cinematography"
            ],
            "artistic": [
                "digital art", "concept art", "detailed illustration", "trending on artstation",
                "masterpiece", "award-winning", "highly detailed", "professional art",
                "sharp details", "vibrant colors", "perfect composition"
            ],
            "anime": [
                "high quality anime", "detailed anime art", "masterpiece", "best quality",
                "trending on pixiv", "sharp details", "vibrant colors", "professional anime art",
                "clean lines", "detailed background", "perfect anatomy"
            ]
        }
        
        # Determine content type and apply appropriate enhancements
        prompt_lower = prompt.lower()
        
        # Detect content type
        if "portrait" in prompt_lower or "woman" in prompt_lower or "man" in prompt_lower or "person" in prompt_lower:
            content_type = "portrait"
        elif "cinematic" in prompt_lower or "movie" in prompt_lower or "film" in prompt_lower:
            content_type = "cinematic"
        elif "anime" in prompt_lower or "manga" in prompt_lower:
            content_type = "anime"
        elif "art" in prompt_lower or "painting" in prompt_lower or "illustration" in prompt_lower:
            content_type = "artistic"
        else:
            content_type = "photorealistic"
        
        # Build enhanced prompt
        enhanced_parts = [prompt]
        
        # Add style-specific enhancements
        if content_type in style_enhancements:
            enhanced_parts.extend(style_enhancements[content_type])
        
        # Add base quality terms
        enhanced_parts.extend(quality_base)
        
        # Add technical photography terms for realism
        if content_type in ["photorealistic", "portrait", "cinematic"]:
            enhanced_parts.extend([
                "RAW photo", "no compression", "uncompressed", "high resolution",
                "professional grade", "commercial photography"
            ])
        
        return ", ".join(enhanced_parts)
    
    def _get_optimized_negative_prompt(self, original_negative: str = "") -> str:
        """Create comprehensive negative prompt for SD 1.5"""
        base_negative = (
            "blurry, low quality, worst quality, low resolution, pixelated, "
            "jpeg artifacts, compression artifacts, noisy, grainy, distorted, "
            "deformed, disfigured, bad anatomy, bad proportions, extra limbs, "
            "missing limbs, fused fingers, too many fingers, watermark, signature, "
            "text, username, error, mutated, mutation, ugly, disgusting"
        )
        
        if original_negative:
            return f"{original_negative}, {base_negative}"
        return base_negative
    
    async def generate_with_leonardo(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image using Leonardo.ai API via REST endpoint"""
        print(f"[ART] Leonardo.ai generation with {prompt[:100]}...")

        # Check API key
        if 'leonardo-api' not in self.api_keys:
            raise ValueError("Leonardo.ai API key not set. Please set your API key first.")

        api_key = self.api_keys['leonardo-api']

        # Validate API key format
        if not isinstance(api_key, str) or len(api_key) > 1000 or len(api_key) < 10:
            raise ValueError("Leonardo.ai API key appears to be corrupted or invalid. Please check your API key configuration.")

        print(f"API key found: {'*' * 10}{api_key[-4:]}")

        # Get parameters
        model_key = kwargs.get("model", "phoenix-1-0")
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)

        print(f"[API] Model: {model_key}, Resolution: {width}x{height}")

        # Get model config
        model_config = self._leonardo_model_config(model_key)
        api_version = model_config["api_version"]
        endpoint_path = model_config["endpoint"]
        full_endpoint = f"https://cloud.leonardo.ai/api/rest/{api_version}/{endpoint_path}"

        print(f"[API] Endpoint: {full_endpoint}")

        # Build payload
        if api_version == "v2":
            payload = self._build_leonardo_payload_v2(model_key, model_config, prompt, **kwargs)
        else:
            payload = self._build_leonardo_payload_v1(model_key, model_config, prompt, **kwargs)

        print(f"[API] Payload: {json.dumps(payload, indent=2)}")

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }

        try:
            response = requests.post(
                full_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract generation ID
            if "sdGenerationJob" in data and "generationId" in data["sdGenerationJob"]:
                generation_id = data["sdGenerationJob"]["generationId"]
            elif "generations_by_pk" in data and "id" in data["generations_by_pk"]:
                generation_id = data["generations_by_pk"]["id"]
            else:
                raise ValueError("Could not extract generation ID from response")
            
            print(f"[API] Generation started: {generation_id}")
            
            # Poll for completion
            return await self._poll_leonardo_generation(generation_id, headers)
            
        except Exception as e:
            print(f"[ERROR] Leonardo.ai generation failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _wait_for_leonardo_callback(self, generation_id: str, callback_id: str, headers: dict) -> Image.Image:
        """Wait for Leonardo.ai callback or fall back to polling"""
        print(f"[WAIT] Waiting for Leonardo.ai callback: {callback_id}")
        
        # Store callback info for the webhook handler
        if not hasattr(self, 'pending_callbacks'):
            self.pending_callbacks = {}
        
        # Create an event to wait for the callback
        callback_event = asyncio.Event()
        self.pending_callbacks[callback_id] = {
            "event": callback_event,
            "generation_id": generation_id,
            "headers": headers
        }
        
        # Wait for callback (timeout after 3 minutes)
        try:
            await asyncio.wait_for(callback_event.wait(), timeout=180)
            
            # Get the result from the callback handler
            if callback_id in self.pending_callbacks and "result" in self.pending_callbacks[callback_id]:
                result = self.pending_callbacks[callback_id]["result"]
                del self.pending_callbacks[callback_id]
                
                if result["success"]:
                    # Download the image
                    image_response = requests.get(result["image_url"], timeout=30)
                    image_response.raise_for_status()
                    
                    image = Image.open(io.BytesIO(image_response.content))
                    print(f"[OK] Leonardo.ai generation completed via callback")
                    return image
                else:
                    raise Exception(f"Leonardo.ai callback error: {result['error']}")
            else:
                raise TimeoutError("Callback received but no result found")
                
        except asyncio.TimeoutError:
            print(f"[TIME] Leonardo.ai callback timeout, falling back to polling")
            del self.pending_callbacks[callback_id]
            return await self._poll_leonardo_generation(generation_id, headers)
    
    async def _poll_leonardo_generation(self, generation_id: str, headers: dict) -> Image.Image:
        """Official Leonardo.ai API polling method following their documentation"""
        print(f"[RELOAD] Polling Leonardo.ai generation: {generation_id}")
        
        # Use the correct endpoint for getting generation status
        status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        
        for attempt in range(180):  # Poll for up to 6 minutes (180 * 2 seconds)
            try:
                status_response = requests.get(status_url, headers=headers, timeout=10)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                
                # Leonardo.ai nests the generation data under "generations_by_pk"
                generation_data = status_data.get("generations_by_pk", {})
                current_status = generation_data.get("status")
                
                print(f"[RELOAD] Poll attempt {attempt + 1}/180 - Status: {current_status}")
                
                # Check if generation is complete
                if current_status == "COMPLETE":
                    print(f"[OK] Generation complete! Retrieving image...")
                    
                    # Get the image URL from the nested structure
                    generated_images = generation_data.get("generated_images", [])
                    if len(generated_images) > 0:
                        image_url = generated_images[0]["url"]
                        
                        # Download the image
                        image_response = requests.get(image_url, timeout=30)
                        image_response.raise_for_status()
                        
                        image = Image.open(io.BytesIO(image_response.content))
                        print(f"[OK] Leonardo.ai generation completed via polling")
                        return image
                    else:
                        raise Exception("Generation marked as COMPLETE but no images found")
                
                # Check for failed status
                elif current_status == "FAILED":
                    error_message = generation_data.get("errorMessage", "Unknown error")
                    raise Exception(f"Leonardo.ai generation failed: {error_message}")
                
                # Continue polling for other statuses (PENDING, RUNNING, etc.)
                else:
                    # Implement delay as per best practices (2-3 seconds between requests)
                    await asyncio.sleep(3)  # Using 3 seconds as recommended
                    
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Polling request failed: {e}")
                await asyncio.sleep(3)  # Wait before retry
        
        raise TimeoutError("Generation timed out after 6 minutes")
    
    def handle_leonardo_callback(self, callback_id: str, webhook_data: dict):
        """Handle Leonardo.ai webhook callback"""
        print(f"[CALLBACK] Received Leonardo.ai callback: {callback_id}")
        
        if hasattr(self, 'pending_callbacks') and callback_id in self.pending_callbacks:
            callback_info = self.pending_callbacks[callback_id]
            
            try:
                # Parse the webhook data
                if webhook_data.get("status") == "COMPLETE":
                    callback_info["result"] = {
                        "success": True,
                        "image_url": webhook_data["url"],
                        "generation_id": webhook_data.get("generationId")
                    }
                else:
                    callback_info["result"] = {
                        "success": False,
                        "error": webhook_data.get("error", "Unknown error")
                    }
                
                # Signal that callback was received
                callback_info["event"].set()
                print(f"[OK] Leonardo.ai callback processed: {callback_id}")
                
            except Exception as e:
                print(f"[ERROR] Error processing Leonardo.ai callback: {e}")
    
    async def upscale_with_leonardo(self, image: Image.Image, upscale_factor: float = 2.0, **kwargs) -> Image.Image:
        """Upscale image using Leonardo.ai Universal Upscaler"""
        print(f"[UPSCALE] Leonardo.ai upscaling with factor {upscale_factor}...")
        
        # Check API key
        if 'leonardo-api' not in self.api_keys:
            raise ValueError("Leonardo.ai API key not set. Please set your API key first.")
        
        api_key = self.api_keys['leonardo-api']
        
        # Validate API key format
        if not isinstance(api_key, str) or len(api_key) > 1000 or len(api_key) < 10:
            raise ValueError("Leonardo.ai API key appears to be corrupted or invalid. Please check your API key configuration.")
        
        print(f"[UPSCALE] API key found: {'*' * 10}{api_key[-4:]}")
        
        # Step 1: Upload the image to get an image ID
        image_id = await self._upload_image_to_leonardo(image, api_key)
        
        # Step 2: Use Universal Upscaler with the uploaded image ID
        print(f"[UPSCALE] Using Universal Upscaler with image ID: {image_id}")
        return await self._upscale_with_image_id(image_id, upscale_factor, api_key, **kwargs)
    
    async def _generate_from_image(self, image_id: str, api_key: str, **kwargs) -> str:
        """Generate an image using uploaded image as input"""
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        
        # Use a simple model for image-to-image generation
        prompt = kwargs.get("prompt", "enhance image details and quality")
        if not prompt or prompt.strip() == "":
            prompt = "enhance image details and quality"  # Ensure we always have a prompt
            
        payload = {
            "modelId": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",  # Phoenix 1.0 - Best quality for variations
            "prompt": prompt,
            "width": 1024,
            "height": 576,
            "init_image_id": image_id,  # For uploaded images
            "init_strength": 0.8,  # How much to influence from init image
            "num_images": 1
        }
        
        print(f"[UPSCALE] Generation payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/generations",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Log detailed error information
            if response.status_code != 200:
                print(f"[ERROR] Generation API Response Status: {response.status_code}")
                print(f"[ERROR] Generation API Response Headers: {dict(response.headers)}")
                try:
                    error_data = response.json()
                    print(f"[ERROR] Generation API Response Body: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"[ERROR] Generation API Response Text: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            generation_id = data.get("sdGenerationJob", {}).get("generationId")
            
            if not generation_id:
                raise Exception("No generation ID returned")
            
            # Poll for completion
            generated_image = await self._poll_leonardo_generation(generation_id, headers)
            
            # Extract the generated image ID from the generation response
            # The polling returns the image, but we need the ID for upscaling
            # Let's make another API call to get the generation details
            status_response = requests.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers=headers,
                timeout=10
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            # Get the generated image ID
            generations_by_pk = status_data.get("generations_by_pk", {})
            generated_images = generations_by_pk.get("generated_images", [])
            
            if len(generated_images) > 0:
                return generated_images[0].get("id")
            else:
                raise Exception("No generated image ID found")
            
        except Exception as e:
            print(f"[ERROR] Failed to generate from image: {e}")
            raise
    
    async def _upscale_generated_image(self, image_id: str, upscale_factor: float, api_key: str, **kwargs) -> Image.Image:
        """Upscale a Leonardo-generated image"""
        print(f"[UPSCALE] Upscaling Leonardo-generated image: {image_id}")
        
        # Check API limits
        max_multiplier = 2.0
        if upscale_factor > max_multiplier:
            print(f"[UPSCALE] Warning: Leonardo.ai only supports up to {max_multiplier}x upscaling. Reducing from {upscale_factor}x to {max_multiplier}x")
            upscale_factor = max_multiplier
        
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        
        # Use the regular upscale endpoint with Leonardo-generated image
        payload = {
            "id": image_id
        }
        
        print(f"[UPSCALE] Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/variations/upscale",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"[ERROR] API Response Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"[ERROR] API Response Body: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"[ERROR] API Response Text: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            print(f"[UPSCALE] Upscale response: {json.dumps(result, indent=2)}")
            
            # Extract ID from nested structure (Leonardo.ai uses sdUpscaleJob.id)
            if "sdUpscaleJob" in result and isinstance(result["sdUpscaleJob"], dict):
                upscaling_id = result["sdUpscaleJob"].get("id")
            else:
                # Fallback to top-level fields
                upscaling_id = (result.get("id") or 
                               result.get("variationId") or 
                               result.get("upscaleId") or
                               result.get("jobId"))
            
            if not upscaling_id:
                print(f"[ERROR] No upscaling ID found in response: {list(result.keys())}")
                raise Exception("Could not extract upscaling ID from response")
            
            print(f"[UPSCALE] Upscaling initiated: {upscaling_id}")
            
            # Poll for completion
            return await self._poll_leonardo_upscale(upscaling_id, headers)
            
        except Exception as e:
            print(f"[ERROR] Leonardo.ai upscaling failed: {e}")
            raise
    
    async def _upscale_with_base64(self, image_b64: str, upscale_factor: float, api_key: str, **kwargs) -> Image.Image:
        """Upscale using Leonardo.ai Universal Upscaler with base64 image"""
        print(f"[UPSCALE] Using base64 image for Universal Upscaler")
        
        # Check API limits and warn if needed
        max_multiplier = 2.0
        if upscale_factor > max_multiplier:
            print(f"[UPSCALE] Warning: Leonardo.ai only supports up to {max_multiplier}x upscaling. Reducing from {upscale_factor}x to {max_multiplier}x")
            upscale_factor = max_multiplier
        
        # Prepare upscaling request
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        
        # Leonardo.ai Universal Upscaler payload with base64 image
        payload = {
            "inputImage": image_b64,  # Use base64 image directly
            "upscaleMultiplier": upscale_factor,  # API limits: 1-2x only
            "creativityStrength": kwargs.get("creativity_strength", 5),
            "upscalerStyle": kwargs.get("upscaler_style", "CINEMATIC"),  # CINEMATIC, ARTISTIC, etc.
        }
        
        # Add optional parameters if provided
        if kwargs.get("prompt"):
            payload["prompt"] = kwargs.get("prompt")
        if kwargs.get("negative_prompt"):
            payload["negativePrompt"] = kwargs.get("negative_prompt")
        
        print(f"[UPSCALE] Payload: {json.dumps({k: v for k, v in payload.items() if k != 'inputImage'}, indent=2)}")
        print(f"[UPSCALE] Upscaling with multiplier: {upscale_factor}x")
        
        try:
            # Initiate upscaling
            import requests
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/variations/universal-upscaler",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Log detailed error information
            if response.status_code != 200:
                print(f"[ERROR] API Response Status: {response.status_code}")
                print(f"[ERROR] API Response Headers: {dict(response.headers)}")
                try:
                    error_data = response.json()
                    print(f"[ERROR] API Response Body: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"[ERROR] API Response Text: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            upscaling_id = result.get("id") or result.get("variationId")
            print(f"[UPSCALE] Upscaling initiated: {upscaling_id}")
            
            # Poll for completion
            return await self._poll_leonardo_upscale(upscaling_id, headers)
            
        except Exception as e:
            print(f"[ERROR] Leonardo.ai upscaling failed: {e}")
            raise
    
    async def _upload_image_to_leonardo(self, image: Image.Image, api_key: str) -> str:
        """Upload image to Leonardo.ai and return the image ID"""
        print("[UPSCALE] Uploading image to Leonardo.ai...")
        
        # Convert image to bytes
        import io
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        image_bytes = img_buffer.getvalue()
        
        # Step 1: Get presigned URL for upload
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        
        upload_payload = {
            "extension": "png"
        }
        
        try:
            response = requests.post(
                "https://cloud.leonardo.ai/api/rest/v1/init-image",
                headers=headers,
                json=upload_payload,
                timeout=30
            )
            response.raise_for_status()
            
            upload_data = response.json()
            upload_init_image = upload_data.get("uploadInitImage", {})
            image_id = upload_init_image.get("id")
            
            if not image_id:
                raise Exception("No image ID returned from upload init image endpoint")
            
            print(f"[UPSCALE] Got image ID: {image_id}")
            
            # Step 2: Upload the actual image to the presigned URL
            fields = json.loads(upload_init_image.get("fields", "{}"))
            upload_url = upload_init_image.get("url")
            
            files = {'file': image_bytes}
            upload_response = requests.post(upload_url, data=fields, files=files, timeout=30)
            upload_response.raise_for_status()
            
            print(f"[UPSCALE] Image uploaded successfully")
            
            # Wait a moment for the image to be processed
            import asyncio
            print("[UPSCALE] Waiting for image processing...")
            await asyncio.sleep(3)
            
            return image_id
            
        except Exception as e:
            print(f"[ERROR] Failed to upload image to Leonardo.ai: {e}")
            raise
    
    async def _upscale_with_image_id(self, image_id: str, upscale_factor: float, api_key: str, **kwargs) -> Image.Image:
        """Upscale using Leonardo.ai image ID"""
        print(f"[UPSCALE] Starting upscaling with image ID: {image_id}")
        
        # Check API limits and warn if needed
        max_multiplier = 2.0
        if upscale_factor > max_multiplier:
            print(f"[UPSCALE] Warning: Leonardo.ai only supports up to {max_multiplier}x upscaling. Reducing from {upscale_factor}x to {max_multiplier}x")
            upscale_factor = max_multiplier
        
        # Prepare upscaling request
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        
        # Leonardo.ai Universal Upscaler payload
        payload = {
            "inputImage": image_id,  # Use the uploaded image ID
            "upscaleMultiplier": upscale_factor,  # API limits: 1-2x only
            "creativityStrength": kwargs.get("creativity_strength", 5),
            "upscalerStyle": kwargs.get("upscaler_style", "CINEMATIC"),  # CINEMATIC, ARTISTIC, etc.
        }
        
        # Add optional parameters if provided
        if kwargs.get("prompt"):
            payload["prompt"] = kwargs.get("prompt")
        if kwargs.get("negative_prompt"):
            payload["negativePrompt"] = kwargs.get("negative_prompt")
        
        print(f"[UPSCALE] Payload: {json.dumps({k: v for k, v in payload.items()}, indent=2)}")
        print(f"[UPSCALE] Upscaling with multiplier: {upscale_factor}x")
        
        # Retry logic in case image is still processing
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Initiate upscaling
                import requests
                response = requests.post(
                    "https://cloud.leonardo.ai/api/rest/v1/variations/universal-upscaler",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                # Log detailed error information
                if response.status_code != 200:
                    print(f"[ERROR] API Response Status: {response.status_code}")
                    print(f"[ERROR] API Response Headers: {dict(response.headers)}")
                    try:
                        error_data = response.json()
                        print(f"[ERROR] API Response Body: {json.dumps(error_data, indent=2)}")
                        
                        # If it's a "couldn't access image" error and we have retries left, wait and retry
                        if "couldn't access image" in str(error_data) and attempt < max_retries - 1:
                            print(f"[UPSCALE] Image still processing, waiting 5 seconds... (attempt {attempt + 1}/{max_retries})")
                            import asyncio
                            await asyncio.sleep(5)
                            continue
                    except:
                        print(f"[ERROR] API Response Text: {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                upscaling_id = result.get("id") or result.get("variationId")
                print(f"[UPSCALE] Upscaling initiated: {upscaling_id}")
                
                # Poll for completion
                return await self._poll_leonardo_upscale(upscaling_id, headers)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"[ERROR] Leonardo.ai upscaling failed after {max_retries} attempts: {e}")
                    raise
                else:
                    print(f"[UPSCALE] Attempt {attempt + 1} failed, retrying...")
                    continue
    
    async def _poll_leonardo_upscale(self, upscaling_id: str, headers: dict) -> Image.Image:
        """Poll Leonardo.ai upscaling completion"""
        print(f"[UPSCALE] Polling upscaling: {upscaling_id}")
        
        # Use the correct endpoint for checking upscale status
        # Based on Leonardo API, the upscale status is at /variations/{id} or /sd-upscales/{id}
        possible_endpoints = [
            f"https://cloud.leonardo.ai/api/rest/v1/sd-upscales/{upscaling_id}",
            f"https://cloud.leonardo.ai/api/rest/v1/variations/{upscaling_id}",
            f"https://cloud.leonardo.ai/api/rest/v1/upscale/{upscaling_id}",
        ]
        
        current_endpoint_idx = 0
        
        for attempt in range(120):  # Poll for up to 4 minutes (120 * 2 seconds)
            try:
                status_url = possible_endpoints[current_endpoint_idx]
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 404:
                    # Try next endpoint
                    if current_endpoint_idx < len(possible_endpoints) - 1:
                        current_endpoint_idx += 1
                        print(f"[UPSCALE] Trying next endpoint: {possible_endpoints[current_endpoint_idx]}")
                        continue
                    else:
                        # All endpoints failed, wait and retry from first
                        current_endpoint_idx = 0
                        await asyncio.sleep(2)
                        continue
                
                status_response.raise_for_status()
                
                status_data = status_response.json()
                
                # Debug: print full response on first successful call
                if attempt == 0:
                    print(f"[UPSCALE] Debug - Full status response: {json.dumps(status_data, indent=2)}")
                
                # Handle Leonardo's generated_image_variation_generic array structure
                # {"generated_image_variation_generic": [{"status": "PENDING", "url": null, ...}]}
                variation_list = status_data.get("generated_image_variation_generic", [])
                if variation_list and isinstance(variation_list, list) and len(variation_list) > 0:
                    variation_data = variation_list[0]
                    current_status = variation_data.get("status")
                    image_url = variation_data.get("url")
                else:
                    # Fallback to old structure parsing
                    upscale_data = status_data.get("sdUpscaleJob", status_data.get("upscale_job", status_data))
                    current_status = (
                        upscale_data.get("status") if isinstance(upscale_data, dict) else None
                    ) or status_data.get("status")
                    image_url = None
                
                # Log every attempt with status
                print(f"[UPSCALE] Poll attempt {attempt + 1}/120 - Status: {current_status}")
                
                if current_status is None and attempt < 3:
                    print(f"[UPSCALE] Debug - Response keys: {list(status_data.keys())}")
                
                if current_status == "COMPLETE":
                    print(f"[UPSCALE] Upscaling complete! Retrieving image...")
                    
                    # Use URL from variation data if available, otherwise try other locations
                    if not image_url:
                        image_url = (
                            status_data.get("upscaledImage") or
                            status_data.get("url") or
                            status_data.get("imageUrl")
                        )
                    
                    if not image_url:
                        print(f"[UPSCALE] Available keys in status_data: {list(status_data.keys())}")
                        if variation_list and len(variation_list) > 0:
                            print(f"[UPSCALE] Available keys in variation: {list(variation_list[0].keys())}")
                        raise Exception("Upscaling marked as COMPLETE but no image URL found")
                    
                    # Download upscaled image
                    image_response = requests.get(image_url, timeout=30)
                    image_response.raise_for_status()
                    
                    upscaled_image = Image.open(io.BytesIO(image_response.content))
                    print(f"[UPSCALE] Upscaling completed successfully!")
                    return upscaled_image
                
                elif current_status == "FAILED":
                    error_message = (
                        upscale_data.get("errorMessage") or
                        status_data.get("errorMessage") or
                        "Unknown error"
                    )
                    raise Exception(f"Leonardo.ai upscaling failed: {error_message}")
                
                else:
                    await asyncio.sleep(2)  # Wait 2 seconds between polls
                    
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Upscaling poll failed: {e}")
                await asyncio.sleep(2)
        
        # If all polling attempts fail, return a fallback
        print(f"[UPSCALE] Polling failed after 4 minutes. Upscaling may still be processing.")
        raise TimeoutError("Upscaling timed out after 4 minutes - the job may still be processing in Leonardo.ai")
    
    def get_webhook_endpoints(self) -> Dict[str, str]:
        """Get webhook endpoints for supported generators"""
        return {
            "leonardo-api": "/webhook/leonardo/{callback_id}",
            "nano-banana-pro": "/webhook/nano-banana/{callback_id}",  # Future support
            "seedream": "/webhook/seedream/{callback_id}"  # Future support
        }
    
    async def generate_image(self, generator_name: str, prompt: str, **kwargs) -> Image.Image:
        """Generate image using specified modern generator"""
        print(f"[ART] Starting generation with {generator_name}")
        print(f"[NOTE] Prompt: {prompt[:100]}...")
        print(f"[SEARCH] Available generators: {list(self.available_generators.keys())}")
        
        if generator_name not in self.available_generators:
            raise ValueError(f"Generator {generator_name} not available")
        
        generator_info = self.available_generators[generator_name]
        print(f"[SEARCH] Generator info: {generator_info}")
        
        try:
            if generator_name == "leonardo-api":
                return await self.generate_with_leonardo(prompt, **kwargs)
            elif generator_name == "nano-banana-pro":
                return await self.generate_with_nano_banana_pro(prompt, **kwargs)
            elif generator_name == "seedream":
                return await self.generate_with_seedream(prompt, **kwargs)
            elif generator_name == "modal":
                return await self.generate_with_modal(prompt, **kwargs)
            elif generator_name == "midjourney-api":
                return await self.generate_with_midjourney(prompt, **kwargs)
            elif generator_name == "dall-e-3":
                return await self.generate_with_dalle3(prompt, **kwargs)
            else:
                raise Exception(f"Unsupported generator: {generator_name}")
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            print(f"[SEARCH] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def upscale_image(self, generator_name: str = "leonardo-api", **kwargs) -> Image.Image:
        """Upscale image using specified generator"""
        print(f"[UPSCALE] Starting upscaling with {generator_name}")
        
        if generator_name not in self.available_generators:
            raise ValueError(f"Generator {generator_name} not available for upscaling")
        
        try:
            if generator_name == "leonardo-api":
                return await self.upscale_with_leonardo(**kwargs)
            else:
                raise ValueError(f"Generator {generator_name} does not support upscaling")
        except Exception as e:
            print(f"[ERROR] Upscaling failed: {e}")
            print(f"[UPSCALE] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _generate_demo_image(self, generator_name: str, prompt: str, **kwargs) -> Image.Image:
        """Generate a demo image for testing without API keys"""
        print(f"[ART] Demo mode: Generating with {self.available_generators[generator_name]['name']}")
        
        # Create a simple demo image with text
        width = kwargs.get("width", 512)
        height = kwargs.get("height", 512)
        
        # Create a gradient background
        image = Image.new('RGB', (width, height), color=(100, 150, 200))
        
        # Add some visual interest with a simple pattern
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(image)
        
        # Create a gradient effect
        for y in range(height):
            color_value = int(100 + (155 * y / height))
            draw.line([(0, y), (width, y)], fill=(color_value, 150, 200))
        
        # Add text
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Add generator name and prompt
        generator_name_display = self.available_generators[generator_name]['name']
        text_lines = [
            f"{generator_name_display}",
            "Demo Mode",
            f"Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"Prompt: {prompt}",
            "Set API key for real generation"
        ]
        
        y_offset = 50
        for line in text_lines:
            if font:
                # Add text with shadow for better visibility
                draw.text((20, y_offset + 2), line, fill=(0, 0, 0), font=font)
                draw.text((18, y_offset), line, fill=(255, 255, 255), font=font)
            else:
                # Fallback to simple text without font
                draw.text((20, y_offset), line, fill=(255, 255, 255))
            y_offset += 40
        
        # Simulate generation time
        await asyncio.sleep(2)  # Simulate API call time
        
        return image
    
    def get_leonardo_options(self) -> Dict[str, Any]:
        """Get Leonardo.ai specific options for frontend"""
        if "leonardo-api" not in self.available_generators:
            return {}
        
        generator_info = self.available_generators["leonardo-api"]
        return {
            "models": generator_info["models"],
            "preset_styles": generator_info["preset_styles"],
            "quality_levels": generator_info["quality_levels"],
            "aspect_ratios": generator_info["aspect_ratios"],
            "default_settings": {
                "model": "leonardo-diffusion-xl",
                "preset_style": "CREATIVE",
                "quality": "standard",
                "aspect_ratio": "1:1",
                "guidance_scale": 7.5,
                "num_inference_steps": 15
            }
        }
    
    def get_optimal_settings(self, generator_name: str) -> Dict[str, Any]:
        """Get optimal settings for a specific modern generator"""
        generator_info = self.available_generators.get(generator_name, {})
        
        base_settings = {
            "default_steps": 20,
            "max_steps": 50,
            "default_guidance": 7.5,
            "default_resolution": generator_info.get("max_resolution", (1024, 1024))
        }
        
        # Generator-specific optimizations
        if generator_name == "nano-banana-pro":
            return {
                **base_settings,
                "default_steps": 15,
                "max_steps": 30,
                "default_guidance": 6.0,
                "supported_styles": ["realistic", "artistic", "anime", "3d"]
            }
        elif generator_name == "seedream":
            return {
                **base_settings,
                "default_steps": 25,
                "max_steps": 40,
                "default_guidance": 7.0,
                "supported_styles": ["photorealistic", "cinematic", "fantasy", "abstract"]
            }
        elif generator_name == "dall-e-3":
            return {
                **base_settings,
                "default_steps": 1,  # DALL-E 3 doesn't use steps
                "max_steps": 1,
                "default_guidance": 0,  # Not applicable
                "supported_sizes": ["1024x1024", "1792x1024", "1024x1792"]
            }
        elif generator_name == "leonardo-api":
            return {
                **base_settings,
                "default_steps": 15,
                "max_steps": 30,
                "default_guidance": 6.5,
                "supported_presets": ["CREATIVE", "DYNAMIC", "ARTISTIC", "PHOTOGRAPHIC"]
            }
        
        return base_settings
    
    def get_generator_recommendations(self) -> Dict[str, str]:
        """Get recommendations for different use cases"""
        return {
            "speed": "nano-banana-pro - Fastest generation with excellent quality",
            "quality": "dall-e-3 - Best overall quality and natural language understanding",
            "professional": "seedream - Professional-grade results with style control",
            "artistic": "leonardo-api - Great for artistic and creative styles",
            "balance": "nano-banana-pro - Best balance of speed and quality"
        }
