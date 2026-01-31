import json
import numpy as np
from scipy.optimize import curve_fit

# ---- critical model ----
def critical_model(O, C, Oc, nu):
    return C * np.maximum(Oc - O, 0)**nu

# ---- config ----
N_BINS = 5
OMEGA_MAX = 1.2
DT_SAMPLE = 100

with open("timeseries.json") as f:
    runs = json.load(f)["runs"]

results = []

for i, run in enumerate(runs):
    omega_ts = np.array(run["omega"])
    times = np.array(run["t"])
    defects = run["defects"]

    defect_times = np.array([d["time"] for d in defects])

    # ---- bin Ω ----
    bins = np.linspace(0, OMEGA_MAX, N_BINS + 1)
    centers = 0.5 * (bins[:-1] + bins[1:])

    time_in_bin = np.zeros(N_BINS)
    defects_in_bin = np.zeros(N_BINS)

    for O in omega_ts:
        idx = np.searchsorted(bins, O) - 1
        if 0 <= idx < N_BINS:
            time_in_bin[idx] += DT_SAMPLE

    for t in defect_times:
        j = np.searchsorted(times, t) - 1
        if j < 0:
            continue
        O = omega_ts[j]
        idx = np.searchsorted(bins, O) - 1
        if 0 <= idx < N_BINS:
            defects_in_bin[idx] += 1

    rate = np.divide(
        defects_in_bin,
        time_in_bin,
        out=np.full_like(defects_in_bin, np.nan),
        where=time_in_bin > 0
    )

    valid = np.isfinite(rate) & (rate > 0)
    O = centers[valid]
    R = rate[valid]

    try:
        popt, _ = curve_fit(
            critical_model,
            O, R,
            bounds=([0, max(O), 0], [np.inf, 2*max(O), 5]),
            maxfev=20000
        )
        C, Oc, nu = popt
    except RuntimeError:
        Oc, nu = np.nan, np.nan

    results.append({
        "run_index": i,
        "Omega_c": float(Oc),
        "nu": float(nu),
        "n_defects": len(defects)
    })

# ---- save ----
with open("analysis/omega_c_by_variant.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nΩc extraction complete:")
for r in results:
    print(r)