import sys

with open('leonardo_dicts.txt', 'r', encoding='utf-8') as f:
    text = f.read()
    parts = text.split('SETUP:\n')
    mapping_str = parts[0].replace('MAPPING:\n', '')
    setup_str = parts[1]

with open('modern_generators.py', 'r', encoding='utf-8') as f:
    py_text = f.read()

marker1_start = '        mapping = {\n'
marker1_end = '        }\n\n        # Fallback: try to infer by modelId pattern'

idx1 = py_text.find(marker1_start)
if idx1 != -1:
    idx1 += len(marker1_start)
    idx2 = py_text.find(marker1_end, idx1)
    if idx2 != -1:
        py_text = py_text[:idx1] + mapping_str + py_text[idx2:]
        print("Replaced mapping")
    else:
        print("Could not find marker1_end")
else:
    print("Could not find marker1_start")

marker2_start = '            "models": {\n'
marker2_end = '            },\n            "preset_styles": ['

idx1_m2 = py_text.find(marker2_start)
if idx1_m2 != -1:
    idx1_m2 += len(marker2_start)
    idx2_m2 = py_text.find(marker2_end, idx1_m2)
    if idx2_m2 != -1:
        # Note: setup_str has an indent that mostly matches, just need to ensure the end fits.
        py_text = py_text[:idx1_m2] + setup_str.lstrip() + "\n" + py_text[idx2_m2:]
        print("Replaced setup")
    else:
        print("Could not find marker2_end")
else:
    print("Could not find marker2_start")

with open('modern_generators.py', 'w', encoding='utf-8') as f:
    f.write(py_text)
print("Done writing")
