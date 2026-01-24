import json
import sys
from collections import defaultdict

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

xi_log = data.get("xi_current_log", [])
rewrites = data.get("rewrite_history", [])

# Identify two main clusters
cluster_ids = set()
for r in rewrites:
    for cid in r.get("cluster_ids", []):
        cluster_ids.add(cid)

cluster_ids = sorted(cluster_ids)
if len(cluster_ids) < 2:
    print("❌ Need ≥2 clusters")
    sys.exit(0)

A, B = cluster_ids[:2]

J_A = 0.0
J_B = 0.0
J_env = 0.0

for entry in xi_log:
    delta = entry["delta_xi"]
    cids = entry.get("cluster_ids", [])

    for v, dxi in delta.items():
        if A in cids:
            J_A += dxi
        elif B in cids:
            J_B += dxi
        else:
            J_env += dxi

print("\n=== ξ-Current Balance (C8A) ===")
print(f"J_A     : {J_A:.2f}")
print(f"J_B     : {J_B:.2f}")
print(f"J_env   : {J_env:.2f}")
print(f"ΣJ      : {J_A + J_B + J_env:.2f}")

if abs(J_A + J_B + J_env) < 1e-6:
    print("✅ ξ-current conserved")
else:
    print("⚠ ξ-current not closed → refine current definition")