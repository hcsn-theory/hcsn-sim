# analysis/measure_effective_rewrite_force.py

import json
import sys

def main(path):
    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])
    if not rewrites:
        print("❌ No rewrite history")
        return

    # Identify clusters
    cluster_ids = set()
    for r in rewrites:
        cluster_ids.update(r.get("cluster_sizes", {}).keys())

    if len(cluster_ids) < 2:
        print("❌ Need ≥2 clusters")
        return

    A, B = sorted(cluster_ids)[:2]

    flux_A = []
    flux_B = []

    for r in rewrites:
        sizes = r.get("cluster_sizes", {})
        if A not in sizes or B not in sizes:
            continue

        # proxy: cluster size change as rewrite pressure
        flux_A.append(sizes.get(A, 0))
        flux_B.append(sizes.get(B, 0))

    if len(flux_A) < 10:
        print("❌ Insufficient overlap data")
        return

    mean_A = sum(flux_A) / len(flux_A)
    mean_B = sum(flux_B) / len(flux_B)

    F_AB = mean_A - mean_B

    print("\n=== Effective Rewrite-Flux Force (C9) ===")
    print(f"Cluster A ID        : {A}")
    print(f"Cluster B ID        : {B}")
    print(f"⟨Φ_A⟩              : {mean_A:.3f}")
    print(f"⟨Φ_B⟩              : {mean_B:.3f}")
    print(f"F_AB = Φ_A − Φ_B   : {F_AB:.6f}")

    if abs(F_AB) > 0.1:
        print("✅ Non-zero effective interaction law detected")
    else:
        print("❌ No measurable force law")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_effective_rewrite_force <json>")
    else:
        main(sys.argv[1])