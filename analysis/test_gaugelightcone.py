import json
import numpy as np

with open("analysis/omega_timeseries.json") as f:
    omega_data = json.load(f)

with open("timeseries.json") as f:
    ts = json.load(f)["runs"][-1]

L_series = ts["t"]  # causal depth proxy if L stored separately adjust here

times = np.array([x["time"] for x in omega_data])
omega = np.array([x["omega"] for x in omega_data])

domega = np.abs(np.diff(omega))
dt = np.diff(times)

# threshold = meaningful Ω change
mask = domega > np.percentile(domega, 75)

speeds = domega[mask] / dt[mask]

print("Ω propagation speed stats:")
print("Max vΩ :", speeds.max())
print("Mean vΩ:", speeds.mean())
print("Std vΩ :", speeds.std())