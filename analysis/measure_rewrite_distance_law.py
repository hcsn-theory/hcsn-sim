import json
import sys
from collections import defaultdict

# ---------------------------------------
# Usage
# ---------------------------------------
if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_rewrite_distance_law <interaction_json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

# ---------------------------------------
# Collect rewrite-touch sets & sizes
# ---------------------------------------
cluster_rewrites = defaultdict(set)
cluster_sizes = defaultdict(list)

for step_index, r in enumerate(rewrites):
    cluster_ids = r.get("cluster_ids", [])
    sizes = r.get("cluster_sizes", {})

    # Track rewrite touch
    for cid in cluster_ids:
        cluster_rewrites[cid].add(step_index)

    # Track size evolution
    for cid, size in sizes.items():
        if size > 0:
            cluster_sizes[cid].append(size)

cluster_ids = sorted(cluster_rewrites.keys())

if len(cluster_ids) < 2:
    print("❌ Less than two clusters detected")
    sys.exit(0)

A, B = cluster_ids[:2]

R_A = cluster_rewrites[A]
R_B = cluster_rewrites[B]

# ---------------------------------------
# Rewrite-distance
# ---------------------------------------
intersection = R_A & R_B
union = R_A | R_B

if not union:
    print("❌ No rewrite overlap data")
    sys.exit(0)

rewrite_distance = 1.0 - len(intersection) / len(union)

# ---------------------------------------
# Interaction strength
# ---------------------------------------
sizes_A = cluster_sizes.get(A, [])
sizes_B = cluster_sizes.get(B, [])

# Require at least two data points per cluster
if len(sizes_A) < 2 or len(sizes_B) < 2:
    print("❌ Insufficient cluster size history (sparse by design)")
    sys.exit(0)

delta_A = sizes_A[-1] - sizes_A[0]
delta_B = sizes_B[-1] - sizes_B[0]
tau = min(len(sizes_A), len(sizes_B))

interaction_strength = abs(delta_A - delta_B) / max(tau, 1)

# ---------------------------------------
# Report
# ---------------------------------------
print("\n=== Rewrite Distance Interaction Law ===")
print(f"Cluster A ID             : {A}")
print(f"Cluster B ID             : {B}")
print(f"Rewrites touching A      : {len(R_A)}")
print(f"Rewrites touching B      : {len(R_B)}")
print(f"Shared rewrites          : {len(intersection)}")
print(f"Rewrite-distance d_AB    : {rewrite_distance:.4f}")
print(f"Δξ_A                     : {delta_A}")
print(f"Δξ_B                     : {delta_B}")
print(f"Interaction strength F   : {interaction_strength:.6f}")

if rewrite_distance < 1.0 and interaction_strength > 0:
    print("✅ Interaction decreases with rewrite separation (candidate law)")
else:
    print("⚠ No clear distance dependence")