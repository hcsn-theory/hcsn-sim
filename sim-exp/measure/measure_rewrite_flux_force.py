# analysis/measure_rewrite_flux_force.py

import json
import sys
from collections import defaultdict

# ----------------------------------------
# Purpose:
# Measure interaction via rewrite-flux
# imbalance between proto-particles.
# ----------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_rewrite_flux_force <interaction_json>")
        sys.exit(1)

    path = sys.argv[1]

    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])

    if not rewrites:
        print("❌ No rewrite history found")
        sys.exit(1)

    # ----------------------------------------
    # Accumulate rewrite flux per cluster
    # ----------------------------------------
    flux_per_cluster = defaultdict(int)
    cluster_sizes = defaultdict(list)

    for r in rewrites:
        sizes = r.get("cluster_sizes", {})
        xi_support = r.get("xi_support", [])

        for cid, size in sizes.items():
            cluster_sizes[cid].append(size)

            # If rewrite touched ξ-support, count as flux
            if xi_support:
                flux_per_cluster[cid] += 1

    if len(flux_per_cluster) < 2:
        print("❌ Insufficient clusters for interaction test")
        sys.exit(1)

    # ----------------------------------------
    # Select two dominant clusters
    # ----------------------------------------
    clusters = sorted(
        flux_per_cluster.keys(),
        key=lambda c: sum(cluster_sizes[c]),
        reverse=True
    )

    A, B = clusters[:2]

    FA = flux_per_cluster[A]
    FB = flux_per_cluster[B]

    # ----------------------------------------
    # Define scalar interaction force
    # ----------------------------------------
    tau = min(len(cluster_sizes[A]), len(cluster_sizes[B]))

    if tau == 0:
        print("❌ Zero coexistence time")
        sys.exit(1)

    F_AB = (FA - FB) / tau

    # ----------------------------------------
    # Report
    # ----------------------------------------
    print("\n=== Rewrite-Flux Interaction Force ===")
    print(f"Cluster A ID      : {A}")
    print(f"Cluster B ID      : {B}")
    print(f"Rewrite flux A    : {FA}")
    print(f"Rewrite flux B    : {FB}")
    print(f"Coexistence τ     : {tau}")
    print(f"Force F_AB        : {F_AB:.4f}")

    if abs(F_AB) > 0.01:
        print("✅ Non-zero interaction force detected")
    else:
        print("⚠ Flux symmetric → weak or no interaction")


if __name__ == "__main__":
    main()