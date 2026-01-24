# analysis/measure_force_time_series.py

import json
import sys
import statistics

WINDOW = 200  # sliding window size
MIN_POINTS = 5

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_force_time_series <interaction_json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    log = data.get("interaction_log", [])
    if not log:
        print("❌ No interaction log found")
        return

    # Extract per-step cluster sizes as flux proxy
    times = []
    flux_A = []
    flux_B = []

    for entry in log:
        sizes = entry.get("cluster_sizes", {})
        if len(sizes) < 2:
            continue

        # enforce deterministic ordering
        cids = sorted(sizes.keys())
        times.append(entry["time"])
        flux_A.append(sizes[cids[0]])
        flux_B.append(sizes[cids[1]])

    if len(times) < WINDOW + MIN_POINTS:
        print("❌ Insufficient data for time-series force analysis")
        return

    forces = []
    force_times = []

    for i in range(WINDOW, len(times)):
        A_window = flux_A[i-WINDOW:i]
        B_window = flux_B[i-WINDOW:i]

        F = statistics.mean(A_window) - statistics.mean(B_window)
        forces.append(F)
        force_times.append(times[i])

    mean_F = statistics.mean(forces)
    std_F = statistics.pstdev(forces)

    print("\n=== C10A — Force Time Stability ===")
    print(f"Mean F_AB        : {mean_F:.4f}")
    print(f"Std deviation   : {std_F:.4f}")
    print(f"Relative noise  : {std_F / abs(mean_F) if mean_F != 0 else float('inf'):.4f}")

    if std_F / abs(mean_F) < 0.1:
        print("✅ Force is time-stable → law-like interaction")
    elif std_F / abs(mean_F) < 0.5:
        print("⚠ Force weakly drifting → renormalizing interaction")
    else:
        print("❌ Force unstable → transient coupling")

if __name__ == "__main__":
    main()