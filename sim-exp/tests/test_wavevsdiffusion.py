import json
import numpy as np

with open("analysis/omega_timeseries.json") as f:
    data = json.load(f)

omega = np.array([x["omega"] for x in data])
omega -= omega.mean()

max_lag = 30
corr = []

for tau in range(1, max_lag + 1):
    c = np.corrcoef(omega[:-tau], omega[tau:])[0, 1]
    corr.append((tau, c))

print("τ | autocorr")
for t, c in corr:
    print(f"{t:2d} | {c:+.3f}")