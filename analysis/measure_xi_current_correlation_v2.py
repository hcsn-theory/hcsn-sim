# analysis/measure_xi_current_correlation_v2.py

import json
import sys
import math

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def std(xs):
    m = mean(xs)
    return math.sqrt(mean([(x - m) ** 2 for x in xs]))

def covariance(xs, ys):
    mx = mean(xs)
    my = mean(ys)
    return mean([(x - mx) * (y - my) for x, y in zip(xs, ys)])

def main(path):
    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])
    if not rewrites:
        print("❌ No rewrite history")
        return

    # Identify clusters globally
    cluster_ids = set()
    for r in rewrites:
        cluster_ids.update(r.get("cluster_sizes", {}).keys())

    if len(cluster_ids) < 2:
        print("❌ Need ≥2 clusters")
        return

    A, B = sorted(cluster_ids)[:2]

    J_A = []
    J_B = []

    prev_sizes = None

    for r in rewrites:
        sizes = r.get("cluster_sizes", {})
        if prev_sizes is None:
            prev_sizes = sizes
            continue

        JA = sizes.get(A, 0) - prev_sizes.get(A, 0)
        JB = sizes.get(B, 0) - prev_sizes.get(B, 0)

        J_A.append(JA)
        J_B.append(JB)

        prev_sizes = sizes

    if len(J_A) < 10:
        print("❌ Insufficient data")
        return

    cov = covariance(J_A, J_B)
    sA = std(J_A)
    sB = std(J_B)
    corr = cov / (sA * sB) if sA > 0 and sB > 0 else 0.0

    print("\n=== ξ–ξ Current Correlation (C8B, fixed) ===")
    print(f"Cluster A ID      : {A}")
    print(f"Cluster B ID      : {B}")
    print(f"Corr(J_A, J_B)    : {corr:.6f}")

    if abs(corr) > 0.1:
        print("✅ Correlated ξ currents → interaction channel confirmed")
    else:
        print("❌ No ξ-current correlation")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_xi_current_correlation_v2 <json>")
    else:
        main(sys.argv[1])