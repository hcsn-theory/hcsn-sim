# analysis/measure_omega_gradient.py

import json
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_omega_gradient <interaction_json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

cluster_omega_boundary = defaultdict(list)
cluster_sizes = defaultdict(list)

for r in rewrites:
    sizes = r.get("cluster_sizes", {})
    omegas = r.get("cluster_omega", {})

    for cid, size in sizes.items():
        if cid in omegas:
            cluster_sizes[cid].append(size)
            cluster_omega_boundary[cid].append(omegas[cid])

clusters = list(cluster_sizes.keys())
if len(clusters) < 2:
    print("❌ Need at least two clusters")
    sys.exit(0)

print("\n=== Ω Gradient Interaction Test ===")

for cid in clusters[:2]:
    if len(cluster_omega_boundary[cid]) < 2:
        continue

    Δξ = cluster_sizes[cid][-1] - cluster_sizes[cid][0]
    Ω_mean = sum(cluster_omega_boundary[cid]) / len(cluster_omega_boundary[cid])
    Ω_fluct = max(cluster_omega_boundary[cid]) - min(cluster_omega_boundary[cid])

    print(f"\nCluster {cid}")
    print(f"Δξ              = {Δξ}")
    print(f"⟨Ω⟩_boundary     = {Ω_mean:.6f}")
    print(f"Ω fluctuation   = {Ω_fluct:.6f}")

    if Ω_fluct > 0 and abs(Δξ) > 0:
        print("✅ External Ω gradient detected")
    else:
        print("❌ No Ω gradient signal")