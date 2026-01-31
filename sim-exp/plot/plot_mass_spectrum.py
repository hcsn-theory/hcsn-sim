# analysis/plot_mass_spectrum.py

import json
import numpy as np
import matplotlib.pyplot as plt

def main():
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    with open("analysis/defect_momentum_timeseries.json") as f:
        defect_stats = json.load(f)

    # build lookup: time -> var_p
    var_p_by_time = {
        d["time"]: d["var_p"]
        for d in defect_stats
        if d["var_p"] > 0
    }

    masses = []

    for p in particles:
        vars_p = []
        for t in p["times"]:
            if t in var_p_by_time:
                vars_p.append(var_p_by_time[t])

        if not vars_p:
            continue

        mean_var = np.mean(vars_p)
        mass = 1.0 / mean_var
        masses.append(mass)

    if not masses:
        print("No masses to plot.")
        return

    plt.figure(figsize=(6, 4))
    plt.hist(masses, bins="auto", alpha=0.8)
    plt.xlabel("Emergent mass  m = 1 / Var(p)")
    plt.ylabel("Count")
    plt.title("HCSN Particle Mass Spectrum")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()