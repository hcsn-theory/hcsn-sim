# analysis/test_signal_density_vs_omega.py
import json
import numpy as np

OMEGA_MIN, OMEGA_MAX = 0.0, 1.2
N_BINS = 6

with open("analysis/signal_speed_samples.json") as f:
    samples = json.load(f)

with open("analysis/omega_timeseries.json") as f:
    omega_ts = json.load(f)

omega_at_time = {x["time"]: x["omega"] for x in omega_ts}

bins = np.linspace(OMEGA_MIN, OMEGA_MAX, N_BINS + 1)
bin_centers = 0.5 * (bins[:-1] + bins[1:])
counts = np.zeros(N_BINS)

for s in samples:
    t = s.get("time", None)
    if t not in omega_at_time:
        continue
    O = omega_at_time[t]
    idx = np.searchsorted(bins, O) - 1
    if 0 <= idx < N_BINS:
        counts[idx] += 1

print("\n=== Signal Density vs Ω ===")
for i in range(N_BINS):
    print(f"Ω ≈ {bin_centers[i]:.3f} | signals = {int(counts[i])}")