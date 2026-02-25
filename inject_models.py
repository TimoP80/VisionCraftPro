import os

with open("leonardo_dicts.txt", "r") as f:
    content = f.read()

parts = content.split("SETUP:\n")
mapping_str = parts[0].replace("MAPPING:\n", "")
setup_str = parts[1]

with open("modern_generators.py", "r") as f:
    py_lines = f.readlines()

out_lines = []
in_mapping = False
in_setup = False
skip_next = False

for line in py_lines:
    if skip_next:
        skip_next = False
        continue

    # Injection point 1: mapping dict
    if "mapping = {" in line and getattr(globals(), 'in_mapping_scope', False):
        out_lines.append(line)
        out_lines.append(mapping_str + "\n")
        in_mapping = True
        continue
    
    # We set a flag when we enter the mapping scope
    if "# Explicit mappings from Leonardo docs" in line:
        globals()['in_mapping_scope'] = True
        out_lines.append(line)
        continue

    if in_mapping and "# FLUX models (V1)" in line:
        in_mapping = False
        globals()['in_mapping_scope'] = False
        out_lines.append(line)
        continue
        
    if in_mapping:
        continue

    # Injection point 2: models dict
    if '"models": {' in line and getattr(globals(), 'in_setup_scope', False):
        out_lines.append(line)
        out_lines.append(setup_str.lstrip() + "\n")
        in_setup = True
        continue
        
    # We set a flag when we enter the setup scope
    if '"features": ["text-to-image", "fine-tuned-models", "texture-generation"],' in line:
        globals()['in_setup_scope'] = True
        out_lines.append(line)
        continue
        
    if in_setup and '"preset_styles": [' in line:
        in_setup = False
        globals()['in_setup_scope'] = False
        out_lines.append("            },\n")
        out_lines.append(line)
        continue
        
    if in_setup:
        continue
        
    out_lines.append(line)

with open("modern_generators_injected.py", "w") as f:
    f.writelines(out_lines)

print("Injected content into modern_generators_injected.py")
