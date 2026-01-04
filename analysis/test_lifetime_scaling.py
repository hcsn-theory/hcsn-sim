import json
import numpy as np
from scipy.stats import linregress

variants = ["baseline", "variant_1", "variant_2", "variant_3", "variant_4"]

# Load global timeseries once
with open("timeseries.json") as f:
    all_runs = json.load(f)["runs"]

proxy = []   # size proxy (final <k>)
tau = []     # mean lifetime

for i, v in enumerate(variants):
    run = all_runs[i]

    # size proxy: final average coordination
    k_series = run["k"]
    proxy.append(k_series[-1])

    # particle stats are per-variant
    with open(f"{v}/particle_stats.json") as f:
        stats = json.load(f)
    tau.append(stats["mean_lifetime"])

proxy = np.array(proxy)
tau = np.array(tau)

logP = np.log(proxy)
logT = np.log(tau)

slope, intercept, r, pval, stderr = linregress(logP, logT)

print("=== STEP 1: Lifetime Scaling (Proxy) ===")
print("Proxy used: final <k>")
print(f"Scaling exponent α ≈ {slope:.3f}")
print(f"Correlation r ≈ {r:.3f}")
print(f"p-value ≈ {pval:.3e}")