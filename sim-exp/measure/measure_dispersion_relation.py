import json
import numpy as np
from scipy.stats import linregress

def main():
    # --- Load defect momentum data ---
    with open("analysis/defect_momentum_timeseries.json") as f:
        defects = json.load(f)

    # sort defects by time
    defects = sorted(defects, key=lambda d: d["time"])

    speeds = []
    energies = []

    for i in range(1, len(defects)):
        t1 = defects[i-1]["time"]
        t2 = defects[i]["time"]
        dt = t2 - t1

        if dt <= 0:
            continue

        # causal distance proxy
        dL = 1.0  # one causal hop (minimal influence step)

        v_eff = dL / dt
        E_eff = defects[i]["var_p"]  # momentum variance ~ energy proxy

        if E_eff <= 0:
            continue

        speeds.append(v_eff)
        energies.append(E_eff)

    speeds = np.array(speeds)
    energies = np.array(energies)

    if len(speeds) < 10:
        print("Not enough causal samples for dispersion analysis.")
        return

    # --- Fit power law: v ~ E^{-β} ---
    logv = np.log(speeds)
    logE = np.log(energies)

    slope, intercept, r, pval, stderr = linregress(logE, logv)
    beta = -slope

    print("\n=== Dispersion Relation (Causal Cones, Option A) ===")
    print(f"Samples: {len(speeds)}")
    print(f"β exponent ≈ {beta:.3f}")
    print(f"Correlation r = {r:.3f}")

if __name__ == "__main__":
    main()