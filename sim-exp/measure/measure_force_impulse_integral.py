# analysis/measure_force_impulse_integral.py

import json
import sys
from collections import defaultdict
import math


# --------------------------------------------------
# Parameters (safe defaults)
# --------------------------------------------------
WINDOW_SIZES = [50, 100, 200, 500]


# --------------------------------------------------
# Utility
# --------------------------------------------------
def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def variance(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_force_impulse_integral <interaction.json>")
        sys.exit(1)

    path = sys.argv[1]

    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])
    if not rewrites:
        print("❌ No rewrite history available")
        return

    # --------------------------------------------------
    # Extract impulse-like force events
    # --------------------------------------------------
    # Force proxy: |Δ(cluster size)| per rewrite
    impulse_events = []

    prev_sizes = {}

    for r in rewrites:
        t = r["time"]
        sizes = r.get("cluster_sizes", {})

        for cid, size in sizes.items():
            prev = prev_sizes.get(cid)
            if prev is not None:
                impulse = size - prev
                if impulse != 0:
                    impulse_events.append({
                        "time": t,
                        "cluster": cid,
                        "impulse": impulse
                    })

            prev_sizes[cid] = size

    if not impulse_events:
        print("❌ No impulse events detected")
        return

    # --------------------------------------------------
    # Group impulses by time
    # --------------------------------------------------
    impulses_by_time = defaultdict(list)
    for e in impulse_events:
        impulses_by_time[e["time"]].append(e["impulse"])

    times = sorted(impulses_by_time.keys())
    t_min, t_max = times[0], times[-1]

    # --------------------------------------------------
    # Coarse-graining
    # --------------------------------------------------
    print("\n=== Force Impulse Integral (C10B) ===")

    for W in WINDOW_SIZES:
        window_forces = []

        t = t_min
        while t + W <= t_max:
            total_impulse = 0.0

            for τ in range(t, t + W + 1):
                if τ in impulses_by_time:
                    total_impulse += sum(impulses_by_time[τ])

            F_eff = total_impulse / W
            window_forces.append(F_eff)

            t += W  # non-overlapping windows (conservative)

        if not window_forces:
            continue

        print(f"\nΔt = {W}")
        print(f"Samples        : {len(window_forces)}")
        print(f"⟨F_eff⟩        : {mean(window_forces):.6f}")
        print(f"Var(F_eff)     : {variance(window_forces):.6f}")

        if variance(window_forces) < abs(mean(window_forces)) ** 2:
            print("✅ Coarse-grained force emerging")
        else:
            print("⚠ Still fluctuation-dominated")

    print("\n✔ Impulse integration complete")


# --------------------------------------------------
if __name__ == "__main__":
    main()