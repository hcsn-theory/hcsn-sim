# analysis/measure_force_event_stability.py

import json
import sys
import statistics

MIN_EVENTS = 10

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_force_event_stability <interaction_json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    log = data.get("interaction_log", [])
    if not log:
        print("❌ No interaction log found")
        return

    forces = []

    for entry in log:
        sizes = entry.get("cluster_sizes", {})
        if len(sizes) < 2:
            continue

        cids = sorted(sizes.keys())
        F = sizes[cids[0]] - sizes[cids[1]]
        forces.append(F)

    if len(forces) < MIN_EVENTS:
        print("❌ Too few interaction events for stability test")
        return

    mean_F = statistics.mean(forces)
    std_F = statistics.pstdev(forces)

    print("\n=== C10A — Event-Based Force Stability ===")
    print(f"Interaction events : {len(forces)}")
    print(f"Mean F_AB          : {mean_F:.4f}")
    print(f"Std deviation     : {std_F:.4f}")
    print(f"Relative noise    : {std_F / abs(mean_F) if mean_F != 0 else float('inf'):.4f}")

    if std_F / abs(mean_F) < 0.2:
        print("✅ Force stable across interaction events")
    elif std_F / abs(mean_F) < 0.6:
        print("⚠ Force fluctuates → renormalizing interaction")
    else:
        print("❌ Force unstable → episodic coupling")

if __name__ == "__main__":
    main()