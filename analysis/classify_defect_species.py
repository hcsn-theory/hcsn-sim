import json
import numpy as np

def main():
    with open("timeseries.json") as f:
        run = json.load(f)["runs"][-1]

    defects = run["defects"]

    times = [d["time"] for d in defects]
    lifetimes = np.diff(times)
    momentum = np.array([abs(d["delta_Q"]) for d in defects[:-1]])
    omega = np.array([d["omega"] for d in defects[:-1]])

    species = {
        "stable": [],
        "transient": [],
        "noisy": []
    }

    for τ, p, Ω in zip(lifetimes, momentum, omega):
        if τ >= np.median(lifetimes) and p < np.median(momentum):
            species["stable"].append((τ, p, Ω))
        elif p > np.percentile(momentum, 75):
            species["noisy"].append((τ, p, Ω))
        else:
            species["transient"].append((τ, p, Ω))

    print("\n=== Defect Species (Rule-Based) ===")
    for name, group in species.items():
        if not group:
            continue
        g = np.array(group)
        print(f"\n{name.upper()}:")
        print(f"  Count: {len(g)}")
        print(f"  Mean lifetime: {g[:,0].mean():.2f}")
        print(f"  Mean |p|: {g[:,1].mean():.4f}")
        print(f"  Mean Ω: {g[:,2].mean():.4f}")

if __name__ == "__main__":
    main()