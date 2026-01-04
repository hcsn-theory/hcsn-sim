import json
import numpy as np

# ----------------------------
# Configuration
# ----------------------------
N_BINS = 5  # try 5–10 later
OMEGA_MIN = 0.0
OMEGA_MAX = 1.2  # allow slight overshoot
DT_SAMPLE = 100  # sampling interval used in simulation

# ----------------------------
# Load data
# ----------------------------
with open("analysis/omega_timeseries.json") as f:
    omega_ts = json.load(f)

with open("timeseries.json") as f:
    runs = json.load(f)["runs"]
    defects = runs[-1]["defects"]

# Extract arrays
times = np.array([x["time"] for x in omega_ts])
omegas = np.array([x["omega"] for x in omega_ts])

defect_times = np.array([d["birth_time"] for d in defects])

# ----------------------------
# Bin Ω
# ----------------------------
bins = np.linspace(OMEGA_MIN, OMEGA_MAX, N_BINS + 1)
bin_centers = 0.5 * (bins[:-1] + bins[1:])

time_in_bin = np.zeros(N_BINS)
defects_in_bin = np.zeros(N_BINS)

# ----------------------------
# Accumulate time spent per bin
# ----------------------------
for omega in omegas:
    idx = np.searchsorted(bins, omega) - 1
    if 0 <= idx < N_BINS:
        time_in_bin[idx] += DT_SAMPLE

# ----------------------------
# Assign defects to bins
# ----------------------------
for t in defect_times:
    # find closest Ω sample before defect
    i = np.searchsorted(times, t) - 1
    if i < 0:
        continue
    omega = omegas[i]
    idx = np.searchsorted(bins, omega) - 1
    if 0 <= idx < N_BINS:
        defects_in_bin[idx] += 1

# ----------------------------
# Compute rates
# ----------------------------
rates = np.zeros(N_BINS)
for i in range(N_BINS):
    if time_in_bin[i] > 0:
        rates[i] = defects_in_bin[i] / time_in_bin[i]
    else:
        rates[i] = np.nan

# ----------------------------
# Output
# ----------------------------
print("\n=== Defect Rate vs Ω Binning ===")
print("Bin Ω_center | time | defects | rate")

for i in range(N_BINS):
    print(
        f"{bin_centers[i]:8.3f} | "
        f"{time_in_bin[i]:5.0f} | "
        f"{defects_in_bin[i]:7.0f} | "
        f"{rates[i]:.4e}"
    )

# Optional: correlation
valid = ~np.isnan(rates)
if valid.sum() > 2:
    r = np.corrcoef(bin_centers[valid], rates[valid])[0, 1]
    print(f"\nCorrelation(rate, Ω) ≈ {r:.3f}")
    
out = []

for i in range(N_BINS):
    out.append({
        "omega": float(bin_centers[i]),
        "time": float(time_in_bin[i]),
        "defects": int(defects_in_bin[i]),
        "rate": None if np.isnan(rates[i]) else float(rates[i])
    })

with open("analysis/defect_rate_vs_omega_bins.json", "w") as f:
    json.dump(out, f, indent=2)

print("\nSaved to analysis/defect_rate_vs_omega_bins.json")