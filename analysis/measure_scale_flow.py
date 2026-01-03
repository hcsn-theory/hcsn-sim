import json
import numpy as np
from scipy.stats import linregress

# different coarse-graining scales (rewrite steps)
SCALES = [1, 2, 5, 10, 20, 50]

def coarse_grain_times(times, s):
    return [t // s for t in times]

def main():
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    with open("analysis/defect_momentum_timeseries.json") as f:
        momentum = json.load(f)

    varp_at_time = {d["time"]: d["var_p"] for d in momentum}

    print("\n=== Scale Flow Analysis (HCSN) ===")
    print("Scale | Samples | β exponent | corr")

    for s in SCALES:
        speeds = []
        varps = []

        for p in particles:
            times = coarse_grain_times(p["times"], s)

            if len(times) < 2:
                continue

            tau = max(times) - min(times)
            if tau <= 0:
                continue

            v_eff = 1.0 / tau

            vp = [
                varp_at_time[t * s]
                for t in times
                if (t * s) in varp_at_time
            ]

            if not vp:
                continue

            speeds.append(v_eff)
            varps.append(np.mean(vp))

        if len(speeds) < 3:
            continue

        speeds = np.array(speeds)
        varps = np.array(varps)

        logv = np.log(speeds)
        logp = np.log(varps)

        slope, _, r, _, _ = linregress(logp, logv)
        beta = -slope

        print(f"{s:5d} | {len(speeds):7d} | {beta:9.3f} | {r:5.3f}")

if __name__ == "__main__":
    main()