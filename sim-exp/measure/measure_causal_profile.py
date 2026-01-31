# analysis/measure_causal_profile.py

import json
import numpy as np

DT_BIN = 25  # rewrite steps

def main():
    with open("analysis/signal_speed_samples.json") as f:
        samples = json.load(f)

    # samples: [{"dt": ..., "influence": 0/1}, ...]

    dts = np.array([s["dt"] for s in samples])
    infl = np.array([s["influence"] for s in samples])

    max_dt = dts.max()
    bins = np.arange(0, max_dt + DT_BIN, DT_BIN)

    print("\n=== Causal Influence Profile ===")
    print("Δt_bin_center | P(influence) | count")

    for i in range(len(bins) - 1):
        mask = (dts >= bins[i]) & (dts < bins[i+1])
        if mask.sum() < 5:
            continue

        p = infl[mask].mean()
        center = 0.5 * (bins[i] + bins[i+1])
        print(f"{center:12.1f} | {p:13.3f} | {mask.sum():5d}")

if __name__ == "__main__":
    main()