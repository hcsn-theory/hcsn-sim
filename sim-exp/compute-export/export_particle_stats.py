import json
import numpy as np

with open("analysis/particles.json") as f:
    particles = json.load(f)

lifetimes = []
mean_omegas = []

for p in particles:
    times = p.get("times", [])
    if len(times) < 2:
        continue

    lifetime = max(times) - min(times)
    if lifetime <= 0:
        continue

    lifetimes.append(lifetime)
    mean_omegas.append(p.get("mean_omega", None))

out = {
    "count": len(lifetimes),
    "mean_lifetime": float(np.mean(lifetimes)) if lifetimes else 0.0,
    "max_lifetime": int(max(lifetimes)) if lifetimes else 0,
    "min_lifetime": int(min(lifetimes)) if lifetimes else 0,
}

with open("analysis/particle_stats.json", "w") as f:
    json.dump(out, f, indent=2)

print("Saved particle statistics to analysis/particle_stats.json")