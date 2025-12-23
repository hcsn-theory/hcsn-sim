import json
import numpy as np

# -----------------------------
# Load data
# -----------------------------
with open("timeseries.json", "r") as f:
    data = json.load(f)

# latest run
run = data[-1] if isinstance(data, list) else data

defects = run["defects"]
times = run["t"]
omega = run["omega"]

if not defects:
    raise RuntimeError("No defects found")

# -----------------------------
# Momentum proxy (observational)
# -----------------------------
def defect_momentum(defects, idx, window=200):
    """
    Momentum = imbalance of Ω drift before vs after defect
    """
    t0 = defects[idx]["time"]

    before = []
    after = []

    for t, om in zip(times, omega):
        if abs(t - t0) > window:
            continue
        if t < t0:
            before.append(om)
        elif t > t0:
            after.append(om)

    if not before or not after:
        return 0.0

    return np.mean(after) - np.mean(before)

# -----------------------------
# Acceleration
# -----------------------------
p = [defect_momentum(defects, i) for i in range(len(defects))]
a = np.diff(p)

# -----------------------------
# Mass proxy
# -----------------------------
if np.var(p) > 0:
    mass = 1.0 / np.var(p)
else:
    mass = np.inf

# -----------------------------
# Output
# -----------------------------
print("Momentum p:")
print(p)

print("\nAcceleration a:")
print(a.tolist())

print("\nMass proxy:")
print(mass)
