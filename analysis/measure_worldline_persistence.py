import json
import numpy as np

WINDOW = 30

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

    runs = data.get("runs", [])
    if not runs:
        print("No runs found.")
        return

    run = runs[-1]

    if "defects" not in run or "rewrite_history" not in run:
        print("Not enough data for worldline persistence analysis.")
        print("Run must contain defects and rewrite_history.")
        return

    defects = run["defects"]
    rewrite_history = run["rewrite_history"]

    if len(defects) < 2:
        print("Not enough defect events.")
        return

    scores = []

    for d1, d2 in zip(defects[:-1], defects[1:]):
        s1 = defect_support(d1["time"], rewrite_history)
        s2 = defect_support(d2["time"], rewrite_history)
        scores.append(persistence(s1, s2))

    scores = np.array(scores)

    print("\n=== Worldline Persistence ===")
    print(f"Samples: {len(scores)}")
    print(f"Mean persistence: {scores.mean():.3f}")
    print(f"Std: {scores.std():.3f}")
    print(f">0.5 fraction: {(scores > 0.5).mean():.2%}")

if __name__ == "__main__":
    main()