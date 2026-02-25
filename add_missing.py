with open('modern_generators.py', 'r', encoding='utf-8') as f:
    text = f.read()

mapping_injection = """
            # Special Aliases and V2 Models
            "universal": {"name": "Universal Enhanced", "id": "6bef9f1b-713b-4271-9231-ef9090632332", "api_version": "v1", "endpoint": "generations"},
            "6bef9f1b-713b-4271-9231-ef9090632332": {"name": "Universal Enhanced", "id": "6bef9f1b-713b-4271-9231-ef9090632332", "api_version": "v1", "endpoint": "generations"},
            "gemini-image-2": {"name": "Nano Banana Pro", "id": "gemini-image-2", "api_version": "v2", "endpoint": "generations"},
            "flux-pro-2.0": {"name": "FLUX.2 Pro", "id": "flux-pro-2.0", "api_version": "v2", "endpoint": "generations"},
"""

if '        }\n\n        # Fallback: try to infer by modelId pattern' in text:
    text = text.replace('        }\n\n        # Fallback: try to infer by modelId pattern', mapping_injection + '        }\n\n        # Fallback: try to infer by modelId pattern')

setup_injection = """
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
"""

if '            },\n            "preset_styles": [' in text:
    text = text.replace('            },\n            "preset_styles": [', setup_injection + '            },\n            "preset_styles": [')

with open('modern_generators.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Added manual overrides back.')
