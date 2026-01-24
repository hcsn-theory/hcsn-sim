# analysis/measure_coarse_grained_force.py

import json
import sys

WINDOW = 500  # coarse-graining window

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_coarse_grained_force <json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])
    if not rewrites:
        print("❌ No rewrite history found")
        return

    flux = {}
    time_bins = []

    for r in rewrites:
        for cid, size in r.get("cluster_sizes", {}).items():
            flux[cid] = flux.get(cid, 0) + size

        if len(flux) >= 2 and r["time"] % WINDOW == 0:
            ids = sorted(flux.keys())[:2]
            F = flux[ids[0]] - flux[ids[1]]
            time_bins.append(F)
            flux = {}

    if len(time_bins) < 3:
        print("❌ Insufficient coarse-grained samples")
        return

    mean_F = sum(time_bins) / len(time_bins)
    var_F = sum((x - mean_F) ** 2 for x in time_bins) / len(time_bins)

    print("\n=== C11 — Coarse-Grained Force Test ===")
    print(f"Samples          : {len(time_bins)}")
    print(f"⟨F⟩              : {mean_F:.3f}")
    print(f"Var(F)           : {var_F:.3f}")

    if var_F < abs(mean_F):
        print("✅ Stable coarse-grained force → force regime emerging")
    else:
        print("⚠ Fluctuation-dominated → pre-force regime")

if __name__ == "__main__":
    main()