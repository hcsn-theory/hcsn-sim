# analysis/measure_force_scaling.py

import json
import sys
import math

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_force_scaling <interaction_json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    log = data.get("interaction_log", [])
    if not log:
        print("❌ No interaction log found")
        return

    samples = []

    for entry in log:
        sizes = entry.get("cluster_sizes", {})
        if len(sizes) < 2:
            continue

        cids = sorted(sizes.keys())
        size_mean = 0.5 * (sizes[cids[0]] + sizes[cids[1]])
        force = sizes[cids[0]] - sizes[cids[1]]

        if size_mean > 0:
            samples.append((size_mean, abs(force)))

    if len(samples) < 5:
        print("❌ Too few samples for scaling analysis")
        return

    # log–log regression
    xs = [math.log(s) for s, f in samples if f > 0]
    ys = [math.log(f) for s, f in samples if f > 0]

    if len(xs) < 5:
        print("❌ Insufficient positive-force samples")
        return

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)

    alpha = num / den if den != 0 else float("nan")

    print("\n=== C10B — Interaction Scaling Test ===")
    print(f"Samples used     : {len(xs)}")
    print(f"Scaling exponent : α ≈ {alpha:.3f}")

    if 0.5 < alpha < 2.5:
        print("✅ Nontrivial scaling → emergent force regime")
    else:
        print("⚠ No clear scaling → pre-force interaction")

if __name__ == "__main__":
    main()