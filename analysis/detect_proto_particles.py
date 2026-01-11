# analysis/detect_proto_particles.py

import json
import sys
from collections import defaultdict

# -----------------------------
# Detection thresholds
# -----------------------------
MIN_LIFETIME = 20        # minimum lifetime (timesteps)
MIN_MEAN_SIZE = 10       # minimum average ξ-cluster size

# -----------------------------
# Load data
# -----------------------------
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

# -----------------------------
# Track clusters by cluster_id
# -----------------------------
cluster_birth = {}                  # cid -> birth time
cluster_last_seen = {}              # cid -> last time seen
cluster_sizes_over_time = defaultdict(list)  # cid -> [sizes]

for r in rewrites:
    t = r["time"]
    cluster_sizes = r.get("cluster_sizes", {})

    for cid, size in cluster_sizes.items():
        if size <= 0:
            continue

        # first appearance
        if cid not in cluster_birth:
            cluster_birth[cid] = t

        cluster_last_seen[cid] = t
        cluster_sizes_over_time[cid].append(size)

# -----------------------------
# Compute statistics
# -----------------------------
lifetimes = []
mean_sizes = []

for cid, sizes in cluster_sizes_over_time.items():
    birth = cluster_birth[cid]
    death = cluster_last_seen[cid]
    lifetime = death - birth

    if lifetime <= 0:
        continue

    mean_size = sum(sizes) / len(sizes)

    lifetimes.append(lifetime)
    mean_sizes.append(mean_size)

# -----------------------------
# Aggregate results
# -----------------------------
total_objects = len(lifetimes)
mean_life = sum(lifetimes) / total_objects if lifetimes else 0.0
max_life = max(lifetimes) if lifetimes else 0
mean_cluster_size = (
    sum(mean_sizes) / len(mean_sizes) if mean_sizes else 0.0
)

# -----------------------------
# Report
# -----------------------------
print("\n=== Proto-Particle Detection ===")
print(f"Total proto-objects     : {total_objects}")
print(f"Mean lifetime           : {mean_life:.2f}")
print(f"Max lifetime            : {max_life}")
print(f"Mean ξ-cluster size     : {mean_cluster_size:.2f}")

if mean_life >= MIN_LIFETIME and mean_cluster_size >= MIN_MEAN_SIZE:
    print("✅ Proto-particles detected")
elif mean_life >= 5:
    print("⚠ Marginal proto-objects")
else:
    print("❌ No proto-particles (noise)")