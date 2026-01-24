# analysis/measure_interaction_vs_distance.py

import json
from collections import defaultdict

PATH = "analysis/interaction_experiment.json"

with open(PATH) as f:
    data = json.load(f)

rewrites = data.get("rewrite_history", [])

# --------------------------------------------------
# Track coexisting clusters over time
# --------------------------------------------------
time_clusters = {}

for r in rewrites:
    t = r["time"]
    sizes = r.get("cluster_sizes", {})

    # keep only steps with >= 2 clusters
    if len(sizes) >= 2:
        time_clusters[t] = sizes

if not time_clusters:
    print("❌ No interaction data available")
    exit(0)

# --------------------------------------------------
# Extract size evolution vs time
# --------------------------------------------------
cluster_time_series = defaultdict(list)

for t, sizes in time_clusters.items():
    for cid, size in sizes.items():
        cluster_time_series[cid].append((t, size))

# --------------------------------------------------
# Simple interaction-distance proxy
# (temporal overlap + growth correlation)
# --------------------------------------------------
print("\n=== Interaction vs Distance (Proxy) ===")

for cid, series in cluster_time_series.items():
    times, sizes = zip(*series)

    growth = sizes[-1] - sizes[0]
    print(
        f"Cluster {cid}: "
        f"lifetime={times[-1] - times[0]}, "
        f"growth={growth}, "
        f"mean_size={sum(sizes)/len(sizes):.2f}"
    )

print("\n⚠ Distance metric not yet geometric")
print("✔ Using coexistence + correlated growth as interaction proxy")