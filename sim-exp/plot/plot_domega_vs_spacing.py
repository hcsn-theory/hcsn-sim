import json
import numpy as np
import matplotlib.pyplot as plt

with open("timeseries.json") as f:
    data = json.load(f)

run = data[-1] if isinstance(data, list) else data

omega = np.array(run["omega"])
t = np.array(run["t"])
defects = run["defects"]

defect_times = np.array([d["time"] for d in defects])
delta_Q = np.array([d["delta_Q"] for d in defects])

# Find omega jump near defect
omega_jump = []
for dt in defect_times:
    idx = np.searchsorted(t, dt)
    if 1 <= idx < len(omega):
        omega_jump.append(abs(omega[idx] - omega[idx - 1]))

omega_jump = np.array(omega_jump)
spacing = np.diff(defect_times)

plt.figure(figsize=(7, 5))
plt.scatter(spacing, omega_jump[1:], s=60)
plt.xlabel("Defect spacing")
plt.ylabel("|ΔΩ|")
plt.title("Defect Spacing vs Hierarchy Jump")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
