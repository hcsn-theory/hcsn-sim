# analysis/sweep_uncertainty_exponent.py

import json
import numpy as np
import subprocess
import itertools
from pathlib import Path

from analysis.defects import momentum_timeseries

# -----------------------------
# Sweep configuration
# -----------------------------
GAMMA_TIME  = [0.05, 0.1, 0.2]
GAMMA_HIER  = [0.03, 0.06, 0.12]
GAMMA_EXT   = [0.02, 0.05, 0.1]

STEPS = 1200
WINDOW = 20
STEP = 5

OUTPUT_FILE = "analysis/uncertainty_sweep_results.json"

# -----------------------------
# Helper: extract alpha
# -----------------------------
def fit_uncertainty_exponent(defects):
    lifetimes = []
    variances = []

    for d in defects:
        ts, ps = momentum_timeseries(
            defects=defects,
            defect=d,
            window=WINDOW,
            step=STEP
        )

        if len(ps) < 5:
            continue

        lifetime = ts[-1] - ts[0]
        var_p = np.var(ps)

        if lifetime > 0 and var_p > 0:
            lifetimes.append(lifetime)
            variances.append(var_p)

    if len(lifetimes) < 5:
        return None, None

    log_tau = np.log(lifetimes)
    log_var = np.log(variances)

    alpha, intercept = np.polyfit(log_tau, log_var, 1)
    return -alpha, np.std(log_var + alpha * log_tau)

# -----------------------------
# Main sweep
# -----------------------------
def main():
    results = []

    param_grid = list(itertools.product(
        GAMMA_TIME, GAMMA_HIER, GAMMA_EXT
    ))

    for i, (gt, gh, ge) in enumerate(param_grid):
        print(f"\n=== Sweep {i+1}/{len(param_grid)} ===")
        print(f"gamma_time={gt}, gamma_hier={gh}, gamma_ext={ge}")

        # Run simulation with env override
        subprocess.run([
            "python3",
            "run_simulation.py",
            str(STEPS),
            str(gt),
            str(gh),
            str(ge)
        ], check=True)

        # Load latest run
        with open("timeseries.json") as f:
            data = json.load(f)

        run = data["runs"][-1]
        defects = run.get("defects", [])

        if len(defects) < 5:
            print("Not enough defects — skipping")
            continue

        alpha, scatter = fit_uncertainty_exponent(defects)

        if alpha is None:
            print("Fit failed — skipping")
            continue

        result = {
            "gamma_time": gt,
            "gamma_hier": gh,
            "gamma_ext": ge,
            "alpha": round(alpha, 3),
            "scatter": round(scatter, 3),
            "num_defects": len(defects)
        }

        print("α =", result["alpha"])
        results.append(result)

        # incremental save (important)
        Path("analysis").mkdir(exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)

    print("\n=== Sweep complete ===")
    print(f"Saved {len(results)} results to {OUTPUT_FILE}")

# -----------------------------
if __name__ == "__main__":
    main()