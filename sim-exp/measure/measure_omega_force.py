# analysis/measure_omega_force.py

import json
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_omega_force <interaction_json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

# --- collect per-cluster time series ---
cluster_omega = defaultdict(list)
cluster_size = defaultdict(list)

for r in rewrites:
    sizes = r.get("cluster_sizes", {})
    omegas = r.get("cluster_omega", {})

    for cid in sizes:
        if cid in omegas:
            cluster_size[cid].append(sizes[cid])
            cluster_omega[cid].append(omegas[cid])

if len(cluster_size) < 2:
    print("❌ Need at least two clusters")
    sys.exit(0)

clusters = list(cluster_size.keys())[:2]

print("\n=== Ω–ξ Interaction Test ===")

for cid in clusters:
    if len(cluster_size[cid]) < 2:
        continue

    Δξ = cluster_size[cid][-1] - cluster_size[cid][0]
    ΔΩ = cluster_omega[cid][-1] - cluster_omega[cid][0]

    ratio = Δξ / ΔΩ if abs(ΔΩ) > 1e-6 else float("inf")

    print(f"\nCluster {cid}")
    print(f"Δξ = {Δξ}")
    print(f"ΔΩ = {ΔΩ:.6f}")
    print(f"ξ/Ω coupling ≈ {ratio:.3f}")

    if abs(ΔΩ) > 0 and abs(Δξ) > 0:
        print("✅ Ω–ξ coupling detected")
    else:
        print("❌ No Ω–ξ coupling")