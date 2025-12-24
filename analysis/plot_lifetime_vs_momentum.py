import json
import numpy as np
import matplotlib.pyplot as plt

with open("timeseries.json") as f:
    run = json.load(f)["runs"][-1]

defects = run["defects"]

times = [d["time"] for d in defects]
lifetimes = np.diff(times)
momentum = np.array([abs(d["delta_Q"]) for d in defects[:-1]])

plt.figure(figsize=(6, 4))
plt.scatter(lifetimes, momentum, alpha=0.8)
plt.xlabel("Defect lifetime (Δt)")
plt.ylabel("|p| (|ΔΩ|)")
plt.title("Lifetime vs Momentum Magnitude")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()