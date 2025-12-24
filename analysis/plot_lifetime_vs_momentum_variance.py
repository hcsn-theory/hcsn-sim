import json
import numpy as np
import matplotlib.pyplot as plt

WINDOW = 3  # local window over defect index

with open("timeseries.json") as f:
    run = json.load(f)["runs"][-1]

defects = run["defects"]

times = [d["time"] for d in defects]
lifetimes = np.diff(times)
p = np.array([abs(d["delta_Q"]) for d in defects])

var_p = []
for i in range(len(lifetimes)):
    start = max(0, i - WINDOW)
    end = min(len(p), i + WINDOW + 1)
    var_p.append(np.var(p[start:end]))

var_p = np.array(var_p)

plt.figure(figsize=(6, 4))
plt.scatter(lifetimes, var_p, alpha=0.8)
plt.xlabel("Defect lifetime (Δt)")
plt.ylabel("Var(|p|)")
plt.title("Lifetime vs Momentum Variance (Mass Proxy)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()