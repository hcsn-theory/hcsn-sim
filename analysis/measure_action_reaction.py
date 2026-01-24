# analysis/measure_action_reaction.py

import json
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python3 -m analysis.measure_action_reaction <interaction_json>")
    sys.exit(1)

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

cluster_sizes = defaultdict(list)
cluster_times = defaultdict(list)

for r in rewrites:
    t = r["time"]
    sizes = r.get("cluster_sizes", {})
    for cid, size in sizes.items():
        if size > 0:
            cluster_sizes[cid].append(size)
            cluster_times[cid].append(t)

if len(cluster_sizes) < 2:
    print("❌ Need at least two clusters")
    sys.exit(0)

clusters = sorted(
    cluster_sizes.keys(),
    key=lambda c: cluster_times[c][-1] - cluster_times[c][0],
    reverse=True
)

A, B = clusters[:2]

Δξ_A = cluster_sizes[A][-1] - cluster_sizes[A][0]
Δξ_B = cluster_sizes[B][-1] - cluster_sizes[B][0]

numerator = Δξ_A + Δξ_B
denominator = abs(Δξ_A) + abs(Δξ_B)

R_env = numerator / denominator if denominator > 0 else 0.0

print("\n=== Action–Reaction Diagnostic ===")
print(f"Δξ_A = {Δξ_A}")
print(f"Δξ_B = {Δξ_B}")
print(f"Δξ_A + Δξ_B = {numerator}")
print(f"Environment ratio R_env = {R_env:.4f}")

if abs(R_env) < 0.05:
    print("✅ Approximately action–reaction symmetric")
else:
    print("⚠ Interaction mediated by environment (Ω-field)")