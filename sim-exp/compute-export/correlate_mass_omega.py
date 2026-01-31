# analysis/correlate_mass_omega.py

import json
import numpy as np
from analysis.defects import defect_momentum

WINDOW = 30

with open("timeseries.json", "r") as f:
    runs = json.load(f)

run = runs[-1] if isinstance(runs, list) else runs
defects = run.get("defects", [])

if len(defects) < 3:
    raise RuntimeError("Not enough defects for mass–Ω correlation")

# Compute momentum per defect
momentum = np.array([
    defect_momentum(defects, d, window=WINDOW)
    for d in defects
])

omega = np.array([
    d["omega"] for d in defects
])

abs_p = np.abs(momentum)

# Mass proxy (global)
mass_proxy = 1.0 / np.var(momentum)

corr = np.corrcoef(omega, abs_p)[0, 1]

print("\n=== Mass–Ω Correlation ===")
print(f"Samples: {len(defects)}")
print(f"Momentum variance: {np.var(momentum):.4f}")
print(f"Mass proxy: {mass_proxy:.2f}")
print(f"Ω–|p| correlation: {corr:.3f}")