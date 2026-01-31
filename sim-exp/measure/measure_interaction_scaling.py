# analysis/measure_interaction_scaling.py

import json
import sys
import math

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_interaction_scaling <interaction.json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]

# --- aggregate per-cluster ---
cluster_sizes = {}
cluster_flux = {}

for r in rewrites:
    sizes = r.get("cluster_sizes", {})
    xi_support = r.get("xi_support", [])

    for cid, size in sizes.items():
        cluster_sizes.setdefault(cid, []).append(size)
        cluster_flux[cid] = cluster_flux.get(cid, 0) + len(xi_support)

# --- compute means ---
results = []

for cid in cluster_sizes:
    mean_size = sum(cluster_sizes[cid]) / len(cluster_sizes[cid])
    flux = cluster_flux.get(cid, 0)

    if mean_size > 0 and flux > 0:
        results.append((cid, mean_size, flux))

# --- log-log scaling ---
print("\n=== Interaction Scaling (C2) ===")

for cid, size, flux in results:
    print(f"Cluster {cid}: ⟨|C|⟩={size:.2f}, Flux={flux}")

if len(results) >= 2:
    (c1, s1, f1), (c2, s2, f2) = results[:2]

    alpha = math.log(f1 / f2) / math.log(s1 / s2)

    print(f"\nEstimated scaling exponent α ≈ {alpha:.3f}")

    if 0.8 <= alpha <= 1.2:
        print("✅ Linear mass-like interaction")
    elif alpha < 0.8:
        print("⚠ Sublinear (screened interaction)")
    else:
        print("⚠ Superlinear (instability)")
else:
    print("❌ Insufficient clusters for scaling")