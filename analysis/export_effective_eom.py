# analysis/export_effective_eom.py
import json

with open("analysis/effective_eom.json") as f:
    eom = json.load(f)

with open("analysis/effective_eom.json", "w") as f:
    json.dump(eom, f, indent=2)

print("Saved  effective_eom.json")