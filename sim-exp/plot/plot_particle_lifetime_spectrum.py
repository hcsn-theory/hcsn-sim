# analysis/plot_particle_lifetime_spectrum.py

import json
import numpy as np
import matplotlib.pyplot as plt

PARTICLE_FILE = "analysis/particles.json"

def particle_lifetime(p):
    times = p.get("times", [])
    if len(times) < 2:
        return 0
    return max(times) - min(times)

def main():
    with open(PARTICLE_FILE) as f:
        particles = json.load(f)

    if not particles:
        print("No particles found.")
        return

    lifetimes = np.array([particle_lifetime(p) for p in particles])

    print("\n=== Particle Lifetime Spectrum ===")
    print(f"Particles:     {len(lifetimes)}")
    print(f"Mean lifetime: {lifetimes.mean():.2f}")
    print(f"Max lifetime:  {lifetimes.max()}")
    print(f"Min lifetime:  {lifetimes.min()}")

    # Histogram
    plt.figure(figsize=(8, 5))

    bins = np.unique(lifetimes)
    plt.hist(
        lifetimes,
        bins=np.append(bins, bins[-1] + 1),
        align="left",
        rwidth=0.8
    )

    plt.xlabel("Particle Lifetime Δτ")
    plt.ylabel("Count")
    plt.title("Particle Lifetime Spectrum (HCSN)")

    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()