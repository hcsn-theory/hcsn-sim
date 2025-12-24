# analysis/classify_particle_species.py

import json
import numpy as np

def classify(lifetime, var_p, omega):
    if lifetime > 100 and var_p < 0.1:
        return "STABLE"
    elif lifetime > 20:
        return "RESONANCE"
    else:
        return "VIRTUAL"

def main():
    # load particle tracks
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    # load defect momentum stats
    with open("analysis/defect_momentum_timeseries.json") as f:
        defect_momentum = json.load(f)

    # build lookup: time -> (mean_p, var_p)
    momentum_by_time = {
        d["time"]: d
        for d in defect_momentum
    }

    species = {}

    for p in particles:
        times = p["times"]
        omegas = p["omegas"]

        if len(times) < 1:
            continue

        # particle lifetime
        lifetime = max(times) - min(times)

        # aggregate momentum variance across defects
        vars_p = []
        for t in times:
            if t in momentum_by_time:
                vars_p.append(momentum_by_time[t]["var_p"])

        if len(vars_p) == 0:
            continue

        var_p = float(np.mean(vars_p))
        omega = float(np.mean(omegas))

        s = classify(lifetime, var_p, omega)
        species.setdefault(s, []).append(
            {
                "particle_id": p["particle_id"],
                "lifetime": lifetime,
                "var_p": var_p,
                "omega": omega,
            }
        )

    print("\n=== Particle Species Classification (HCSN) ===")
    for s, group in species.items():
        print(f"\n{s}:")
        print(f"  Count: {len(group)}")
        print(f"  Mean lifetime: {np.mean([g['lifetime'] for g in group]):.2f}")
        print(f"  Mean Var(p): {np.mean([g['var_p'] for g in group]):.3f}")
        print(f"  Mean Ω: {np.mean([g['omega'] for g in group]):.3f}")

if __name__ == "__main__":
    main()