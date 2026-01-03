import numpy as np
import json

with open("analysis/omega_timeseries.json") as f:
    data = json.load(f)

omega = np.array([x["omega"] for x in data])
delta = omega - omega.mean()

msd = []
for tau in range(1, 20):
    msd.append(np.mean((delta[tau:] - delta[:-tau])**2))

for i, v in enumerate(msd, 1):
    print(f"τ={i:2d} MSD={v:.5f}")