# analysis/measure_shielding_effect.py

import json
import sys

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_shielding_effect <interaction.json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]

cluster_flux = {}
cluster_overlap = {}

for r in rewrites:
    touched = set(r.get("xi_support", []))
    clusters = r.get("cluster_ids", [])

    for cid in clusters:
        cluster_flux[cid] = cluster_flux.get(cid, 0) + len(touched)

    for a in clusters:
        for b in clusters:
            if a >= b:
                continue
            cluster_overlap[(a, b)] = cluster_overlap.get((a, b), 0) + len(touched)

print("\n=== Shielding & Effective Distance (C4) ===")

for (a, b), overlap in cluster_overlap.items():
    fa = cluster_flux.get(a, 1)
    fb = cluster_flux.get(b, 1)

    shielding = overlap / min(fa, fb)

    print(f"Clusters {a}-{b}: shielding={shielding:.3f}")

    if shielding > 0.2:
        print("  ✅ Strong mutual shielding")
    elif shielding > 0.05:
        print("  ⚠ Weak interaction")
    else:
        print("  ❌ Effectively distant")