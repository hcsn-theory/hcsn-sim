import json
import numpy as np

WINDOW = 50  # rewrite window for influence detection

def defect_support(defect_time, rewrite_history, window=WINDOW):
    support = set()
    for r in rewrite_history:
        if abs(r["time"] - defect_time) <= window:
            support |= set(r["rewrite"].get("added_vertices", []))
            support |= set(r["rewrite"].get("removed_vertices", []))
    return support

def influenced(d1, d2, rewrite_history):
    s1 = defect_support(d1["time"], rewrite_history)
    s2 = defect_support(d2["time"], rewrite_history)
    return len(s1 & s2) > 0

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    run = data["runs"][-1]
    defects = run["defects"]
    history = run["rewrite_history"]

    speeds = []
    samples = []

    for i, d1 in enumerate(defects):
        for d2 in defects[i + 1:]:
            dt = d2["time"] - d1["time"]
            if dt <= 0:
                continue

            infl = influenced(d1, d2, history)

            samples.append({
                "dt": dt,
                "influence": int(infl)
            })

            if infl:
                speeds.append(1.0 / dt)

    speeds = np.array(speeds)

    print("\n=== Signal Speed Measurement ===")
    print(f"Samples: {len(speeds)}")
    if len(speeds) > 0:
        print(f"Max speed: {speeds.max():.4f}")
        print(f"Mean speed: {speeds.mean():.4f}")
        print(f"Std: {speeds.std():.4f}")

    # --- SAVE FOR STEP 12 ---
    with open("analysis/signal_speed_samples.json", "w") as f:
        json.dump(samples, f, indent=2)

    print(f"Saved {len(samples)} causal samples to analysis/signal_speed_samples.json")

    # Optional: keep numpy speeds
    np.save("analysis/signal_speeds.npy", speeds)


if __name__ == "__main__":
    main()