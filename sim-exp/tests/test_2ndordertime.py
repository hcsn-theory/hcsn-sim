import json
import numpy as np

# Load omega time series
with open("analysis/omega_timeseries.json") as f:
    omega_data = json.load(f)

# Extract omega values (ensure correct ordering)
omega = np.array([x["omega"] for x in omega_data])

# Second discrete time derivative
d2 = omega[2:] - 2 * omega[1:-1] + omega[:-2]

print("=== Step 20.1: Second-Order Time Test ===")
print("Samples:", len(d2))
print("Mean d²Ω:", np.mean(d2))
print("Variance d²Ω:", np.var(d2))
print("Std d²Ω:", np.std(d2))