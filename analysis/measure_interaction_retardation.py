# analysis/measure_interaction_retardation.py

import json
import sys
import numpy as np
from collections import defaultdict

MAX_LAG = 200  # steps

def main(path):
    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])

    # --- build time series of cluster sizes ---
    cluster_ts = defaultdict(dict)

    for r in rewrites:
        t = r["time"]
        sizes = r.get("cluster_sizes", {})
        for cid, size in sizes.items():
            cluster_ts[cid][t] = size

    if len(cluster_ts) < 2:
        print("❌ Need ≥2 clusters for retardation test")
        return

    ids = sorted(cluster_ts.keys())[:2]
    A, B = ids

    times = sorted(set(cluster_ts[A]) & set(cluster_ts[B]))

    if len(times) < MAX_LAG + 10:
        print("❌ Insufficient overlap history")
        return

    series_A = np.array([cluster_ts[A][t] for t in times])
    series_B = np.array([cluster_ts[B][t] for t in times])

    dA = np.diff(series_A)
    dB = np.diff(series_B)

    correlations = {}

    for lag in range(0, MAX_LAG):
        if lag >= len(dA):
            break
        corr = np.corrcoef(dA[:-lag or None], dB[lag:])[0, 1]
        correlations[lag] = corr

    best_lag = max(correlations, key=lambda k: abs(correlations[k]))
    best_corr = correlations[best_lag]

    print("\n=== Interaction Retardation (C5) ===")
    print(f"Best lag τ        : {best_lag}")
    print(f"Correlation       : {best_corr:.4f}")

    if best_lag > 0 and abs(best_corr) > 0.2:
        print("✅ Finite interaction delay detected")
    elif best_lag == 0:
        print("⚠ Instantaneous or unresolved interaction")
    else:
        print("❌ No causal signal")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_interaction_retardation <json>")
        sys.exit(1)
    main(sys.argv[1])