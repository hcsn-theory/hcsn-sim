# analysis/export_lorentz_cone.py
import json

with open("analysis/signal_speed_samples.json") as f:
    samples = json.load(f)

speeds = [1/d["dt"] for d in samples if d["influence"] == 1]

data = {
    "v_max": max(speeds),
    "mean": sum(speeds)/len(speeds),
    "violations": sum(1 for v in speeds if v > max(speeds))
}

with open("analysis/lorentz_cone.json", "w") as f:
    json.dump(data, f, indent=2)

print("Saved  lorentz_cone.json")