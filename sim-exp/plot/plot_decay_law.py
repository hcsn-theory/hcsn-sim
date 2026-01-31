# analysis/plot_decay_law.py

import json
import numpy as np
import matplotlib.pyplot as plt

def main():
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    lifetimes = [
        max(p["times"]) - min(p["times"])
        for p in particles
        if len(p["times"]) > 1
    ]

    lifetimes = np.array(lifetimes)

    plt.figure(figsize=(6,4))
    plt.hist(lifetimes, bins=10, density=True)
    plt.xlabel("Lifetime Δτ")
    plt.ylabel("Probability density")
    plt.title("Particle Decay Distribution")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    print("\nDecay stats:")
    print(f"Mean lifetime: {lifetimes.mean():.2f}")
    print(f"Std: {lifetimes.std():.2f}")

if __name__ == "__main__":
    main()