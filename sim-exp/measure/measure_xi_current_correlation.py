# analysis/measure_xi_current_correlation.py

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

    xi_log = data.get("xi_current_log", [])
    if not xi_log:
        print("❌ No ξ-current log available (C8A missing)")
        return

    # Identify clusters
    cluster_ids = set()
    for entry in xi_log:
        cluster_ids.update(entry.get("cluster_ids", []))

    if len(cluster_ids) < 2:
        print("❌ Need ≥2 clusters for C8B")
        return

    cid_list = sorted(cluster_ids)
    A, B = cid_list[:2]

    J_A = []
    J_B = []

    for entry in xi_log:
        delta_xi = entry["delta_xi"]
        touched = entry["touched"]

        JA = 0.0
        JB = 0.0

        for v in touched:
            dxi = delta_xi.get(str(v), delta_xi.get(v, 0.0))
            if A in entry["cluster_ids"]:
                JA += dxi
            if B in entry["cluster_ids"]:
                JB += dxi

        J_A.append(JA)
        J_B.append(JB)

    if len(J_A) < 10:
        print("❌ Insufficient data for correlation")
        return

    cov = covariance(J_A, J_B)
    stdA = std(J_A)
    stdB = std(J_B)

    corr = cov / (stdA * stdB) if stdA > 0 and stdB > 0 else 0.0

    print("\n=== ξ–ξ Current Correlation (C8B) ===")
    print(f"Cluster A ID      : {A}")
    print(f"Cluster B ID      : {B}")
    print(f"⟨J_A⟩             : {mean(J_A):.6f}")
    print(f"⟨J_B⟩             : {mean(J_B):.6f}")
    print(f"Corr(J_A, J_B)    : {corr:.6f}")

    if abs(corr) > 0.1:
        print("✅ Non-zero ξ-current correlation → interaction channel detected")
    else:
        print("❌ ξ-currents uncorrelated")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_xi_current_correlation <json>")
    else:
        main(sys.argv[1])