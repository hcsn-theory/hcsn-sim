# analysis/measure_interaction_strength.py

import json
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_interaction_strength <interaction_json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

# ----------------------------------------
# Accumulate cluster sizes over time
# ----------------------------------------
cluster_sizes = defaultdict(list)
cluster_times = defaultdict(list)

for r in rewrites:
    t = r["time"]
    sizes = r.get("cluster_sizes", {})

    for cid, size in sizes.items():
        if size <= 0:
            continue
        cluster_sizes[cid].append(size)
        cluster_times[cid].append(t)

if len(cluster_sizes) < 2:
    print("❌ Fewer than two clusters detected")
    sys.exit(0)

# ----------------------------------------
# Pick two longest-lived clusters
# ----------------------------------------
clusters = sorted(
    cluster_sizes.keys(),
    key=lambda c: cluster_times[c][-1] - cluster_times[c][0],
    reverse=True
)

A, B = clusters[:2]

# ----------------------------------------
# Compute interaction strength
# ----------------------------------------
def growth(cid):
    return cluster_sizes[cid][-1] - cluster_sizes[cid][0]

def lifetime(cid):
    return cluster_times[cid][-1] - cluster_times[cid][0]

Δξ_A = growth(A)
Δξ_B = growth(B)
τ = min(lifetime(A), lifetime(B))

F_AB = (Δξ_A - Δξ_B) / τ if τ > 0 else 0.0

# ----------------------------------------
# Report
# ----------------------------------------
print("\n=== Interaction Strength (Scalar) ===")
print(f"Cluster A ID        : {A}")
print(f"Cluster B ID        : {B}")
print(f"Δξ_A                : {Δξ_A}")
print(f"Δξ_B                : {Δξ_B}")
print(f"Coexistence τ       : {τ}")
print(f"Interaction F_AB    : {F_AB:.4f}")

if abs(F_AB) > 0.01:
    print("✅ Non-zero interaction strength detected")
else:
    print("⚠ Interaction weak or marginal")