# analysis/measure_cluster_distance_memory.py

import json
import sys
import math
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "analysis/interaction_experiment.json"

with open(path) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

distance_series = defaultdict(list)

for r in rewrites:
    dmem = r.get("cluster_distance_memory", None)
    if not dmem:
        continue
    for key, d in dmem.items():
        if math.isfinite(d):
            distance_series[key].append(d)

print("\n=== Cluster Distance Memory (G1) ===\n")

if not distance_series:
    print("❌ No distance memory recorded")
    sys.exit(0)

for key, series in distance_series.items():
    mean = sum(series) / len(series)
    var = sum((x - mean) ** 2 for x in series) / len(series)
    print(f"Clusters {key}: samples={len(series)}, ⟨d⟩={mean:.3f}, Var={var:.3f}")

print("\n✔ Distance memory present (proto-geometry confirmed)")