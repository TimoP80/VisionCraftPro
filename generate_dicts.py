import json

data = json.load(open("clean_models.json"))
models = data.get("custom_models", [])

mapping_str = ""
setup_str = ""

for m in models:
    model_id = m["id"]
    name = m["name"]
    desc = m.get("description", "").replace('"', '\\"')
    # Create a nice key: lowercase, replace spaces with hyphen, remove quotes/parentheses
    key = name.lower().replace(" ", "-").replace(".", "-").replace("(", "").replace(")", "").replace("'", "")

    # For mapping
    mapping_str += f'            "{key}": {{"name": "{name}", "id": "{model_id}", "api_version": "v1", "endpoint": "generations"}},\n'
    mapping_str += f'            "{model_id}": {{"name": "{name}", "id": "{model_id}", "api_version": "v1", "endpoint": "generations"}},\n'

    # For setup
    setup_str += f'''
                "{key}": {{
                    "id": "{model_id}",
                    "name": "{name}",
                    "description": "{desc}",
                    "max_resolution": (1024, 1024),
                    "aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                    "note": "Official Leonardo model"
                }},'''

with open("leonardo_dicts.txt", "w") as f:
    f.write("MAPPING:\n")
    f.write(mapping_str)
    f.write("\nSETUP:\n")
    f.write(setup_str)

print("Done generating leonardo_dicts.txt")
