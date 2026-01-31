# analysis/validate_momentum_conservation.py

import json
import numpy as np
from analysis.defects import defect_momentum

TIME_WINDOW = 30
NEAR_ZERO = 0.2  # tolerance

with open("timeseries.json", "r") as f:
    runs = json.load(f)

# Use latest run
run = runs[-1] if isinstance(runs, list) else runs
defects = run.get("defects", [])

if len(defects) < 2:
    raise RuntimeError("Not enough defects for momentum conservation test")

# Compute momentum for each defect
momentum = [
    defect_momentum(defects, d, window=TIME_WINDOW)
    for d in defects
]

# Pair nearby defects
pairs = []
for i in range(len(defects)):
    for j in range(i + 1, len(defects)):
        if abs(defects[i]["time"] - defects[j]["time"]) <= TIME_WINDOW:
            pairs.append((i, j))

if not pairs:
    raise RuntimeError("No nearby defect pairs found")

# Conservation residuals
residuals = [
    momentum[i] + momentum[j]
    for (i, j) in pairs
]

residuals = np.array(residuals)

print("\n=== Momentum Conservation Test ===")
print(f"Pairs tested: {len(residuals)}")
print(f"Mean residual: {np.mean(residuals):.3e}")
print(f"Std residual:  {np.std(residuals):.3e}")
print(
    f"Fraction near zero: "
    f"{np.mean(np.abs(residuals) < NEAR_ZERO) * 100:.1f}%"
)

# Randomized control
shuffled = np.random.permutation(momentum)
random_residuals = [
    shuffled[i] + shuffled[j] for (i, j) in pairs
]

print("\nRandomized control:")
print(f"Mean: {np.mean(random_residuals):.3e}")
print(f"Std:  {np.std(random_residuals):.3e}")