import json
import numpy as np
from scipy.stats import pearsonr

with open("analysis/particles.json") as f:
    particles = json.load(f)

taus = []
mean_omegas = []

for p in particles:
    if len(p["times"]) >= 2:
        tau = max(p["times"]) - min(p["times"])
        taus.append(tau)
        mean_omegas.append(np.mean(p["omegas"]))

taus = np.array(taus)
mean_omegas = np.array(mean_omegas)

r, p = pearsonr(mean_omegas, taus)

print("=== Lifetime vs Ω Basin Test ===")
print(f"Correlation r ≈ {r:.3f}")
print(f"p-value ≈ {p:.3e}")