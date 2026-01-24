import json
from collections import defaultdict

path = "analysis/interaction_experiment.json"

with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]

# Track per-time cluster info
cluster_sizes = defaultdict(list)
cluster_times = defaultdict(list)

for r in rewrites:
    t = r["time"]
    sizes = r.get("cluster_sizes", {})
    for cid, size in sizes.items():
        cluster_sizes[cid].append(size)
        cluster_times[cid].append(t)

# Pairwise interaction signal
cids = list(cluster_sizes.keys())
if len(cids) < 2:
    print("Less than two clusters — no interaction to measure")
    exit()

c1, c2 = cids[:2]

sizes_1 = cluster_sizes[c1]
sizes_2 = cluster_sizes[c2]

# Simple correlation proxy
def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

print("\n=== Interaction Diagnostics ===")
print(f"Cluster A mean size: {mean(sizes_1):.2f}")
print(f"Cluster B mean size: {mean(sizes_2):.2f}")

# Growth comparison
growth_1 = sizes_1[-1] - sizes_1[0]
growth_2 = sizes_2[-1] - sizes_2[0]

print(f"Cluster A growth: {growth_1}")
print(f"Cluster B growth: {growth_2}")

print(
    f"Net ξ change A: {sizes_1[-1] - sizes_1[0]}, "
    f"B: {sizes_2[-1] - sizes_2[0]}"
)

if abs(growth_1 - growth_2) > 0.1 * max(growth_1, growth_2):
    print("⚠ Asymmetric growth detected → interaction candidate")
else:
    print("✓ No strong growth asymmetry")
    
