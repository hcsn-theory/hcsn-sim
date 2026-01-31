import json
import numpy as np

PROXIMITY = 50   # time window for interaction
EPS = 0.15       # near-conservation threshold

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    runs = data["runs"]
    run = runs[-1]
    defects = run["defects"]

    if len(defects) < 2:
        print("Not enough defects for scattering analysis.")
        return

    residuals = []

    for i in range(len(defects)):
        for j in range(i + 1, len(defects)):
            d1 = defects[i]
            d2 = defects[j]

            dt = abs(d1["time"] - d2["time"])
            if dt > PROXIMITY:
                continue

            # Use observable momentum magnitude proxy
            p1 = abs(d1.get("delta_Q", 0.0))
            p2 = abs(d2.get("delta_Q", 0.0))

            # Look ahead to nearest later events (post-interaction)
            p1_after = p1
            p2_after = p2

            for d in defects:
                if d["time"] > max(d1["time"], d2["time"]) and \
                   d["time"] < max(d1["time"], d2["time"]) + PROXIMITY:
                    p1_after = abs(d.get("delta_Q", p1_after))
                    p2_after = abs(d.get("delta_Q", p2_after))
                    break

            residual = (p1 + p2) - (p1_after + p2_after)
            residuals.append(residual)

    residuals = np.array(residuals)

    if len(residuals) == 0:
        print("No scattering pairs detected.")
        return

    print("\n=== Scattering Experiment (Observable-Level) ===")
    print(f"Pairs tested: {len(residuals)}")
    print(f"Mean Δp_total: {residuals.mean():.3e}")
    print(f"Std Δp_total:  {residuals.std():.3e}")
    print(f"Near-zero fraction: {(np.abs(residuals) < EPS).mean():.2%}")

if __name__ == "__main__":
    main()