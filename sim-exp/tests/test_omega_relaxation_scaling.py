import json
import numpy as np

with open("analysis/omega_timeseries.json") as f:
    data = json.load(f)

omega = np.array([d["omega"] for d in data])
time  = np.array([d["time"] for d in data])

omega_inf = np.mean(omega[-10:])
eps = 0.05 * abs(omega_inf)

relax_times = []

for i in range(len(omega)):
    if abs(omega[i] - omega_inf) < eps:
        relax_times.append(time[i] - time[0])
        break

print("=== STEP 3: Ω Relaxation ===")
print("Relaxation time:", relax_times[0] if relax_times else "not converged")