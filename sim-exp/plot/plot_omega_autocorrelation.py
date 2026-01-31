import json
import numpy as np
import matplotlib.pyplot as plt

with open("timeseries.json") as f:
    data = json.load(f)

run = data[-1] if isinstance(data, list) else data
omega = np.array(run["omega"])

omega -= omega.mean()
corr = np.correlate(omega, omega, mode="full")
corr = corr[corr.size // 2:]
corr /= corr[0]

lags = np.arange(len(corr))

plt.figure(figsize=(7, 5))
plt.plot(lags, corr)
plt.xscale("log")
plt.xlabel("Lag")
plt.ylabel("C(Ω)")
plt.title("Autocorrelation of Hierarchical Closure")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
