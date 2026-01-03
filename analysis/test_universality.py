# analysis/test_universality.py
import json
import numpy as np

def load_metrics(path):
    with open(path) as f:
        return json.load(f)

variants = [
    "baseline",
    "variant_1",
    "variant_2",
    "variant_3",
    "variant_4",
]

results = []

for v in variants:
    cone = load_metrics(f"{v}/lorentz_cone.json")
    eom  = load_metrics(f"{v}/effective_eom.json")
    part = load_metrics(f"{v}/particle_stats.json")

    results.append({
        "variant": v,
        "v_max": cone["v_max"],
        "c2": eom["c_omega_sq"],
        "m2": eom["m_omega_sq"],
        "violations": cone["violations"],
        "mean_lifetime": part["mean_lifetime"]
    })

print("\n=== Step 21: Universality Test ===")
for r in results:
    print(r)