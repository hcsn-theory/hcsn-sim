import json
import sys
from collections import defaultdict

# -----------------------------
# Parameters (tune later)
# -----------------------------
XI_THRESHOLD = 1e-6      # what counts as ξ-active
OVERLAP_ALPHA = 0.5      # identity overlap threshold

# -----------------------------
# Load data
# -----------------------------
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]

# -----------------------------
# Extract ξ-active sets per time
# -----------------------------
xi_sets = defaultdict(set)

for r in rewrites:
    t = r["time"]
    xi_support = r.get("xi_support", [])
    for v in xi_support:
        xi_sets[t].add(v)

times = sorted(xi_sets.keys())

# -----------------------------
# Cluster identity tracking
# -----------------------------
clusters = {}      # cluster_id -> set(vertices)
cluster_birth = {}
cluster_death = {}

next_cluster_id = 0

def overlap(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

# -----------------------------
# Time evolution
# -----------------------------
for i, t in enumerate(times):
    current = xi_sets[t]
    matched = set()

    if i == 0:
        clusters[0] = current
        cluster_birth[0] = t
        next_cluster_id = 1
        continue

    prev_t = times[i - 1]
    prev_clusters = {
        cid: verts for cid, verts in clusters.items()
        if cluster_death.get(cid) is None
    }

    used_prev = set()

    for cid, verts in prev_clusters.items():
        ov = overlap(verts, current)
        if ov >= OVERLAP_ALPHA:
            clusters[cid] = current
            matched.add(cid)
            used_prev.add(cid)

    if not matched and current:
        clusters[next_cluster_id] = current
        cluster_birth[next_cluster_id] = t
        next_cluster_id += 1

    for cid in prev_clusters:
        if cid not in used_prev and cid not in cluster_death:
            cluster_death[cid] = t

# Close remaining clusters
final_time = times[-1]
for cid in clusters:
    if cid not in cluster_death:
        cluster_death[cid] = final_time

# -----------------------------
# Report statistics
# -----------------------------
lifetimes = []
sizes = []

for cid in clusters:
    birth = cluster_birth.get(cid)
    death = cluster_death.get(cid)
    if birth is None or death is None:
        continue
    lifetimes.append(death - birth)
    sizes.append(len(clusters[cid]))

print("\n=== Proto-Particle Detection ===")
print(f"Total clusters detected : {len(lifetimes)}")
print(f"Mean lifetime           : {sum(lifetimes)/len(lifetimes):.2f}")
print(f"Max lifetime            : {max(lifetimes)}")
print(f"Mean cluster size       : {sum(sizes)/len(sizes):.2f}")

# Classification
if max(lifetimes) < 20:
    print("❌ No proto-particles (noise)")
elif sum(lifetimes)/len(lifetimes) < 50:
    print("⚠ Marginal proto-objects")
else:
    print("✅ Proto-particles detected")