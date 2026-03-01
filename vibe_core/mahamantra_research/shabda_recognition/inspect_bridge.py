import json

d = json.load(open("vibe_core/mahamantra/data/shabda_bridge.json"))
syls = d["syllables"]
print(f"Syllables: {len(syls)}")
print(f"Type: {type(syls)}")
if isinstance(syls, dict):
    for k, v in syls.items():
        print(f"  {k}: {v}")
elif isinstance(syls, list):
    for i, s in enumerate(syls):
        print(f"  [{i}]: {s}")
