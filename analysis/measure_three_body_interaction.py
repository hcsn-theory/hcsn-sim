# analysis/measure_three_body_interaction.py

import json
import sys

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_three_body_interaction <interaction.json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]

cluster_flux = {}
cluster_birth = {}

for r in rewrites:
    t = r["time"]
    sizes = r.get("cluster_sizes", {})
    xi_support = r.get("xi_support", [])

    for cid in sizes:
        cluster_flux[cid] = cluster_flux.get(cid, 0) + len(xi_support)
        cluster_birth.setdefault(cid, t)

clusters = sorted(cluster_flux)

print("\n=== Three-Body Interaction Test (C3) ===")

if len(clusters) < 3:
    print("❌ Need ≥3 clusters")
    sys.exit(0)

A, B, C = clusters[:3]

FAB = cluster_flux[A] + cluster_flux[B]
FAC = cluster_flux[A] + cluster_flux[C]
FABC = cluster_flux[A] + cluster_flux[B] + cluster_flux[C]

delta = FABC - (FAB + FAC)

print(f"ΔF_A (non-additivity) = {delta}")

if abs(delta) < 1e-6:
    print("⚠ Additive (unlikely for emergent force)")
elif delta < 0:
    print("✅ Screening / competition detected")
else:
    print("⚠ Cooperative amplification")