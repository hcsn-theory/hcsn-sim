import json
import numpy as np

WINDOW = 80          # choose from your tests
P_THRESHOLD = 0.5    # identity threshold

def defect_support(defect_time, rewrite_history, window=WINDOW):
    support = set()
    for r in rewrite_history:
        if abs(r["time"] - defect_time) <= window:
            support |= set(r["rewrite"].get("added_vertices", []))
            support |= set(r["rewrite"].get("removed_vertices", []))
    return support

def persistence(s1, s2):
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    run = data["runs"][-1]

    defects = run.get("defects", [])
    rewrite_history = run.get("rewrite_history", [])

    if len(defects) < 2 or not rewrite_history:
        print("Not enough data to measure lifetimes.")
        return

    lifetimes = []
    current_life = 1

    supports = [
        defect_support(d["time"], rewrite_history)
        for d in defects
    ]

    for i in range(len(supports) - 1):
        p = persistence(supports[i], supports[i + 1])
        if p >= P_THRESHOLD:
            current_life += 1
        else:
            lifetimes.append(current_life)
            current_life = 1

    lifetimes.append(current_life)

    lifetimes = np.array(lifetimes)

    print("\n=== Defect Lifetime Distribution ===")
    print(f"Samples: {len(lifetimes)}")
    print(f"Mean lifetime: {lifetimes.mean():.2f}")
    print(f"Std: {lifetimes.std():.2f}")
    print(f"Max lifetime: {lifetimes.max()}")
    print(f"Min lifetime: {lifetimes.min()}")

    # Optional histogram data (no plotting yet)
    unique, counts = np.unique(lifetimes, return_counts=True)
    print("\nLifetime counts:")
    for u, c in zip(unique, counts):
        print(f"  {u}: {c}")

if __name__ == "__main__":
    main()
