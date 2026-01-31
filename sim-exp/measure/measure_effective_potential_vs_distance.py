import json
import sys
import math
from collections import defaultdict


def is_finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_effective_potential_vs_distance <json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    interaction_log = data.get("interaction_log", [])
    if not interaction_log:
        print("❌ No interaction_log found")
        return

    # --------------------------------------------------
    # Distance → list of finite ΔΦ samples
    # --------------------------------------------------
    bins = defaultdict(list)

    prev_activity = {}

    for entry in interaction_log:
        # must have ≥2 clusters
        if entry.get("num_clusters", 0) < 2:
            continue

        distances = entry.get("cluster_distance_memory_raw", {})
        if not distances:
            continue

        xi_support = entry.get("xi_support", {})
        if not xi_support:
            continue

        # finite ξ activity proxy
        activity = sum(v for v in xi_support.values() if is_finite(v))

        for pair, d in distances.items():
            if not is_finite(d):
                continue

            d = int(d)

            prev = prev_activity.get(d)
            if prev is not None:
                delta_phi = prev - activity
                if is_finite(delta_phi):
                    bins[d].append(delta_phi)

            prev_activity[d] = activity

    if not bins:
        print("❌ No distance-resolved samples")
        return

    # --------------------------------------------------
    # Output
    # --------------------------------------------------
    print("\n=== D2 — Effective Potential vs Distance (finite ξ) ===\n")

    for d in sorted(bins):
        vals = bins[d]
        n = len(vals)
        mean = sum(vals) / n
        var = sum((x - mean) ** 2 for x in vals) / n

        print(
            f"d = {d:3d} | "
            f"samples = {n:4d} | "
            f"⟨ΔΦ⟩ = {mean: .6e} | "
            f"Var = {var: .6e}"
        )

    print("\n✔ Distance-resolved effective potential extraction complete")


if __name__ == "__main__":
    main()