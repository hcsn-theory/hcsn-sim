# analysis/compute_defect_momentum_timeseries.py

import json
import numpy as np
from analysis.defects import momentum_timeseries

WINDOW = 20
STEP = 5
OUTFILE = "analysis/defect_momentum_timeseries.json"

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    runs = data["runs"]
    run = runs[-1]

    defects = run.get("defects", [])
    if len(defects) < 2:
        print("Not enough defects for momentum time series.")
        return

    print("\n=== Defect Momentum Time Series ===")

    results = []

    for i, d in enumerate(defects):
        ts, ps = momentum_timeseries(
            defects=defects,
            defect=d,
            window=WINDOW,
            step=STEP
        )

        if len(ps) < 2:
            continue

        mean_p = float(np.mean(ps))
        var_p  = float(np.var(ps))

        print(f"\nDefect {i} at t={d['time']}")
        print(f"  samples: {len(ps)}")
        print(f"  mean p: {mean_p:.3f}")
        print(f"  var(p): {var_p:.3f}")

        results.append({
            "time": d["time"],
            "samples": len(ps),
            "mean_p": mean_p,
            "var_p": var_p
        })

    with open(OUTFILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved momentum time series to {OUTFILE}")

if __name__ == "__main__":
    main()