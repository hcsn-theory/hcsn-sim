# analysis/measure_force_impulse_integral_overlap.py

import json
import sys
import math
import numpy as np

# --------------------------------------------
# Overlapping impulse integral (C10C)
# --------------------------------------------

WINDOWS = [50, 100, 200, 500]

def extract_force_series(data):
    """
    Reconstruct instantaneous force proxy
    using rewrite-flux imbalance between clusters.
    """
    rewrites = data.get("rewrite_history", [])

    series = []
    for r in rewrites:
        sizes = r.get("cluster_sizes", {})
        if len(sizes) < 2:
            continue

        ids = sorted(sizes.keys())
        # force proxy = size imbalance
        F = sizes[ids[0]] - sizes[ids[1]]
        series.append(F)

    return series


def sliding_window_force(F_series, window):
    half = window // 2
    F_eff = []

    for i in range(half, len(F_series) - half):
        segment = F_series[i - half : i + half]
        F_eff.append(sum(segment) / window)

    return F_eff


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_force_impulse_integral_overlap <json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    F_series = extract_force_series(data)

    if len(F_series) < 100:
        print("❌ Insufficient force samples")
        sys.exit(0)

    print("\n=== Overlapping Impulse Integral (C10C) ===")

    for Δt in WINDOWS:
        F_eff = sliding_window_force(F_series, Δt)

        if len(F_eff) < 10:
            continue

        mean_F = float(np.mean(F_eff))
        var_F  = float(np.var(F_eff))

        print(f"\nΔt = {Δt}")
        print(f"Samples        : {len(F_eff)}")
        print(f"⟨F_eff⟩        : {mean_F:.6f}")
        print(f"Var(F_eff)     : {var_F:.6f}")

        if var_F < mean_F**2:
            print("✅ Classical-force regime emerging")
        else:
            print("⚠ Still fluctuation-dominated")

    print("\n✔ Overlapping impulse integration complete")


if __name__ == "__main__":
    main()