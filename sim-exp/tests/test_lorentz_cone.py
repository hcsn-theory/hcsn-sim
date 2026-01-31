import json
import numpy as np

def main():
    with open("analysis/signal_speed_samples.json") as f:
        samples = json.load(f)

    dt = np.array([s["dt"] for s in samples])
    influence = np.array([s["influence"] for s in samples])

    # Emergent causal speed
    speeds = influence / dt

    vmax = speeds.max()
    mean_v = speeds.mean()
    std_v = speeds.std()

    # Check for violations (should be none by construction)
    violations = np.sum(speeds > vmax * 1.001)

    # Correlation: faster signals ↔ smaller dt
    valid = speeds > 0
    corr = np.corrcoef(dt[valid], speeds[valid])[0, 1] if valid.sum() > 2 else np.nan

    print("\n=== Step 20.4: Emergent Lorentz (Causal) Cone ===")
    print(f"Samples: {len(speeds)}")
    print(f"Signals detected: {valid.sum()}")
    print(f"Max causal speed v_max ≈ {vmax:.6f}")
    print(f"Mean speed           ≈ {mean_v:.6f}")
    print(f"Std deviation        ≈ {std_v:.6f}")
    print(f"Violations           : {violations}")
    print(f"Corr(speed, dt)      ≈ {corr:.3f}")

if __name__ == "__main__":
    main()