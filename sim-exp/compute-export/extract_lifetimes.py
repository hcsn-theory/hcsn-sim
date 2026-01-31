import json
import numpy as np

with open("analysis/particles.json") as f:
    particles = json.load(f)

lifetimes = []

for p in particles:
    t = p["times"]
    if len(t) >= 2:
        lifetimes.append(max(t) - min(t))

lifetimes = np.array(lifetimes)

print("=== Particle Lifetime Distribution ===")
print(f"Count (τ > 0): {len(lifetimes)}")
print(f"Mean τ: {lifetimes.mean():.2f}")
print(f"Std τ : {lifetimes.std():.2f}")
print(f"Min τ : {lifetimes.min():.2f}")
print(f"Max τ : {lifetimes.max():.2f}")

np.save("analysis/lifetimes.npy", lifetimes)