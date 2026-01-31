# analysis/measure_bound_state.py

import json
import sys
import statistics

WINDOW = 500

def main(path):
    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])

    cluster_sizes_ts = {}

    for r in rewrites:
        t = r["time"]
        sizes = r.get("cluster_sizes", {})
        for cid, size in sizes.items():
            cluster_sizes_ts.setdefault(cid, []).append((t, size))

    if len(cluster_sizes_ts) < 2:
        print("❌ Need ≥2 clusters for bound state test")
        return

    ids = sorted(cluster_sizes_ts.keys())[:2]
    A, B = ids

    sizes_A = [s for _, s in cluster_sizes_ts[A][-WINDOW:]]
    sizes_B = [s for _, s in cluster_sizes_ts[B][-WINDOW:]]

    combined = [a + b for a, b in zip(sizes_A, sizes_B)]

    var_A = statistics.variance(sizes_A)
    var_B = statistics.variance(sizes_B)
    var_combined = statistics.variance(combined)

    print("\n=== Bound State Diagnostic (C6) ===")
    print(f"Var(A)        : {var_A:.2f}")
    print(f"Var(B)        : {var_B:.2f}")
    print(f"Var(A+B)      : {var_combined:.2f}")

    if var_combined < min(var_A, var_B):
        print("✅ Bound-state-like stabilization detected")
    else:
        print("❌ No bound state")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_bound_state <json>")
        sys.exit(1)
    main(sys.argv[1])