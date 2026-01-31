import numpy as np
import json

with open("analysis/omega_timeseries.json") as f:
    data = json.load(f)

omega = np.array([x["omega"] for x in data])
times = np.array([x["time"] for x in data])

# detect large jump
jumps = np.where(np.abs(np.diff(omega)) > 0.1)[0]

for j in jumps[:5]:
    print(f"\nJump at t={times[j]}")
    for k in range(j, min(j+6, len(omega))):
        print(f" t={times[k]:5d} Ω={omega[k]:.4f}")