# analysis/measure_single_particle_flux.py

import json
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_single_particle_flux <json>")
    sys.exit(1)

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

# cluster_id → cumulative size proxy
cluster_flux = defaultdict(int)
cluster_lifetime = defaultdict(int)

for r in rewrites:
    sizes = r.get("cluster_sizes", {})
    for cid, size in sizes.items():
        cluster_flux[cid] += size
        cluster_lifetime[cid] += 1

if not cluster_flux:
    print("❌ No proto-particles detected")
    sys.exit(0)

cid = max(cluster_flux, key=lambda c: cluster_flux[c])

print("\n=== Single Proto-Particle Flux (Control) ===")
print(f"Cluster ID        : {cid}")
print(f"Total flux proxy  : {cluster_flux[cid]}")
print(f"Lifetime τ        : {cluster_lifetime[cid]}")
print(f"Mean flux rate    : {cluster_flux[cid]/cluster_lifetime[cid]:.4f}")
print("✅ Control baseline established")